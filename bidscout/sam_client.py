"""SAM.gov Get Opportunities API client (key required; free registration).

One request per NAICS per run with limit=1000 keeps a whole niche inside even
the ~10/day roleless key budget. Notice types of interest: presolicitation (p),
combined synopsis/solicitation (k), solicitation (o).
"""

from datetime import date, timedelta

from . import config
from .http import request_json


def _mmddyyyy(d: date) -> str:
    return d.strftime("%m/%d/%Y")


def fetch_opportunities(naics: str, days_back: int = 7, limit: int = 1000,
                        ptypes: str = "o,k,p") -> list[dict]:
    """Fetch recent opportunities for one NAICS. One metered request."""
    if not config.SAM_API_KEY:
        raise RuntimeError("SAM_API_KEY is not set. See RUNBOOK step 1.")
    today = date.today()
    params = {
        "api_key": config.SAM_API_KEY,
        "postedFrom": _mmddyyyy(today - timedelta(days=days_back)),
        "postedTo": _mmddyyyy(today),
        "ncode": naics,
        "ptype": ptypes,
        "limit": str(limit),
        "offset": "0",
    }
    data = request_json(config.SAM_BASE, params=params, sam_metered=True)
    return data.get("opportunitiesData", [])


def normalize_opportunity(raw: dict) -> dict:
    """Reduce a SAM opportunity record to the fields briefs actually use.

    Every field that reaches a subscriber keeps a source URL so the brief
    writer can link claims to the federal record.
    """
    notice_id = raw.get("noticeId", "")
    place = raw.get("placeOfPerformance") or {}
    state = ((place.get("state") or {}).get("code")
             or (place.get("state") or {}).get("name") or "")
    set_aside = raw.get("typeOfSetAside") or raw.get("typeOfSetAsideDescription") or ""
    return {
        "notice_id": notice_id,
        "title": raw.get("title", ""),
        "solicitation_number": raw.get("solicitationNumber", ""),
        "agency": raw.get("fullParentPathName", "") or raw.get("department", ""),
        "naics": raw.get("naicsCode", ""),
        "notice_type": raw.get("type", ""),
        "posted": raw.get("postedDate", ""),
        "deadline": raw.get("responseDeadLine", ""),
        "set_aside": set_aside,
        "set_aside_desc": raw.get("typeOfSetAsideDescription", ""),
        "pop_state": state,
        "description_api": raw.get("description", ""),  # often a URL to fetch
        "sam_url": raw.get("uiLink") or f"https://sam.gov/opp/{notice_id}/view",
    }
