"""Niche scorer — the day-1 decision tool.

The question it answers: in which NAICS should Bid Scout sell $49-79/mo
research briefs to small government contractors?

Terms (each measured, each able to vary — see the design note):
  set_aside_share  35  Share of NEW awards made under small-business set-asides.
                       An attribute of the SOLICITATION, not of whoever won:
                       set-aside work is where a small firm competes against
                       peers rather than against a large prime, which is exactly
                       the bid a $59/mo brief can change.
  notice_flow      30  SAM.gov notices posted in the last 30 days. The only
                       direct measure of how much biddable work appears weekly.
                       Requires a SAM key; without one the term is dropped and
                       the remaining weights are renormalized (stated in output).
  price_band       20  Median new small-business award inside $25k-$1.5M. This
                       is BUYER fit, not capability fit: a firm whose median
                       award is $3M has a capture manager and already pays for
                       GovWin-class tooling.
  repeat_bidders   15  HYPOTHESIS TERM, higher = better. Awards-per-firm in the
                       recent sample, as an inverse-concentration proxy: a niche
                       where relatively few firms take the work is a niche full
                       of firms that bid and lose every quarter — the buyer.
                       Flagged as a hypothesis because no free federal dataset
                       proves the sign; revisit once offers-received data is in.

Gate (not scored): at least GATE_MIN_PROSPECTS distinct small-business awardees
must be reachable. Every plausible niche has thousands, far above the founder's
~300 sends/month, so prospect COUNT carries no decision information and must not
be scored — it only has to clear a floor.

Design notes, learned from two failures on 2026-08-29:
  1. The first version counted rows of an amount-sorted, capped result page.
     Every term saturated and seven of eight niches tied at exactly 91.0.
  2. The second version fixed the counts but kept caps below the real data
     (flow cap 8,000 vs 9k-41k actual; prospect cap 400 against a 500-row
     scan), so three of four terms were still constant — a one-variable ranking
     wearing a four-variable costume.
The lesson is encoded, not just remembered: render_table now reports per-term
spread and names any term that fails to discriminate, and score_niche records
whether a sample hit its scan cap. A scorer that cannot tell niches apart must
say so instead of emitting a confident ranking.
"""

import statistics

from . import config
from .usaspending_client import (SB_SET_ASIDE_CODES, award_count, sb_award_scan)

W_SET_ASIDE = 35
W_NOTICE_FLOW = 30
W_PRICE_BAND = 20
W_REPEAT_BIDDERS = 15

# A niche needs ~15 notices/week to fill an issue; below ~5/week it cannot.
NOTICE_FULL, NOTICE_FLOOR = 60, 20
BUYER_MIN, BUYER_MAX = 25_000, 1_500_000
REPEAT_FULL = 2.0            # 2+ awards per firm in-sample earns full credit
GATE_MIN_PROSPECTS = 150     # ~the smoke-test send volume
SCAN_PAGES = 5


def _price_band_fit(median: float) -> float:
    """1.0 inside the buyer band; decays faster above it than below.

    Asymmetric on purpose: a niche whose firms are too small may grow into the
    product, while one whose firms are too large has already bought a
    competitor's tool and is the reason the buyer loses.
    """
    if median <= 0:
        return 0.0
    if BUYER_MIN <= median <= BUYER_MAX:
        return 1.0
    if median < BUYER_MIN:
        return max(0.4, median / BUYER_MIN)
    return max(0.05, (BUYER_MAX / median) ** 1.5)


