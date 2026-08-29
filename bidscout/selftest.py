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

    # Niche scorer. Regression guard for BOTH 2026-08-29 failures: the
    # all-tied-at-91.0 saturation and the follow-on "one live term, three dead
    # ones" version. This drives score_niche itself with the real probed
    # population counts, so a scorer that stops discriminating fails here
    # instead of in front of the founder.
    from . import niche_scorer as ns
    if not (ns._price_band_fit(500_000) == 1.0
            and ns._price_band_fit(300_000_000) < 0.05001
            and ns._price_band_fit(0) == 0.0
            and ns._price_band_fit(10_000) >= 0.4):
        failures.append("_price_band_fit: band, decay, or floor wrong")

    # Real 24-month probes (2026-08-29): (total, set_aside-ish, notices, median)
    real = {
        "541511": (9455, 6383, 74, 180_000.0),
        "541512": (21752, 7265, 51, 640_000.0),
        "541330": (41436, 20330, 33, 95_000.0),
        "561612": (9292, 2037, 12, 2_400_000.0),
    }
    saved = (ns.award_count, ns.sb_award_scan, ns.config.SAM_API_KEY)
    try:
        ns.award_count = (lambda n, months_back=24, set_aside_codes=None, **kw:
                          real[n][1] if set_aside_codes else real[n][0])
        ns.sb_award_scan = lambda n, **kw: {
            "rows": [{"amount": real[n][3]}] * 400,
            "prospects": [{"recipient": f"F{i}"} for i in range(200)],
            "rows_scanned": 400, "scan_capped": False}
        ns.config.SAM_API_KEY = ""  # exercise the renormalize path
        scored = [ns.score_niche(n, n, use_sam=False) for n in real]
    finally:
        ns.award_count, ns.sb_award_scan, ns.config.SAM_API_KEY = saved

    for term in ("set_aside", "price_band"):
        if len({r["terms"][term] for r in scored}) == 1:
            failures.append(f"score_niche: '{term}' scored identically across "
                            f"four real niches — the term is saturated and "
                            f"contributes nothing to the ranking")
    if len({r["composite"] for r in scored}) < len(scored):
        failures.append("score_niche: real-world counts produced duplicate "
                        "composites")
    if abs(sum(scored[0]["terms"].values()) - scored[0]["composite"]) > 0.2:
        failures.append("score_niche: renormalized terms do not sum to composite")
    if not all(0 <= r["composite"] <= 100.01 for r in scored):
        failures.append("score_niche: composite outside 0-100 after "
                        "renormalization")

    out = ns.render_table(scored)
    if "SHORTLIST" not in out:
        failures.append("render_table: must emit a two-niche shortlist")
    dead = [dict(r, terms=dict(r["terms"], set_aside=35.0)) for r in scored]
    if "DEAD TERM: set_aside" not in ns.render_table(dead):
        failures.append("render_table: must name a term that stops discriminating")

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
