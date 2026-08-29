"""Offline end-to-end selftest on fixtures: normalize -> match -> packet.

This is what the scheduled routine's health check runs. It touches no network,
so a pass means the code path is sound and a production failure is environmental
(key, quota, connectivity) — exactly the triage split the runbook uses.
"""

from . import config
from .brief_packet import build_packet
from .matcher import Subscriber, match_all
from .sam_client import normalize_opportunity


def run() -> int:
    failures: list[str] = []

    raw = config.load_json(config.FIXTURES_DIR / "sam_opportunities.json")
    opps = [normalize_opportunity(o) for o in raw]
    if len(opps) < 3:
        failures.append(f"expected >=3 fixture opportunities, got {len(opps)}")
    for o in opps:
        if not o["notice_id"] or not o["sam_url"].startswith("https://sam.gov/"):
            failures.append(f"bad normalize: {o}")

    subs_raw = config.load_json(config.REPO_ROOT / "subscribers" / "subscribers.json")
    subs = [Subscriber.from_dict(s) for s in subs_raw]
    results = match_all(subs, opps)

    demo = results.get("demo-vasys", [])
    if not demo:
        failures.append("demo-vasys matched nothing; matcher or fixtures broken")
    else:
        top = demo[0]
        if top["score"] < 5:
            failures.append(f"top match score {top['score']} < 5")
        if not top["reasons"]:
            failures.append("top match has no reasons")
        if any("security guard" in r["opportunity"]["title"].lower() for r in demo):
            failures.append("keyword-excluded opportunity leaked through")

    wrong_sa = [r for r in results.get("demo-guards", [])
                if r["opportunity"]["set_aside"] == "SDVOSBC"]
    if wrong_sa:
        failures.append("set-aside gate failed: non-SDVOSB firm matched SDVOSBC notice")

    if demo:
        sub = next(s for s in subs_raw if s["id"] == "demo-vasys")
        packet = build_packet(sub, demo[0], with_awards=False)
        for key in ("opportunity", "match", "framing"):
            if key not in packet:
                failures.append(f"packet missing {key}")
        if "verify every detail" not in packet["framing"]["product_line"].lower():
            failures.append("packet framing lost the verify-before-bidding line")

    from .brief_packet import build_sample_packet
    sample = build_sample_packet("Example Firm, LLC", opps[0],
                                 "Your SAM registration under NAICS 541512 in VA",
                                 with_awards=False)
    if not sample.get("sample") or "framing" not in sample:
        failures.append("sample packet missing sample flag or framing")
    if not sample["match"]["cautions"]:
        failures.append("sample packet lost its outreach caution")

    # Niche scorer. Regression guard for all three 2026-08-29 failures: the
    # all-tied-at-91.0 saturation, the "one live term, three dead ones" version,
    # and the gate that measured sample yield instead of the market. Drives
    # score_niche itself with real probed population counts, so a scorer that
    # stops discriminating fails HERE rather than in front of the founder.
    from . import niche_scorer as ns

    # (total_new, set_aside, sb_won, notices_30d, median_sb_award)
    real = {
        "541519": (43608, 15263, 21804, 117, 59_998.0),
        "541330": (41436, 3315, 20330, 127, 159_268.0),
        "541512": (21752, 1305, 7265, 41, 185_071.0),
        "561612": (9292, 372, 2037, 9, 306_394.0),
    }
    import bidscout.sam_client as _sc
    saved = (ns.award_count, ns.sb_award_scan, ns.config.SAM_API_KEY)
    _saved_count = getattr(_sc, "count_opportunities", None)
    try:
        def _fake_count(n, months_back=24, set_aside_codes=None,
                        small_business_only=False, **kw):
            t, sa, sb, _, _ = real[n]
            if set_aside_codes:
                return sa
            return sb if small_business_only else t
        ns.award_count = _fake_count
        ns.sb_award_scan = lambda n, **kw: {
            "rows": [{"amount": real[n][4]}] * 400,
            "prospects": [{"recipient": f"F{i}"} for i in range(120)],
            "rows_scanned": 400, "scan_capped": True}
        ns.config.SAM_API_KEY = "test"
        _sc.count_opportunities = lambda n, days_back=30, **kw: real[n][3]
        scored = sorted([ns.score_niche(n, n) for n in real],
                        key=lambda r: -r["composite"])
    finally:
        ns.award_count, ns.sb_award_scan, ns.config.SAM_API_KEY = saved
        if _saved_count is not None:
            _sc.count_opportunities = _saved_count

    for term in ("set_aside", "notice_flow", "sb_win"):
        if len({r["terms"][term] for r in scored}) == 1:
            failures.append(f"score_niche: '{term}' scored identically across "
                            "four real niches — the term is saturated and "
                            "contributes nothing to the ranking")
    if len({r["composite"] for r in scored}) < len(scored):
        failures.append("score_niche: real counts produced duplicate composites")
    if not all(0 <= r["composite"] <= 100.01 for r in scored):
        failures.append("score_niche: composite outside 0-100")
    if abs(sum(scored[0]["terms"].values()) - scored[0]["composite"]) > 0.2:
        failures.append("score_niche: terms do not sum to composite")
    # A capped scan must never be scored, only reported.
    if any("distinct" in k and k in r.get("terms", {})
           for r in scored for k in r.get("terms", {})):
        failures.append("score_niche: scored a scan-bounded firm count")

    out = ns.render_table(scored)
    if "SHORTLIST" not in out:
        failures.append("render_table: must emit a two-niche shortlist")
    dead = [dict(r, terms=dict(r["terms"], set_aside=40.0)) for r in scored]
    if "DEAD TERM: set_aside" not in ns.render_table(dead):
        failures.append("render_table: must name a term that stops discriminating")
    # Buyer-size gate must reject a niche whose firms are too big to be buyers.
    big = ns.render_table([dict(scored[0], median_sb_award=9_000_000.0,
                                gates={"buyer_size": "FAIL", "activity": "pass"},
                                gates_pass=False)])
    if "GATE FAIL" not in big:
        failures.append("render_table: must report gate failures")

    from .render import markdown_to_html
    title, body = markdown_to_html(
        "# Test Brief\n\n> note\n\n## Section\n- **bold** and "
        "[link](https://sam.gov/opp/X/view)\n\n---\n*footer line*")
    if title != "Test Brief" or '<a href="https://sam.gov/opp/X/view">' not in body:
        failures.append("render: title or link lost")
    if "**" in body or "<script" in body.lower():
        failures.append("render: markdown leaked or unexpected markup")

    if failures:
        print("SELFTEST FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print(f"SELFTEST PASS — {len(opps)} fixture opportunities, "
          f"{sum(len(v) for v in results.values())} matches, packet OK")
    return 0
