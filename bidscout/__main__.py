"""Bid Scout CLI.

  python -m bidscout score-niches [--sam]        rank candidate NAICS niches
  python -m bidscout ingest --naics 541512       pull recent opportunities (SAM key)
  python -m bidscout match [--fixtures]          match opportunities to subscribers
  python -m bidscout packets [--fixtures]        emit brief packets for the skill layer
  python -m bidscout prospects --naics 541512 [--state VA]
  python -m bidscout filter-prospects --naics 541512   score prospects for outreach
  python -m bidscout enrich-prospects --naics 541512   UEI/registration from SAM (metered)
  python -m bidscout sample --firm "X LLC" --notice <id> --reason "<public fact>"
  python -m bidscout render                      briefs (md) -> state/pages/ (html)
  python -m bidscout verify-codes [--naics X]    probe each set-aside code for zeros
  python -m bidscout budget                      show today's SAM request budget
  python -m bidscout selftest                    offline end-to-end check on fixtures

State lives in ./state (BIDSCOUT_STATE to override). Fixtures let every stage
run with zero network so the scheduled routine can be rehearsed anywhere.
"""

import argparse
import json
import sys
from pathlib import Path

from . import config
from .brief_packet import build_packet
from .http import sam_budget_remaining
from .matcher import Subscriber, match_all
from .sam_client import fetch_opportunities, normalize_opportunity


def _load_subscribers(path: Path) -> list[dict]:
    subs = config.load_json(path)
    if not isinstance(subs, list):
        raise SystemExit(f"{path} must be a JSON array of subscriber objects")
    return subs


def _load_opportunities(fixtures: bool) -> list[dict]:
    src = (config.FIXTURES_DIR / "sam_opportunities.json" if fixtures
           else config.ensure_state_dir() / "opportunities.json")
    if not src.exists():
        raise SystemExit(f"No opportunities at {src}. Run `ingest` first "
                         "(or pass --fixtures).")
    return [normalize_opportunity(o) if "noticeId" in o else o
            for o in config.load_json(src)]


def cmd_score_niches(args) -> int:
    from .niche_scorer import render_table, score_all
    rows = score_all(use_sam=args.sam)
    out = config.ensure_state_dir() / "niche_scores.json"
    config.save_json(out, rows)
    print(render_table(rows))
    print(f"\nSaved: {out}")
    return 0


def cmd_ingest(args) -> int:
    opps = [normalize_opportunity(o)
            for o in fetch_opportunities(args.naics, days_back=args.days)]
    out = config.ensure_state_dir() / "opportunities.json"
    config.save_json(out, opps)
    print(f"{len(opps)} opportunities (NAICS {args.naics}, {args.days}d) -> {out}")
    print(f"SAM budget remaining today: {sam_budget_remaining()}")
    return 0


def cmd_match(args) -> int:
    subs_raw = _load_subscribers(Path(args.subscribers))
    subs = [Subscriber.from_dict(s) for s in subs_raw]
    opps = _load_opportunities(args.fixtures)
    results = match_all(subs, opps)
    out = config.ensure_state_dir() / "matches.json"
    config.save_json(out, results)
    for sid, rows in results.items():
        print(f"{sid}: {len(rows)} matches"
              + (f" (top: {rows[0]['opportunity']['title'][:60]})" if rows else ""))
    print(f"Saved: {out}")
    return 0


def cmd_packets(args) -> int:
    subs = {s["id"]: s for s in _load_subscribers(Path(args.subscribers))}
    matches_path = config.ensure_state_dir() / "matches.json"
    if not matches_path.exists():
        raise SystemExit("No matches.json — run `match` first.")
    matches = config.load_json(matches_path)
    out_dir = config.ensure_state_dir() / "packets"
    n = 0
    for sid, rows in matches.items():
        for i, row in enumerate(rows[:args.max_per_subscriber]):
            packet = build_packet(subs[sid], row,
                                  with_awards=not args.fixtures)
            path = out_dir / f"{sid}-{i+1:02d}.json"
            config.save_json(path, packet)
            n += 1
    print(f"{n} brief packets -> {out_dir}")
    print("Next: run the bid-brief-writer skill over each packet, then "
          "brief-qc, then founder review, then delivery.")
    return 0


def cmd_prospects(args) -> int:
    from .usaspending_client import small_business_awardees
    rows = small_business_awardees(args.naics, state=args.state)
    out = config.ensure_state_dir() / f"prospects-{args.naics}.json"
    config.save_json(out, rows)
    print(f"{len(rows)} distinct small-business awardees -> {out}")
    print("Contact emails: look up each firm's public POC on sam.gov entity "
          "search (or Entity API with your key). Exclude opted-out entities.")
    return 0


