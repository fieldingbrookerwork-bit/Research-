"""Niche scorer — the day-1 decision tool.

The question: in which NAICS should Bid Scout sell $49-79/mo research briefs to
small government contractors?

SCORED TERMS (each one demonstrably varies in live data — that is the bar for
inclusion; a term that cannot discriminate is padding that hides which signal
is actually driving the ranking):
  set_aside_share  40  Share of NEW awards made under a small-business
                       set-aside. An attribute of the SOLICITATION, not of
                       whoever won: set-aside work is where a small firm
                       competes against peers rather than a large prime, which
                       is exactly the bid a $59/mo brief can change.
  notice_flow      40  SAM.gov notices posted in the last 30 days — the only
                       direct measure of how much biddable work appears weekly,
                       and therefore whether a weekly product has anything to
                       put in it. Needs a SAM key; without one the term is
                       dropped, remaining weights renormalize, and the output
                       says so.
  sb_win_share     20  Share of new awards won by small businesses by any
                       route. Cross-checks set-aside share: a niche can have few
                       set-asides yet still be won by small firms on full-and-
                       open (a harder sell, but real).

GATES (pass/fail, never scored — see the design note):
  median new small-business award inside $10k-$1.5M ... buyer fit. A firm whose
    median award is $3M has a capture manager and already pays for GovWin-class
    tooling; it is not a $59/mo buyer.
  at least MIN_SB_AWARDS small-business awards in 24 months ... enough activity.

Design notes — three scorer failures on 2026-08-29, each encoded here so it
cannot recur silently:
  1. Counting rows of an amount-sorted, capped page: every term saturated and
     seven of eight niches tied at exactly 91.0.
  2. Population counts, but caps set below the real data (flow cap 8,000 vs
     9k-41k actual): three of four terms constant — a one-variable ranking in a
     four-variable costume.
  3. Live run showed price_band spanning 0.0 points (every service NAICS median
     sits inside any sane band) and repeat_bidders spanning 2.4 of 15, its value
     tracking the scan cap rather than the market. Both are now gates or gone.
The general lesson: DISTINCT-FIRM COUNTS FROM A CAPPED SCAN MEASURE THE SAMPLE,
NOT THE MARKET. Anything derived from the scan is reported as a floor and never
scored. render_table names any term that stops discriminating.
"""

import statistics

from . import config
from .usaspending_client import SB_SET_ASIDE_CODES, award_count, sb_award_scan

W_SET_ASIDE = 40
W_NOTICE_FLOW = 40
W_SB_WIN = 20

# A niche needs ~15 notices/week to fill an issue; under ~5/week it cannot.
NOTICE_FULL, NOTICE_FLOOR = 60, 20
BUYER_MIN, BUYER_MAX = 10_000, 1_500_000
MIN_SB_AWARDS = 500
SCAN_PAGES = 5


def score_niche(naics: str, label: str, use_sam: bool = True) -> dict:
    warnings: list[str] = []

    total = award_count(naics, months_back=24)
    set_aside = award_count(naics, months_back=24,
                            set_aside_codes=SB_SET_ASIDE_CODES)
    sb_total = award_count(naics, months_back=24, small_business_only=True)

    # set_aside_type_codes and recipient_type_names are unvalidated free text:
    # a bad value returns 200 with a wrong count rather than an error. These are
    # the tripwires for that failure mode.
    if total and set_aside > total:
        warnings.append(f"set-aside count ({set_aside}) exceeds total ({total}) "
                        "— check SB_SET_ASIDE_CODES against USAspending source")
    if total and sb_total > total:
        warnings.append(f"small-business count ({sb_total}) exceeds total "
                        f"({total}) — check the recipient_type_names filter")
    set_aside_share = min(set_aside / total, 1.0) if total else 0.0
    sb_win_share = min(sb_total / total, 1.0) if total else 0.0

    scan = sb_award_scan(naics, months_back=24, pages=SCAN_PAGES)
    amounts = [r["amount"] for r in scan["rows"] if (r["amount"] or 0) > 0]
    median_award = statistics.median(amounts) if amounts else 0.0
    prospects = scan["prospects"]
    if not prospects:
        warnings.append("no small-business awardees returned — median and gates "
                        "are unevidenced for this niche")

    notices_30d, notice_error = None, None
    if use_sam and config.SAM_API_KEY:
        from .sam_client import count_opportunities
        try:
            notices_30d = count_opportunities(naics, days_back=30)
        except Exception as e:
            notice_error = f"{type(e).__name__}: {e}"
            warnings.append(f"SAM notice count unavailable ({notice_error}); "
                            "flow term dropped and weights renormalized")
    elif use_sam:
        warnings.append("SAM_API_KEY not set; flow term dropped and weights "
                        "renormalized — set the key for a decision-grade score")

    terms = {"set_aside": set_aside_share * W_SET_ASIDE,
             "sb_win": sb_win_share * W_SB_WIN}
    weights = {"set_aside": W_SET_ASIDE, "sb_win": W_SB_WIN}
    if notices_30d is not None:
        flow = min(max(notices_30d - NOTICE_FLOOR, 0)
                   / (NOTICE_FULL - NOTICE_FLOOR), 1.0)
        terms["notice_flow"] = flow * W_NOTICE_FLOW
        weights["notice_flow"] = W_NOTICE_FLOW

    scale = 100 / sum(weights.values())
    terms = {k: round(v * scale, 1) for k, v in terms.items()}
    composite = round(sum(terms.values()), 1)

    gates = {
        "buyer_size": ("pass" if BUYER_MIN <= median_award <= BUYER_MAX
                       else "FAIL"),
        "activity": "pass" if sb_total >= MIN_SB_AWARDS else "FAIL",
    }

    return {
        "naics": naics,
        "label": label,
        "new_awards_24mo": total,
        "set_aside_awards_24mo": set_aside,
        "set_aside_share": round(set_aside_share, 3),
        "sb_awards_24mo": sb_total,
        "sb_win_share": round(sb_win_share, 3),
        "median_sb_award": median_award,
        "sample_size": len(amounts),
        # Reported, never scored: bounded by the scan, not the market.
        "distinct_firms_in_sample": len(prospects),
        "scan_capped": scan["scan_capped"],
        "notices_30d": notices_30d,
        "gates": gates,
        "gates_pass": all(v == "pass" for v in gates.values()),
        "terms": terms,
        "term_weights_used": weights,
        "warnings": warnings,
        "composite": composite,
    }


