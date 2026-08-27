"""Niche scorer — the day-1 decision tool.

For each candidate NAICS it measures, from USAspending (keyless):
  - federal contract award flow over 24 months (count, total, median $)
  - small-business share of awards (is there room for small firms?)
  - distinct small-business awardees (= reachable prospect density)
and, when a SAM key is present, 30-day opportunity flow (one metered request
per NAICS). The composite prefers niches with steady flow, real SB share,
mid-size median awards (big enough to matter, small enough for small firms),
and a deep prospect pool.
"""

from . import config
from .http import BudgetExhausted
from .usaspending_client import recent_awards, small_business_awardees


def score_niche(naics: str, label: str, use_sam: bool = False) -> dict:
    all_awards = [a for page in (1, 2)
                  for a in recent_awards(naics, months_back=24, limit=100, page=page)]
    # Small-business slice via USAspending's recipient_type filter:
    sb_raw = [a for page in (1, 2)
              for a in recent_awards(naics, months_back=24,
                                     small_business_only=True, limit=100, page=page)]
    prospects = small_business_awardees(naics, months_back=24, pages=2)

    amounts = sorted(float(a.get("Award Amount") or 0) for a in all_awards)
    median = amounts[len(amounts) // 2] if amounts else 0.0
    total = sum(amounts)
    sb_share = (len(sb_raw) / len(all_awards)) if all_awards else 0.0

    opp_30d = None
    if use_sam and config.SAM_API_KEY:
        from .sam_client import fetch_opportunities
        try:
            opp_30d = len(fetch_opportunities(naics, days_back=30))
        except BudgetExhausted:
            opp_30d = None

    # Composite: flow (sampled award count), SB share, prospect density, and a
    # sweet-spot median ($100k-$5M scores highest for small-firm relevance).
    sweet = 1.0 if 100_000 <= median <= 5_000_000 else 0.4
    composite = round(
        min(len(all_awards), 200) / 200 * 30
        + sb_share * 30
        + min(len(prospects), 100) / 100 * 25
        + sweet * 15, 1)

    return {
        "naics": naics,
        "label": label,
        "awards_24mo_sampled": len(all_awards),
        "sb_awards_24mo_sampled": len(sb_raw),
        "sb_share_sampled": round(sb_share, 2),
        "median_award": median,
        "total_sampled": total,
        "distinct_sb_awardees": len(prospects),
        "opportunities_30d": opp_30d,
        "composite": composite,
    }


def score_all(use_sam: bool = False) -> list[dict]:
    rows = []
    for naics, label in config.CANDIDATE_NICHES.items():
        try:
            rows.append(score_niche(naics, label, use_sam=use_sam))
        except Exception as e:  # keep scoring the rest; report the failure
            rows.append({"naics": naics, "label": label, "error": str(e)})
    rows.sort(key=lambda r: -(r.get("composite") or -1))
    return rows


def render_table(rows: list[dict]) -> str:
    head = (f"{'NAICS':7} {'score':>5} {'awards':>6} {'SB%':>5} "
            f"{'median $':>12} {'SB firms':>8}  label")
    lines = [head, "-" * len(head)]
    for r in rows:
        if "error" in r:
            lines.append(f"{r['naics']:7} ERROR  {r['error'][:60]}")
            continue
        lines.append(
            f"{r['naics']:7} {r['composite']:>5} {r['awards_24mo_sampled']:>6} "
            f"{int(r['sb_share_sampled']*100):>4}% {r['median_award']:>12,.0f} "
            f"{r['distinct_sb_awardees']:>8}  {r['label']}")
    lines.append("")
    lines.append("Sampled = first 200 awards by amount, 24 months. Pick the top "
                 "composite whose label is NOT a local-heavy control; confirm "
                 "with opportunities_30d once a SAM key is set.")
    return "\n".join(lines)