def cmd_filter_prospects(args) -> int:
    """Score the raw awardee list for outreach fitness (keyless).

    The raw list is every firm USAspending reports as a small-business awardee.
    That is not a buyer list: 541519 is a catch-all NAICS and the small-business
    flag is per-award self-certification. See bidscout/prospect_filter.py for
    the rule set and its measurement limits.
    """
    from .prospect_filter import filter_prospects
    state = config.ensure_state_dir()

    prospects_path = state / f"prospects-{args.naics}.json"
    if not prospects_path.exists():
        raise SystemExit(f"No {prospects_path} — run `prospects --naics "
                         f"{args.naics}` first.")
    prospects = config.load_json(prospects_path)

    # Award descriptions live on the scan rows, not on the aggregated prospect
    # records, so the scan is cached alongside them and reused when present.
    scan_path = state / f"prospect_scan-{args.naics}.json"
    if args.rescan or not scan_path.exists():
        from .usaspending_client import sb_award_scan
        scan = sb_award_scan(args.naics, state=args.state,
                             months_back=args.months, pages=args.pages)
        config.save_json(scan_path, scan)
    else:
        scan = config.load_json(scan_path)
    rows = scan.get("rows", [])

    supp_path = state / "suppression.json"
    if not supp_path.exists():
        raise SystemExit("state/suppression.json missing — refusing to build an "
                         "outreach list without the opt-out record.")
    suppression = config.load_json(supp_path)

    result = filter_prospects(prospects, rows, suppression)
    result["naics"] = args.naics
    result["source"] = {
        "prospects": str(prospects_path),
        "scan_rows": len(rows),
        "scan_capped": scan.get("scan_capped"),
    }
    out = state / f"prospects-{args.naics}-filtered.json"
    config.save_json(out, result)

    s = result["summary"]
    print(f"{s['input']} prospects -> {s['kept']} kept / {s['excluded']} excluded")
    for rule, n in s["excluded_by_rule"].items():
        print(f"   {n:>4}  {rule}")
    print(f"   {s['flagged_kept']} kept firm(s) carry flags for founder review")
    if scan.get("scan_capped"):
        print("   NOTE: the award scan was page-capped — totals understate every "
              "firm and the list is not exhaustive.")
    print(f"\nTop {min(10, len(result['kept']))} by fitness score:")
    for k in result["kept"][:10]:
        print(f"   {k['fitness_score']:>3}  {k['awards']:>3} awd  "
              f"${k['total_amount']:>12,.0f}  {k['recipient']}")
    print(f"\nSaved: {out}")
    print("Every excluded firm carries the rule, the matched token and the "
          "evidence text — audit before mailing.")
    return 0


def cmd_enrich_prospects(args) -> int:
    """Attach SAM.gov entity data to the filtered prospects (1 request per firm).

    Keyed by UEI, never by legal name. A name search returns several
    registrations for most firms and picking one is guesswork -- on 2026-09-03 it
    resolved to the wrong company for 3 of 8 firms tried, one of them a namesake
    whose registration lapsed in 2018. Firms whose UEI is unknown are skipped
    rather than guessed at.
    """
    from .sam_entity import enrich_batch, is_biddable
    state = config.ensure_state_dir()

    filtered = state / f"prospects-{args.naics}-filtered.json"
    if not filtered.exists():
        raise SystemExit(f"No {filtered} — run `filter-prospects --naics "
                         f"{args.naics}` first.")
    kept = config.load_json(filtered)["kept"]
    if args.limit:
        kept = kept[:args.limit]
    firms = {k["recipient"]: k.get("uei", "") for k in kept}

    out = state / f"entities-{args.naics}.json"
    existing = config.load_json(out) if out.exists() else {}
    result = enrich_batch(firms, existing=existing)
    config.save_json(out, result["entities"])

    drops, unknown, ok = [], [], 0
    for firm, ent in result["entities"].items():
        verdict, why = is_biddable(ent)
        if verdict is True:
            ok += 1
        elif verdict is False:
            drops.append((firm, why))
        else:
            unknown.append(firm)

    print(f"{result['looked_up']} looked up this run "
          f"({sam_budget_remaining()} SAM requests left today)")
    print(f"   {ok} verified biddable, {len(drops)} DROP, {len(unknown)} unknown")
    if result["skipped_no_uei"]:
        print(f"   {len(result['skipped_no_uei'])} skipped — no UEI known, and a "
              f"name lookup cannot be trusted")
    for firm, why in drops:
        print(f"   DROP {firm}: {why}")
    if result["budget_exhausted"]:
        print("   Budget exhausted mid-run. Everything already paid for is saved; "
              "re-run tomorrow to continue.")
    print(f"\nSaved: {out}")
    print("POC EMAIL is not returned by the Entity API (SAM keeps it behind the "
          "FOUO tier). Open https://sam.gov/entity/<UEI>/coreData to read it.")
    return 0


def cmd_sample(args) -> int:
    from .brief_packet import build_sample_packet
    opps = _load_opportunities(args.fixtures)
    opp = next((o for o in opps if o["notice_id"] == args.notice), None)
    if opp is None:
        raise SystemExit(f"Notice {args.notice} not in the latest ingest "
                         f"({len(opps)} opportunities loaded).")
    packet = build_sample_packet(args.firm, opp, args.reason,
                                 with_awards=not args.fixtures)
    out = config.ensure_state_dir() / "packets" / f"{packet['subscriber']['id']}.json"
    config.save_json(out, packet)
    print(f"Sample packet for {args.firm} -> {out}")
    print("Next: bid-brief-writer skill renders it; outreach-drafter attaches it.")
    return 0


