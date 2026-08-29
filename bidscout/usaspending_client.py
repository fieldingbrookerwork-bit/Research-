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
SPEND_BY_AWARD_COUNT = f"{config.USASPENDING_BASE}/search/spending_by_award_count/"

AWARD_FIELDS = [
    "Award ID", "Recipient Name", "recipient_id", "Award Amount",
    "Start Date", "End Date", "Awarding Agency", "Awarding Sub Agency",
    "Description", "generated_internal_id", "Place of Performance State Code",
    # Required in `fields` to be a legal `sort` key. "Base Obligation Date" maps
    # to date_signed (true award recency); "Start Date" is period-of-performance
    # start, which skews toward long-lead work and must not be used for samples.
    "Base Obligation Date",
]

# Small-business set-aside codes, verified against USAspending's own
# setAsideDefinitions / setAsideTypeMapping (usaspending-website
# src/js/dataMapping/search/contractFields.js, fetched 2026-08-29).
# This is the union of their small-disadvantaged, HUBZone, VOSB and WOSB
# groupings: every code meaning "competition restricted to small business or a
# small-business subcategory".
# Deliberately EXCLUDED: NONE (no set-aside); BI/ISEE/ISBEE (Native American-
# owned) and HMP/HMT (HBCU/MI) restrict competition but are not small-business
# size classifications — add them only with a stated reason.
# NOTE: USAspending validates set_aside_type_codes as free text with NO enum,
# so a wrong code returns HTTP 200 with a silently LOW count. An earlier version
# of this list was missing HS3, HS2Civ, RSBCiv, 8ACCiv and VSBCiv — RSBCiv
# ("Reserved for Small Business $2,501 to $100K") especially, which covers the
# high-volume small-purchase reserve. Never edit this list without re-checking
# it against that source file.
SB_SET_ASIDE_CODES = [
    # small-disadvantaged / general small business
    "SBA", "SBP", "8A", "8AN", "8ACCiv", "HS3", "HS2Civ", "ESB",
    "RSBCiv", "VSBCiv",
    # HUBZone
    "HZC", "HZS",
    # veteran-owned
    "SDVOSBC", "SDVOSBS", "VSA", "VSS",
    # women-owned
    "WOSB", "WOSBSS", "EDWOSB", "EDWOSBSS",
]


def _months_ago(months: int) -> date:
    """Calendar-accurate offset; months*30 drifts ~10 days per 24 months."""
    end = date.today()
    total = end.year * 12 + (end.month - 1) - months
    y, m = divmod(total, 12)
    return date(y, m + 1, min(end.day, 28))


def _time_period(months_back: int, date_type: str | None = None) -> list[dict]:
    """Time window. date_type='new_awards_only' counts awards MADE in the window.

    The API default is asymmetric (lower bound on action_date, upper on
    date_signed), which selects awards *active* in the window — including
    modifications to contracts signed years earlier. That is right for a brief's
    comparable-award context and wrong for measuring new opportunity flow.
    """
    tp = {"start_date": _months_ago(months_back).isoformat(),
          "end_date": date.today().isoformat()}
    if date_type:
        tp["date_type"] = date_type
    return [tp]


def _award_filters(naics: str | None, months_back: int, agency_name: str | None = None,
                   state: str | None = None, small_business_only: bool = False,
                   date_type: str | None = None,
                   set_aside_codes: list[str] | None = None) -> dict:
    filters: dict = {
        "time_period": _time_period(months_back, date_type=date_type),
        "award_type_codes": config.CONTRACT_AWARD_TYPES,
    }
    if naics:
        filters["naics_codes"] = [naics]
    if set_aside_codes:
        filters["set_aside_type_codes"] = set_aside_codes
    if agency_name:
        filters["agencies"] = [
            {"type": "awarding", "tier": "toptier", "name": agency_name}]
    if state:
        filters["place_of_performance_locations"] = [
            {"country": "USA", "state": state}]
    if small_business_only:
        filters["recipient_type_names"] = ["small_business"]
    return filters


