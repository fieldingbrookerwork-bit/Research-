"""Bid Scout CLI.

  python -m bidscout score-niches [--sam]        rank candidate NAICS niches
  python -m bidscout ingest --naics 541512       pull recent opportunities (SAM key)
  python -m bidscout match [--fixtures]          match opportunities to subscribers
  python -m bidscout packets [--fixtures]        emit brief packets for the skill layer
  python -m bidscout prospects --naics 541512 [--state VA]
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
