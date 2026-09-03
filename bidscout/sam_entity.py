"""SAM.gov Entity Management API — enrich outreach prospects (metered).

WHAT THIS DOES AND DOES NOT GIVE YOU
------------------------------------
Measured against a live key on 2026-08-30, the Entity API returns, per firm:

  * ueiSAM                  -- the reliable lookup key, better than a legal name
  * registrationStatus      -- an ACTIVE registration is required to bid at all
  * registrationExpirationDate
  * physical address
  * pointsOfContact         -- POC NAMES and MAILING ADDRESSES

It does NOT return POC **email addresses**. Those sit behind SAM's FOUO/sensitive
data tier, which a standard public API key does not reach. So this narrows the
founder's manual step to one field -- the email -- rather than removing it. It
never invents one, and there is no code path here that could.

WHY registrationStatus MATTERS MORE THAN IT LOOKS
-------------------------------------------------
A firm whose SAM registration has lapsed cannot receive a federal award. Mailing
one a "should you bid" brief is wasted send volume against a fixed daily cap, and
it reads as unresearched to the recipient. Any firm that comes back not-Active is
a drop, not a prospect.

BUDGET
------
One metered SAM request per firm, through the same ledger as everything else.
`enrich_batch` stops cleanly when the budget runs out and reports how far it got,
so a partial run is resumable rather than lost.
"""

from . import config
from .http import BudgetExhausted, request_json

# Sections worth requesting. pointsOfContact is included because POC NAMES are
# returned even though emails are not -- a name lets outreach open with a person
# rather than a blank salutation.
_SECTIONS = "entityRegistration,coreData,pointsOfContact"


def _poc_name(poc: dict | None) -> str:
    if not poc:
        return ""
    parts = [poc.get("firstName") or "", poc.get("lastName") or ""]
    return " ".join(p.title() for p in parts if p).strip()


def lookup_entity(legal_name: str, uei: str | None = None) -> dict:
    """One metered Entity API lookup, keyed by UEI wherever possible.

    MEASURED 2026-09-03, and the reason this function insists on a UEI: a
    legalBusinessName search returns MULTIPLE registrations for most firms (2 or
    3 for six of eight tried), and taking the first was wrong for three of eight
    -- PANAMERICA COMPUTERS, STERLING COMPUTERS and COUNTERTRADE PRODUCTS all
    resolved to a namesake rather than the company holding the awards. The
    COUNTERTRADE namesake's registration had lapsed in 2018, which would have
    dropped a live prospect as "inactive". A name match is therefore NEVER
    authoritative: it is returned with verified=False and must not drive a
    keep/drop decision.
    """
    if not config.SAM_API_KEY:
        raise RuntimeError("SAM_API_KEY is not set. See RUNBOOK step 1.")
    params = {"api_key": config.SAM_API_KEY, "includeSections": _SECTIONS}
    by_uei = bool(uei)
    if by_uei:
        params["ueiSAM"] = uei
    else:
        params["legalBusinessName"] = legal_name
    data = request_json(config.SAM_ENTITY_BASE, params=params, sam_metered=True)
    ents = data.get("entityData") or []
    total = int(data.get("totalRecords") or len(ents))
    if not ents:
        return {"query": legal_name, "requested_uei": uei, "matches": 0,
                "verified": False,
                "note": "no SAM entity matched; do not infer anything from this"}

    e = ents[0]
    reg = e.get("entityRegistration") or {}
    core = e.get("coreData") or {}
    poc = e.get("pointsOfContact") or {}
    addr = (core.get("physicalAddress") or {})
    found_uei = reg.get("ueiSAM", "")
    return {
        "query": legal_name,
        "requested_uei": uei,
        "matches": total,
        # verified=True ONLY when the record was fetched by UEI and came back
        # with that same UEI. Everything else is a candidate, not a match.
        "verified": bool(by_uei and found_uei and found_uei == uei),
        "match_basis": "uei" if by_uei else "legal_name",
        "ambiguous": (not by_uei) and total > 1,
        "uei": found_uei,
        "legal_name": reg.get("legalBusinessName", ""),
        "dba": reg.get("dbaName") or "",
        "registration_status": reg.get("registrationStatus", ""),
        "registration_expires": reg.get("registrationExpirationDate", ""),
        "cage": reg.get("cageCode") or "",
        "city": addr.get("city", ""),
        "state": addr.get("stateOrProvinceCode", ""),
        "electronic_business_poc": _poc_name(poc.get("electronicBusinessPOC")),
        "government_business_poc": _poc_name(poc.get("governmentBusinessPOC")),
        # Stated explicitly so no later reader assumes the field was merely missed.
        "poc_email": None,
        "poc_email_note": ("NOT returned by the public Entity API — SAM keeps POC "
                           "email behind its FOUO/sensitive tier. Look it up "
                           "manually by UEI on sam.gov, or skip the firm."),
        "sam_entity_url": (f"https://sam.gov/entity/{reg.get('ueiSAM')}/coreData"
                           if reg.get("ueiSAM") else ""),
    }


def enrich_batch(firms: dict[str, str], existing: dict | None = None) -> dict:
    """Look up each firm, skipping any already verified in `existing`.

    `firms` maps firm name -> UEI (from USAspending's "Recipient UEI"). A firm
    with no UEI is SKIPPED rather than looked up by name: a name lookup cannot
    produce a verified record, and spending a metered request on one that cannot
    be trusted is worse than not spending it.

    Returns {"entities": {...}, "budget_exhausted": bool, "looked_up": n,
             "skipped_no_uei": [...]}. Stops at the ledger's limit rather than
    raising, so the caller keeps every result it paid for.
    """
    out = dict(existing or {})
    n = 0
    skipped = []
    for firm, uei in firms.items():
        if out.get(firm, {}).get("verified"):
            continue
        if not uei:
            skipped.append(firm)
            continue
        try:
            out[firm] = lookup_entity(firm, uei=uei)
            n += 1
        except BudgetExhausted:
            return {"entities": out, "budget_exhausted": True, "looked_up": n,
                    "skipped_no_uei": skipped}
    return {"entities": out, "budget_exhausted": False, "looked_up": n,
            "skipped_no_uei": skipped}


def is_biddable(entity: dict) -> tuple[bool, str | None]:
    """Can this firm actually receive a federal award right now?

    Three-valued on purpose. None means UNKNOWN, not False: an unverified or
    missing record is an absence of evidence, and dropping a live prospect on it
    is exactly the mistake the name-matching bug produced on 2026-09-03.
    """
    if not entity or not entity.get("matches"):
        return None, "no SAM entity record retrieved — status unknown, not disqualifying"
    if not entity.get("verified"):
        return None, ("record was matched by legal name, not UEI — SAM returns "
                      "multiple registrations per name and this one may be a "
                      "namesake. Unknown, not disqualifying. Re-look-up by UEI.")
    status = (entity.get("registration_status") or "").lower()
    if status != "active":
        return False, (f"SAM registration status is "
                       f"'{entity.get('registration_status')}' (expires "
                       f"{entity.get('registration_expires')}), not Active — this "
                       f"firm cannot currently receive a federal award")
    return True, "Active SAM registration, matched by UEI"