def award_count(naics: str | None, months_back: int = 24, state: str | None = None,
                small_business_only: bool = False,
                date_type: str | None = "new_awards_only",
                set_aside_codes: list[str] | None = None) -> int:
    """Population count of matching awards via spending_by_award_count.

    A true count, not a page of results — the only honest source for "how much
    flow does this niche have" and for share ratios. Counting rows of a capped
    result page (the original approach) saturates at the cap.

    Reads the "contracts" bucket specifically rather than summing all buckets:
    summing is correct only while award_type_codes stays contracts-only, and
    would silently inflate the moment anyone widens it to include IDVs.
    """
    payload = {
        "filters": _award_filters(naics, months_back, state=state,
                                  small_business_only=small_business_only,
                                  date_type=date_type,
                                  set_aside_codes=set_aside_codes),
        "subawards": False,
    }
    data = request_json(SPEND_BY_AWARD_COUNT, payload=payload)
    return int(data.get("results", {}).get("contracts", 0) or 0)


def recent_awards(naics: str, months_back: int = 24, agency_name: str | None = None,
                  state: str | None = None, small_business_only: bool = False,
                  limit: int = 100, page: int = 1,
                  sort: str = "Award Amount", order: str = "desc",
                  date_type: str | None = None) -> list[dict]:
    """Contract awards in a NAICS, optionally narrowed by agency/state.

    `sort` defaults to largest-first, which suits brief context (comparable
    awards a reader recognizes). Pass sort="Start Date" for a recency-ordered
    sample when the caller needs something representative rather than extreme —
    an amount-sorted slice is NOT a sample and must never be used for medians
    or population statistics.
    """
    payload = {
        "filters": _award_filters(naics, months_back, agency_name=agency_name,
                                  state=state,
                                  small_business_only=small_business_only,
                                  date_type=date_type),
        "fields": AWARD_FIELDS,
        "limit": limit,
        "page": page,
        "sort": sort,
        "order": order,
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


def sb_award_scan(naics: str, state: str | None = None, months_back: int = 24,
                  pages: int = 5, sort: str = "Base Obligation Date",
                  date_type: str | None = "new_awards_only") -> dict:
    """One scan of recent small-business awards, serving three callers at once.

    Returns {"rows": [...], "prospects": [...], "rows_scanned": n,
             "scan_capped": bool}. The scorer needs award amounts (median) and
    distinct firms (density) over the SAME sample; two separate paged scans with
    identical filters were duplicating pages 1-3 of every request.

    Ordered by date_signed (award recency), NOT by amount and NOT by
    period-of-performance start: an amount-sorted scan returns the same few
    large winners, and "Start Date" sorts by when work begins, which skews
    toward long-lead multi-year awards.

    `scan_capped` is the honest signal that the page budget, not the market,
    bounded the result — never treat a capped distinct-firm count as a
    measurement of market size.
    """
    seen: dict[str, dict] = {}
    rows: list[dict] = []
    for page in range(1, pages + 1):
        raws = recent_awards(naics, months_back=months_back, state=state,
                             small_business_only=True, limit=100, page=page,
                             sort=sort, order="desc", date_type=date_type)
        if not raws:
            break
        for raw in raws:
            a = normalize_award(raw)
            rows.append(a)
            key = a["recipient"].upper()
            entry = seen.setdefault(key, {
                "recipient": a["recipient"], "awards": 0, "total_amount": 0,
                "latest_award": "", "example_award_url": a["usaspending_url"],
            })
            entry["awards"] += 1
            entry["total_amount"] += a["amount"] or 0
            entry["latest_award"] = max(entry["latest_award"], a["start"] or "")
    return {
        "rows": rows,
        "prospects": sorted(seen.values(), key=lambda p: -p["total_amount"]),
        "rows_scanned": len(rows),
        "scan_capped": len(rows) >= pages * 100,
    }


def small_business_awardees(naics: str, state: str | None = None,
                            months_back: int = 24, pages: int = 5) -> list[dict]:
    """Distinct small-business awardees — the prospect list for outreach."""
    return sb_award_scan(naics, state=state, months_back=months_back,
                         pages=pages)["prospects"]


def probe_set_aside_codes(codes: list[str], naics: str | None = None,
                          months_back: int = 24) -> list[dict]:
    """Count awards per individual set-aside code.

    USAspending validates set_aside_type_codes as free text with no enum, so an
    invalid code and a valid-but-unused code both return zero. Probing each code
    alone — government-wide when naics is None — is the only way to tell them
    apart: a code that is zero across ALL federal contracts is either wrong or
    genuinely dead, and either way must not sit in a scoring filter pretending
    to contribute.
    """
    out = []
    for code in codes:
        try:
            n = award_count(naics, months_back=months_back, set_aside_codes=[code])
            out.append({"code": code, "awards": n, "error": None})
        except Exception as e:
            out.append({"code": code, "awards": None,
                        "error": f"{type(e).__name__}: {e}"})
    return out