def score_all(use_sam: bool = True) -> list[dict]:
    rows = []
    for naics, label in config.CANDIDATE_NICHES.items():
        try:
            rows.append(score_niche(naics, label, use_sam=use_sam))
        except Exception as e:
            rows.append({"naics": naics, "label": label,
                         "error": f"{type(e).__name__}: {e}"})
    rows.sort(key=lambda r: -(r.get("composite") or -1))
    return rows


def render_table(rows: list[dict]) -> str:
    head = (f"{'NAICS':7} {'score':>5} {'SetAsd%':>7} {'SBwin%':>6} "
            f"{'notices':>7} {'med $':>10} {'gates':>5}  label")
    lines = [head, "-" * len(head)]
    for r in rows:
        if "error" in r:
            lines.append(f"{r['naics']:7} ERROR   {r['error'][:60]}")
            continue
        lines.append(
            f"{r['naics']:7} {r['composite']:>5} {r['set_aside_share']*100:>6.0f}% "
            f"{r['sb_win_share']*100:>5.0f}% "
            f"{str(r['notices_30d'] if r['notices_30d'] is not None else '-'):>7} "
            f"{r['median_sb_award']:>10,.0f} "
            f"{'pass' if r['gates_pass'] else 'FAIL':>5}  {r['label']}")

    scored = [r for r in rows if "composite" in r]
    lines.append("")
    if not scored:
        return "\n".join(lines + ["No niche scored successfully."])

    for term, weight in (("set_aside", W_SET_ASIDE),
                         ("notice_flow", W_NOTICE_FLOW),
                         ("sb_win", W_SB_WIN)):
        vals = [r["terms"][term] for r in scored if term in r["terms"]]
        if len(vals) >= 2 and max(vals) - min(vals) < 0.2 * weight:
            lines.append(f"DEAD TERM: {term} spans only "
                         f"{max(vals) - min(vals):.1f} pts — it is not "
                         "discriminating; the ranking does not depend on it.")
    for r in scored:
        if not r["gates_pass"]:
            failed = [k for k, v in r["gates"].items() if v != "pass"]
            lines.append(f"GATE FAIL {r['naics']}: {', '.join(failed)} "
                         f"(median ${r['median_sb_award']:,.0f}, "
                         f"{r['sb_awards_24mo']:,} SB awards)")
        for w in r.get("warnings", []):
            lines.append(f"WARN {r['naics']}: {w}")

    eligible = [r for r in scored
                if r["gates_pass"] and "control" not in r["label"].lower()]
    lines.append("")
    if len(eligible) >= 2:
        gap = eligible[0]["composite"] - eligible[1]["composite"]
        lines.append(f"SHORTLIST: {eligible[0]['naics']} "
                     f"({eligible[0]['composite']}) and {eligible[1]['naics']} "
                     f"({eligible[1]['composite']}), gap {gap:.1f}.")
        lines.append("Gap under 10 points → split the 150-send smoke test 75/75 "
                     "and let reply rate decide; reply rate from real sends "
                     "beats any composite this data can produce. Gap over 10 → "
                     "lead with the top one, keep the other as the month-2 "
                     "fallback.")
    elif len(eligible) == 1:
        lines.append(f"ONLY ONE NICHE CLEARS THE GATES: {eligible[0]['naics']}.")
    else:
        lines.append("NO NICHE CLEARS THE GATES — do not pick; investigate the "
                     "gate failures above first.")
    lines.append("Weights: set-aside 40, notice flow 40, SB win share 20 "
                 "(renormalized if a term is unavailable). Distinct-firm counts "
                 "are a sample floor and are never scored.")
    return "\n".join(lines)