def score_niche(naics: str, label: str, use_sam: bool = True) -> dict:
    warnings: list[str] = []

    total = award_count(naics, months_back=24)
    set_aside = award_count(naics, months_back=24,
                            set_aside_codes=SB_SET_ASIDE_CODES)
    if total and set_aside > total:
        # set_aside_type_codes is unvalidated free text: a bad code returns 200
        # with a wrong count rather than an error. This is the tripwire.
        warnings.append(f"set-aside count ({set_aside}) exceeds total ({total}) "
                        f"— check SB_SET_ASIDE_CODES; share clamped")
    set_aside_share = min(set_aside / total, 1.0) if total else 0.0

    scan = sb_award_scan(naics, months_back=24, pages=SCAN_PAGES)
    amounts = [r["amount"] for r in scan["rows"] if (r["amount"] or 0) > 0]
    median_award = statistics.median(amounts) if amounts else 0.0
    prospects = scan["prospects"]
    awards_per_firm = (scan["rows_scanned"] / len(prospects)) if prospects else 0.0
    if not prospects:
        warnings.append("no small-business awardees returned — price/repeat "
                        "terms are 0 by default, not by evidence")

    notices_30d = None
    notice_error = None
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

    terms = {
        "set_aside": set_aside_share * W_SET_ASIDE,
        "price_band": _price_band_fit(median_award) * W_PRICE_BAND,
        "repeat_bidders": min(awards_per_firm / REPEAT_FULL, 1.0) * W_REPEAT_BIDDERS,
    }
    weights = {"set_aside": W_SET_ASIDE, "price_band": W_PRICE_BAND,
               "repeat_bidders": W_REPEAT_BIDDERS}
    if notices_30d is not None:
        flow = min(max(notices_30d - NOTICE_FLOOR, 0) / (NOTICE_FULL - NOTICE_FLOOR), 1.0)
        terms["notice_flow"] = flow * W_NOTICE_FLOW
        weights["notice_flow"] = W_NOTICE_FLOW

    # Renormalize to 100 so scores stay comparable when a term is unavailable.
    scale = 100 / sum(weights.values())
    terms = {k: round(v * scale, 1) for k, v in terms.items()}
    composite = round(sum(terms.values()), 1)

    return {
        "naics": naics,
        "label": label,
        "new_awards_24mo": total,
        "set_aside_awards_24mo": set_aside,
        "set_aside_share": round(set_aside_share, 3),
        "median_sb_award": median_award,
        "sample_size": len(amounts),
        "distinct_sb_awardees": len(prospects),
        "awards_per_firm": round(awards_per_firm, 2),
        "notices_30d": notices_30d,
        "scan_capped": scan["scan_capped"],
        "prospects_gate": "pass" if len(prospects) >= GATE_MIN_PROSPECTS else "FAIL",
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
    head = (f"{'NAICS':7} {'score':>5} {'SetAsd%':>7} {'notices':>7} "
            f"{'med $':>10} {'firms':>6} {'a/firm':>6} {'gate':>5}  label")
    lines = [head, "-" * len(head)]
    for r in rows:
        if "error" in r:
            lines.append(f"{r['naics']:7} ERROR   {r['error'][:60]}")
            continue
        lines.append(
            f"{r['naics']:7} {r['composite']:>5} {r['set_aside_share']*100:>6.0f}% "
            f"{str(r['notices_30d'] if r['notices_30d'] is not None else '-'):>7} "
            f"{r['median_sb_award']:>10,.0f} {r['distinct_sb_awardees']:>6} "
            f"{r['awards_per_firm']:>6.2f} {r['prospects_gate']:>5}  {r['label']}")

    scored = [r for r in rows if "composite" in r]
    lines.append("")
    if not scored:
        return "\n".join(lines + ["No niche scored successfully."])

    # Per-term discrimination check — an aggregate spread check hides a live
    # term carrying the whole ranking while three dead terms pad the score.
    for term, weight in (("set_aside", W_SET_ASIDE), ("notice_flow", W_NOTICE_FLOW),
                         ("price_band", W_PRICE_BAND),
                         ("repeat_bidders", W_REPEAT_BIDDERS)):
        vals = [r["terms"][term] for r in scored if term in r["terms"]]
        if len(vals) < 2:
            continue
        spread = max(vals) - min(vals)
        if spread < 0.2 * weight:
            lines.append(f"DEAD TERM: {term} spans only {spread:.1f} pts — it is "
                         f"not discriminating; the ranking does not depend on it.")
    if any(r.get("scan_capped") for r in scored):
        lines.append("NOTE: the award scan hit its page cap for at least one "
                     "niche — distinct-firm counts are bounded by the scan, not "
                     "the market, so treat them as a floor.")
    for r in scored:
        for w in r.get("warnings", []):
            lines.append(f"WARN {r['naics']}: {w}")

    # Shortlist, not a winner: the evidence supports narrowing to two, and a
    # 75/75 split of the smoke test measures reply rate, which beats any
    # composite this data can produce.
    top = [r for r in scored if "control" not in r["label"].lower()][:2]
    lines.append("")
    if len(top) == 2:
        gap = top[0]["composite"] - top[1]["composite"]
        lines.append(f"SHORTLIST: {top[0]['naics']} ({top[0]['composite']}) and "
                     f"{top[1]['naics']} ({top[1]['composite']}), gap {gap:.1f}.")
        lines.append("Gap under 10 points → split the 150-send smoke test 75/75 "
                     "and let reply rate decide. Gap over 10 → lead with the top "
                     "one and keep the other as the month-2 fallback.")
    lines.append("Weights: set-aside 35, notice flow 30, price band 20, repeat "
                 "bidders 15 (renormalized if a term is unavailable). "
                 "Prospect count is a gate, not a score.")
    return "\n".join(lines)