def cmd_render(_args) -> int:
    from .render import render_all
    pages = render_all()
    for p in pages:
        print(p)
    print(f"{len(pages)} brief pages rendered to state/pages/ "
          "(deploy alongside site/ or attach to delivery emails).")
    return 0


def cmd_verify_codes(args) -> int:
    from .usaspending_client import SB_SET_ASIDE_CODES, probe_set_aside_codes
    scope = f"NAICS {args.naics}" if args.naics else "government-wide"
    print(f"Probing {len(SB_SET_ASIDE_CODES)} set-aside codes, {scope}, "
          f"{args.months} months (keyless):\n")
    rows = probe_set_aside_codes(SB_SET_ASIDE_CODES, naics=args.naics,
                                 months_back=args.months)
    dead = []
    for r in rows:
        if r["error"]:
            print(f"  {r['code']:10} ERROR {r['error'][:60]}")
            continue
        flag = "  <-- ZERO" if r["awards"] == 0 else ""
        print(f"  {r['code']:10} {r['awards']:>9,}{flag}")
        if r["awards"] == 0:
            dead.append(r["code"])
    out = config.ensure_state_dir() / "set_aside_code_probe.json"
    config.save_json(out, {"scope": scope, "months": args.months, "rows": rows,
                           "zero_codes": dead})
    print(f"\nSaved: {out}")
    if dead:
        print(f"\n{len(dead)} code(s) matched ZERO awards {scope}: "
              f"{', '.join(dead)}")
        print("Government-wide zeros are indistinguishable from invalid codes. "
              "Remove them from SB_SET_ASIDE_CODES or document why they stay — "
              "an inert code in a scoring filter is a silent miscount.")
    else:
        print("\nEvery code matches real awards; the list is live.")
    return 0


def cmd_budget(_args) -> int:
    print(f"SAM.gov requests remaining today: {sam_budget_remaining()} "
          f"(daily budget {config.SAM_DAILY_BUDGET})")
    return 0


def cmd_selftest(_args) -> int:
    from .selftest import run
    return run()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="bidscout", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("score-niches"); s.add_argument("--sam", action="store_true")
    s.set_defaults(fn=cmd_score_niches)

    s = sub.add_parser("ingest")
    s.add_argument("--naics", required=True); s.add_argument("--days", type=int, default=7)
    s.set_defaults(fn=cmd_ingest)

    s = sub.add_parser("match")
    s.add_argument("--subscribers", default="subscribers/subscribers.json")
    s.add_argument("--fixtures", action="store_true")
    s.set_defaults(fn=cmd_match)

    s = sub.add_parser("packets")
    s.add_argument("--subscribers", default="subscribers/subscribers.json")
    s.add_argument("--max-per-subscriber", type=int, default=8)
    s.add_argument("--fixtures", action="store_true")
    s.set_defaults(fn=cmd_packets)

    s = sub.add_parser("prospects")
    s.add_argument("--naics", required=True); s.add_argument("--state", default=None)
    s.set_defaults(fn=cmd_prospects)

    s = sub.add_parser("filter-prospects")
    s.add_argument("--naics", required=True)
    s.add_argument("--state", default=None)
    s.add_argument("--months", type=int, default=24)
    s.add_argument("--pages", type=int, default=5)
    s.add_argument("--rescan", action="store_true",
                   help="refetch award rows (keyless) instead of reusing the cached scan")
    s.set_defaults(fn=cmd_filter_prospects)

    s = sub.add_parser("enrich-prospects")
    s.add_argument("--naics", required=True)
    s.add_argument("--limit", type=int, default=None,
                   help="only the top N kept prospects (each costs 1 SAM request)")
    s.set_defaults(fn=cmd_enrich_prospects)

    s = sub.add_parser("sample")
    s.add_argument("--firm", required=True)
    s.add_argument("--notice", required=True, help="notice_id from the latest ingest")
    s.add_argument("--reason", required=True,
                   help="public-fact hook, e.g. 'Your firm's award <id> with <agency>'")
    s.add_argument("--fixtures", action="store_true")
    s.set_defaults(fn=cmd_sample)

    s = sub.add_parser("render"); s.set_defaults(fn=cmd_render)

    s = sub.add_parser("verify-codes")
    s.add_argument("--naics", default=None,
                   help="restrict the probe to one NAICS (default: government-wide)")
    s.add_argument("--months", type=int, default=24)
    s.set_defaults(fn=cmd_verify_codes)

    s = sub.add_parser("budget"); s.set_defaults(fn=cmd_budget)
    s = sub.add_parser("selftest"); s.set_defaults(fn=cmd_selftest)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
