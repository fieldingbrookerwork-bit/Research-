"""USAspending.gov client (keyless, generous). Award history powers both the
brief's incumbent/pricing context and the prospect list of past awardees.

Honesty rule baked into the data model: USAspending shows AWARDEES, not
bidders. Award context is labeled "recent comparable awards", and any
incumbent inference is a candidate, never a fact, unless the solicitation
itself names one.
"""

from datetime import date, timedelta

from . import config
from .http import request_json

SPEND_BY_AWARD = f"{config.USASPENDING_BASE}/search/spending_by_award/"

AWARD_FIELDS = [
    "Award ID", "Recipient Name", "recipient_id", "Award Amount",
    "Start Date", "End Date", "Awarding Agency", "Awarding Sub Agency",
    "Description", "generated_internal_id", "Place of Performance State Code",
]


def _time_period(months_back: int) -> list[dict]:
    end = date.today()
    start = end - timedelta(days=months_back * 30)
    return [{"start_date": start.isoformat(), "end_date": end.isoformat()}]


def recent_awards(naics: str, months_back: int = 24, agency_name: str | None = None,
                  state: str | None = None, small_business_only: bool = False,
                  limit: int = 100, page: int = 1) -> list[dict]:
    """Recent contract awards in a NAICS, optionally narrowed by agency/state."""
    filters: dict = {
        "naics_codes": [naics],
        "time_period": _time_period(months_back),
        "award_type_codes": config.CONTRACT_AWARD_TYPES,
    }
    if agency_name:
        filters["agencies"] = [
            {"type": "awarding", "tier": "toptier", "name": agency_name}]
    if state:
        filters["place_of_performance_locations"] = [
            {"country": "USA", "state": state}]
    if small_business_only:
        filters["recipient_type_names"] = ["small_business"]
    payload = {
        "filters": filters,
        "fields": AWARD_FIELDS,
        "limit": limit,
        "page": page,
        "sort": "Award Amount",
        "order": "desc",
        "subawards": False,
    }
    data = request_json(SPEND_BY_AWARD, payload=payload)
    return data.get("results", [])


def normalize_award(raw: dict) -> dict:
    internal = raw.get("generated_internal_id", "")
    return {
        "award_id": raw.get("Award ID", ""),
        "recipient": raw.get("Recipient Name", ""),
        "amount": raw.get("Award Amount", 0),
        "start": raw.get("Start Date", ""),
        "end": raw.get("End Date", ""),
        "agency": raw.get("Awarding Agency", ""),
        "sub_agency": raw.get("Awarding Sub Agency", ""),
        "description": (raw.get("Description") or "")[:300],
        "pop_state": raw.get("Place of Performance State Code", ""),
        "usaspending_url": (
            f"https://www.usaspending.gov/award/{internal}" if internal else ""),
    }


def award_context_for(opportunity: dict, months_back: int = 36,
                      limit: int = 25) -> dict:
    """Comparable-award context for one opportunity: same NAICS, same awarding
    toptier agency when it can be derived, ranked by amount. Keyword overlap
    with the opportunity title marks likely-related awards (candidate
    incumbents) — explicitly a heuristic, surfaced as such.
    """
    toptier = (opportunity.get("agency") or "").split(".")[0].strip() or None
    try:
        raws = recent_awards(opportunity.get("naics", ""), months_back=months_back,
                             agency_name=toptier, limit=limit)
    except Exception:
        # Toptier name may not match USAspending's naming; degrade to NAICS-only.
        raws = recent_awards(opportunity.get("naics", ""), months_back=months_back,
                             limit=limit)
        toptier = None
    awards = [normalize_award(a) for a in raws]

    title_words = {w.lower() for w in opportunity.get("title", "").split()
                   if len(w) > 4}
    for a in awards:
        desc_words = {w.lower().strip(",.;()") for w in a["description"].split()}
        a["title_overlap"] = len(title_words & desc_words)
    awards.sort(key=lambda a: (-a["title_overlap"], -(a["amount"] or 0)))

    amounts = sorted(a["amount"] or 0 for a in awards)
    median = amounts[len(amounts) // 2] if amounts else 0
    return {
        "scoped_to_agency": toptier,
        "months_back": months_back,
        "award_count": len(awards),
        "median_amount": median,
        "candidate_related": [a for a in awards if a["title_overlap"] >= 2][:5],
        "top_awards": awards[:10],
    }


def small_business_awardees(naics: str, state: str | None = None,
                            months_back: int = 24, pages: int = 3) -> list[dict]:
    """Distinct small-business awardees in a NAICS (+state) — the prospect
    universe. Contact emails come from SAM entity records (key required) or
    manual lookup; this returns names, totals, and USAspending links.
    """
    seen: dict[str, dict] = {}
    for page in range(1, pages + 1):
        raws = recent_awards(naics, months_back=months_back, state=state,
                             small_business_only=True, limit=100, page=page)
        if not raws:
            break
        for raw in raws:
            a = normalize_award(raw)
            key = a["recipient"].upper()
            entry = seen.setdefault(key, {
                "recipient": a["recipient"], "awards": 0, "total_amount": 0,
                "latest_award": "", "example_award_url": a["usaspending_url"],
            })
            entry["awards"] += 1
            entry["total_amount"] += a["amount"] or 0
            entry["latest_award"] = max(entry["latest_award"], a["start"] or "")
    prospects = sorted(seen.values(), key=lambda p: -p["total_amount"])
    return prospects
