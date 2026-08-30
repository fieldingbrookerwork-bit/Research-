"""Score prospect firms for outreach fitness — keyless, auditable, no silent drops.

WHY THIS EXISTS
---------------
`prospects` returns every distinct firm that USAspending reports as a
small-business awardee in a NAICS. Two independent defects make that list unfit
to mail as-is, both documented in state/last_run_status.json (2026-08-30):

1. **NAICS 541519 is a catch-all.** "Other computer related services" collects
   whatever a contracting officer could not place elsewhere, so the awardee list
   carries a party-rental company (tents, fans, generators), an industrial
   controls distributor, a broadcaster's antenna-site lease and a legal
   publisher alongside genuine IT firms.

2. **`small_business` on USAspending is per-award self-certification**, not a
   size determination. A giant that self-certified small on one small order
   appears exactly like a five-person shop.

MEASUREMENT LIMITS — read before trusting any number here
---------------------------------------------------------
* `total_amount` is obligations **inside one NAICS, inside the scan window, and
  inside a page-capped scan**. It therefore UNDERSTATES every firm, without
  exception. Crossing the scale ceiling proves a firm is too big; staying under
  it proves nothing at all. This is not a theoretical caveat: in the 2026-08-30
  scan CARAHSOFT appears at $4,500 and SHI INTERNATIONAL at $15,331 — both far
  under any sane ceiling. A dollar test alone cannot catch the giants, which is
  precisely why NAME_EXCLUSIONS exists as a separate, independent rule.
* `latest_award` from `sb_award_scan` is the period-of-performance START date,
  not the award/signing date, so 54% of rows carry a FUTURE value. It is copied
  through as `latest_award_pop_start` and MUST NOT be used as an award date in
  outreach copy.
* Industry classification reads award descriptions, which are free text written
  by contracting officers. Some are useless ("NEW AWARD", "TASK ORDER #3").
  Those firms are KEPT and flagged UNVERIFIABLE_INDUSTRY, never dropped.

CONTRACT
--------
Nothing is silently dropped. Every input firm appears in exactly one of `kept`
or `excluded`, and every excluded firm carries the rule that fired, the literal
token that matched, and the evidence text it matched in — so the founder can
audit a decision without re-running anything.
"""

import json
import re

# --------------------------------------------------------------------------
# RULE 1 — SCALE CEILING
# --------------------------------------------------------------------------
# A firm obligating more than this inside a single NAICS in the scan window
# already employs proposal staff and is not a $49-79/mo buyer. The niche's
# median small-business award is ~$60k (state/niche_scores.json), so this
# ceiling sits roughly two orders of magnitude above a typical single award.
# ONE-SIDED: see MEASUREMENT LIMITS. Over the line is decisive; under it is not.
SCALE_CEILING_USD = 5_000_000

# The band a target buyer actually lives in; used for ranking, not exclusion.
SWEET_SPOT_USD = (50_000, 3_000_000)

# --------------------------------------------------------------------------
# RULE 2 — NAME EXCLUSIONS (catches what the dollar test structurally cannot)
# --------------------------------------------------------------------------
# Matched against the firm name only, case-insensitive, on word boundaries.
# Each entry: (pattern, category, why this firm is not a buyer).
NAME_EXCLUSIONS: list[tuple[str, str, str]] = [
    # Large IT resellers / distributors / aggregators. These bid constantly and
    # have dedicated capture teams; a weekly research brief sells them nothing.
    (r"CARAHSOFT", "large_reseller", "Top-tier federal software aggregator; billions in annual federal sales"),
    (r"SHI INTERNATIONAL", "large_reseller", "Multi-billion-dollar global IT reseller"),
    (r"\bCDW\b", "large_reseller", "Fortune 500 IT reseller"),
    (r"INSIGHT (PUBLIC SECTOR|DIRECT|ENTERPRISES)", "large_reseller", "Fortune 500 IT reseller"),
    (r"\bCONNECTION\b.*\b(GOV|PUBLIC)", "large_reseller", "PC Connection — public-company IT reseller"),
    (r"\bZONES\b", "large_reseller", "National IT solutions reseller"),
    (r"WORLD ?WIDE TECHNOLOG", "large_reseller", "WWT — multi-billion-dollar integrator"),
    (r"PRESIDIO", "large_reseller", "National IT integrator, private-equity owned"),
    (r"\bEPLUS\b|E-?PLUS TECHNOLOG", "large_reseller", "Public-company IT reseller"),
    (r"IMMIXGROUP|\bDLT SOLUTIONS\b", "large_reseller", "Government software distributor (Arrow subsidiary)"),
    (r"SOFTWARE ?ONE|SOFTWAREONE", "large_reseller", "Global software reseller"),
    (r"GOVCONNECTION", "large_reseller", "Public-company IT reseller"),

    # Alaska Native Corporation / tribal / Native Hawaiian holding subsidiaries.
    # These hold 8(a) status through their parent, not through being small, and
    # are exempt from competitive 8(a) dollar limits. Not the buyer profile.
    (r"\bASRC\b|ARCTIC SLOPE", "anc_tribal_subsidiary", "Arctic Slope Regional Corporation subsidiary (ANC)"),
    (r"CHENEGA", "anc_tribal_subsidiary", "Chenega Corporation subsidiary (ANC)"),
    (r"CHUGACH", "anc_tribal_subsidiary", "Chugach Alaska Corporation subsidiary (ANC)"),
    (r"ALUTIIQ", "anc_tribal_subsidiary", "Afognak/Alutiiq subsidiary (ANC)"),
    (r"KONIAG", "anc_tribal_subsidiary", "Koniag Inc subsidiary (ANC)"),
    (r"\bNANA\b", "anc_tribal_subsidiary", "NANA Regional Corporation subsidiary (ANC)"),
    (r"\bAKIMA\b", "anc_tribal_subsidiary", "Akima / NANA family (ANC)"),
    (r"BERING STRAITS", "anc_tribal_subsidiary", "Bering Straits Native Corporation subsidiary (ANC)"),
    (r"OLGOONIK", "anc_tribal_subsidiary", "Olgoonik Corporation subsidiary (ANC)"),
    (r"GOLDBELT", "anc_tribal_subsidiary", "Goldbelt Inc subsidiary (ANC)"),
    (r"CHEROKEE NATION", "anc_tribal_subsidiary", "Cherokee Nation Businesses subsidiary (tribal)"),
    (r"\bTAHKOX\b", "anc_tribal_subsidiary", "Tahkox — Native corporation affiliate"),

    # Large federal integrators that occasionally self-certify on small orders.
    (r"\bLEIDOS\b|\bBOOZ ALLEN\b|\bACCENTURE\b|\bDELOITTE\b|\bIBM\b",
     "large_integrator", "Global consultancy / integrator"),
    (r"GENERAL DYNAMICS|\bCACI\b|\bSAIC\b|\bPERATON\b|\bMANTECH\b|\bNORTHROP\b|\bRAYTHEON\b",
     "large_integrator", "Large defense prime"),
    (r"\bDELL\b|\bMICROSOFT\b|\bORACLE\b|\bCISCO\b|\bAMAZON\b|\bGOOGLE\b|\bVMWARE\b",
     "oem_manufacturer", "OEM/manufacturer, not a small services firm"),

    # Obvious non-IT by trade name. Kept separate from description evidence so a
    # firm is never dropped on a name alone unless the name IS the trade.
    (r"PARTY RENTAL|\bRENTAL[S]?\b.*\b(TENT|PARTY)", "non_it_by_name", "Event/party rental company"),
    (r"ELECTRICAL EQUIPMENT", "non_it_by_name", "Electrical/industrial equipment distributor"),
    (r"\bPUBLICATIONS?\b|\bPUBLISHING\b", "non_it_by_name", "Publisher, not an IT services firm"),
    (r"LOCAL MEDIA|BROADCAST", "non_it_by_name", "Broadcaster/media company"),
    (r"\bCATERING\b|\bJANITORIAL\b|\bLANDSCAP", "non_it_by_name", "Facilities/food services"),
]

# --------------------------------------------------------------------------
# RULE 3 — INDUSTRY EVIDENCE from award descriptions
# --------------------------------------------------------------------------
# DECISIVE non-IT markers name a physical, non-IT deliverable. They exclude even
# when an IT-ish word also appears, because catch-all NAICS coding puts IT words
# next to non-IT buys ("ANTENNA LICENSE AGREEMENT", "CLX WORKSTATION").
NON_IT_DECISIVE = [
    "TENT", "GENERATOR", "PORTABLE TOILET", "CATERING", "FOOD SERVICE",
    "FURNITURE", "JANITORIAL", "LANDSCAP", "ROOFING", "HVAC", "PLUMBING",
    "ANTENNA SITE", "ANTENNA LICENSE", "FLAT PANEL ANTENNA",
    "RADIOGRAPHY", "X-RAY SYSTEM", "ALLEN-BRADLEY", "CONTROLLOGIX",
    "COPIER", "TONER", "TONER CARTRIDGE", "UNIFORM", "APPAREL",
    "LAWN", "PEST CONTROL", "CONSTRUCTION OF", "HAND TOOL",
]

# WEAK non-IT markers exclude only when NO IT evidence exists anywhere.
NON_IT_WEAK = [
    "SEMINAR", "CONFERENCE REGISTRATION", "PERIODICAL", "SUBSCRIPTION TO",
    "BOOKS", "TRAVEL", "LODGING", "VEHICLE", "SHIPPING AND INSTALLATION",
    "DEINSTALLATION", "MUSEUM",
    # NOTE: "RESERVATION SYSTEM" was here and was wrong -- a reservation system
    # IS software. Removed so the exclusion rests on the domain word, not on a
    # marker that mislabels software as non-IT.
]

# IT markers. Deliberately specific — bare "LICENSE" is NOT here, because
# "ANTENNA LICENSE AGREEMENT" would otherwise rescue a broadcaster.
IT_MARKERS = [
    "SOFTWARE", "LICENSES", "SAAS", "CLOUD", "CYBER", "INFORMATION TECHNOLOGY",
    "IT SUPPORT", "IT SERVICES", "HELP DESK", "HELPDESK", "SERVER", "NETWORK",
    "COMPUTER", "LAPTOP", "DATA MANAGEMENT", "DATABASE", "APPLICATION",
    "SOFTWARE DEVELOPMENT", "SYSTEMS INTEGRATION", "INFRASTRUCTURE",
    "MODERNIZATION", "SUSTAINMENT", "ANALYTICS", "GIS", "GEOSPATIAL",
    "ENDPOINT", "FIREWALL", "STORAGE", "BACKUP", "VIRTUALIZ", "MIGRATION",
    "HOSTING", "WEB", "PORTAL", "DIGITAL", "ENGINEERING SUPPORT",
    "TECHNICAL SUPPORT", "O&M", "OPERATIONS AND MAINTENANCE", "TELECONFERENCE",
    "AUDIO VISUAL", "AUDIO-VISUAL", "VTC", "ENTERPRISE ASSET MANAGEMENT",
    "SECURITY AWARENESS", "PROGRAM MANAGEMENT",
]

# Descriptions carrying no industry information at all.
UNINFORMATIVE = re.compile(
    r"^(NEW AWARD|TASK ORDER\s*#?\d*|MODIFICATION|OPTION YEAR\s*\d*|"
    r"IGF::\w+::IGF|N/A|NONE|\W*)$", re.I)


# Descriptions that read as product resale rather than delivered services.
# NOT an exclusion: small resellers genuinely bid small-business set-asides.
RESELLER_MARKERS = ["LICENSES", "RENEWAL", "SUBSCRIPTION", "MAINTENANCE RENEWAL",
                    "PURCHASE OF", "PROCUREMENT OF", "HARDWARE", "LAPTOP",
                    "WORKSTATION", "MONITOR", "PRINTER"]
SERVICES_MARKERS = ["SERVICES", "SUPPORT SERVICES", "DEVELOPMENT", "OPERATIONS",
                    "MAINTENANCE AND", "ENGINEERING", "CONSULTING", "STAFFING",
                    "HELP DESK", "HELPDESK", "MANAGEMENT SERVICES", "O&M",
                    "SUSTAINMENT", "MIGRATION", "INTEGRATION", "ANALYSIS"]


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).upper().strip()


# Markers match on a LEADING word boundary only. Leading, because a bare
# substring test is wrong -- "TENT" fires inside "CONTENT" and wrongly excluded
# SOFTWARE INFORMATION RESOURCE CORP, an Atlassian licensing reseller. Only
# leading, so a marker still matches its own plurals and suffixes
# ("TENT"->"TENTS", "COPIER"->"COPIERS", "LANDSCAP"->"LANDSCAPING").
_MARKER_RE: dict[str, re.Pattern] = {}


def _marker_re(marker: str) -> re.Pattern:
    rx = _MARKER_RE.get(marker)
    if rx is None:
        rx = _MARKER_RE[marker] = re.compile(r"\b" + re.escape(marker))
    return rx


def _hits(text: str, markers: list[str]) -> list[str]:
    return [m for m in markers if _marker_re(m).search(text)]


def _name_rule(name: str) -> tuple[str, str, str] | None:
    """First NAME_EXCLUSIONS entry matching the firm name, else None."""
    up = _norm(name)
    for pattern, category, why in NAME_EXCLUSIONS:
        if re.search(pattern, up):
            return pattern, category, why
    return None


def _industry_evidence(name: str, descriptions: list[str]) -> dict:
    """Classify a firm's federal work as IT / non-IT / unverifiable."""
    informative = [d for d in descriptions if not UNINFORMATIVE.match(_norm(d))]
    blob = _norm(name + " || " + " || ".join(informative))
    decisive = _hits(blob, NON_IT_DECISIVE)
    weak = _hits(blob, NON_IT_WEAK)
    it = _hits(blob, IT_MARKERS)
    return {
        "it_markers": it,
        "reseller_markers": _hits(blob, RESELLER_MARKERS),
        "services_markers": _hits(blob, SERVICES_MARKERS),
        "non_it_decisive": decisive,
        "non_it_weak": weak,
        "informative_descriptions": len(informative),
        "sample_descriptions": informative[:3] or descriptions[:3],
    }


def _fitness(p: dict, ev: dict) -> tuple[int, list[str]]:
    """0-100 outreach-fitness score for a KEPT firm, with its components.

    Ranking only — it orders the kept list, it never excludes.
    """
    parts: list[str] = []
    score = 0

    # IT relevance, up to 40.
    n_it = len(ev["it_markers"])
    it_pts = 0 if n_it == 0 else min(40, 15 + 8 * n_it)
    score += it_pts
    parts.append(f"it_relevance={it_pts} ({n_it} marker(s))")

    # Award activity, up to 25. More awards = an active federal bidder who
    # feels the cost of chasing the wrong ones.
    n = p.get("awards", 0)
    act = 0 if n <= 0 else min(25, 5 + 7 * (n ** 0.5))
    score += int(act)
    parts.append(f"activity={int(act)} ({n} award(s))")

    # Scale fit, up to 25. Inside the sweet spot is best; below it means the
    # firm may be too small to have a proposal budget at all.
    total = p.get("total_amount", 0) or 0
    lo, hi = SWEET_SPOT_USD
    if lo <= total <= hi:
        fit = 25
    elif total > hi:
        fit = 12
    elif total > 0:
        fit = 8
    else:
        fit = 0
    score += fit
    parts.append(f"scale_fit={fit} (${total:,.0f})")

    # Verifiability, up to 10. A firm whose descriptions say nothing cannot be
    # confirmed as IT; it stays in the list but ranks below firms that can.
    ver = 10 if ev["informative_descriptions"] > 0 else 0
    score += ver
    parts.append(f"verifiable={ver}")

    return min(100, score), parts


def _flags(p: dict, ev: dict) -> list[str]:
    out = []
    if ev["informative_descriptions"] == 0:
        out.append("UNVERIFIABLE_INDUSTRY — award descriptions carry no industry "
                   "information; confirm the firm is an IT services firm before sending")
    if ev["non_it_weak"] and ev["it_markers"]:
        out.append("MIXED_INDUSTRY — both IT and non-IT signals present: "
                   + ", ".join(ev["non_it_weak"]))
    if p.get("awards", 0) <= 1:
        out.append("SINGLE_AWARD — one award in the scan window; thin evidence "
                   "of an ongoing federal practice")
    if not (p.get("total_amount") or 0):
        out.append("ZERO_OBLIGATED — award(s) carry $0 obligated; the outreach "
                   "hook must cite the award id, not a dollar figure")
    # The 'latest_award' field is a period-of-performance START date for every
    # firm (see module docstring), so flagging all of them would be noise. Only
    # a FUTURE value is flagged, because that is the case where copying the
    # field into outreach produces a visibly absurd claim.
    la = p.get("latest_award") or ""
    if la and la > _today():
        out.append(f"FUTURE_POP_START — 'latest_award' is {la}, in the future. It "
                   "is a period-of-performance start date, not an award date; "
                   "never use it as an award date in copy")
    if ev["reseller_markers"] and not ev["services_markers"]:
        out.append("RESELLER_SIGNAL — award descriptions read as product resale "
                   "(" + ", ".join(ev["reseller_markers"]) + ") rather than "
                   "services. Kept: resellers do bid set-asides, but a "
                   "'should you bid' brief is a weaker fit — founder's call")
    return out


def _suppressed(name: str, suppression: dict) -> str | None:
    up = _norm(name)
    for entry in suppression.get("firms", []) or []:
        if _norm(entry) and _norm(entry) in up:
            return entry
    return None


def filter_prospects(prospects: list[dict], rows: list[dict],
                     suppression: dict | None = None) -> dict:
    """Partition prospects into kept/excluded with an auditable reason each.

    `rows` are award rows from sb_award_scan (they carry the descriptions the
    aggregated prospect records drop). A firm with no rows is still processed —
    it simply has no description evidence and is flagged, never dropped.
    """
    suppression = suppression or {}
    by_firm: dict[str, list[dict]] = {}
    for r in rows or []:
        by_firm.setdefault(_norm(r.get("recipient", "")), []).append(r)

    kept, excluded = [], []
    for p in prospects:
        name = p.get("recipient", "")
        firm_rows = by_firm.get(_norm(name), [])
        descriptions = [r.get("description", "") for r in firm_rows]
        ev = _industry_evidence(name, descriptions)

        base = {
            "recipient": name,
            "awards": p.get("awards", 0),
            "total_amount": p.get("total_amount", 0),
            "example_award_url": p.get("example_award_url", ""),
            "award_ids": sorted({r.get("award_id", "") for r in firm_rows
                                 if r.get("award_id")})[:5],
            "agencies": sorted({r.get("agency", "") for r in firm_rows
                                if r.get("agency")})[:3],
            "pop_states": sorted({r.get("pop_state", "") for r in firm_rows
                                  if r.get("pop_state")})[:3],
            # Deliberately renamed: the source field is mislabeled. See module docstring.
            "latest_award_pop_start": p.get("latest_award", ""),
            "evidence": ev,
        }

        # Rules fire in order; the FIRST match decides, so the reason recorded
        # is the strongest one, and the ordering is part of the documented spec.
        sup = _suppressed(name, suppression)
        if sup:
            excluded.append({**base, "rule": "R0_SUPPRESSED",
                             "matched": sup,
                             "why": "Firm is on the opt-out list — never contact",
                             "evidence_text": sup})
            continue

        nm = _name_rule(name)
        if nm:
            pattern, category, why = nm
            excluded.append({**base, "rule": "R2_NAME_EXCLUSION",
                             "category": category, "matched": pattern, "why": why,
                             "evidence_text": name})
            continue

        total = p.get("total_amount", 0) or 0
        if total > SCALE_CEILING_USD:
            excluded.append({
                **base, "rule": "R1_ABOVE_SCALE_CEILING",
                "matched": f"total_amount ${total:,.0f} > ${SCALE_CEILING_USD:,}",
                "why": ("Obligations in this NAICS alone exceed the small-firm "
                        "ceiling; this firm already has capture staff. NOTE: the "
                        "scan understates totals, so this test is one-sided — "
                        "over the line is decisive, under it proves nothing."),
                "evidence_text": f"{p.get('awards', 0)} award(s), ${total:,.0f}"})
            continue

        if ev["non_it_decisive"]:
            excluded.append({
                **base, "rule": "R3_NON_IT_DECISIVE",
                "matched": ", ".join(ev["non_it_decisive"]),
                "why": ("Award description names a non-IT physical deliverable. "
                        "NAICS 541519 is a catch-all, so this firm is coded here "
                        "without being an IT services firm."),
                "evidence_text": " | ".join(ev["sample_descriptions"])[:300]})
            continue

        if ev["non_it_weak"] and not ev["it_markers"]:
            excluded.append({
                **base, "rule": "R4_NON_IT_NO_COUNTERSIGNAL",
                "matched": ", ".join(ev["non_it_weak"]),
                "why": ("Non-IT signal in the award description with no IT signal "
                        "anywhere in the firm's record."),
                "evidence_text": " | ".join(ev["sample_descriptions"])[:300]})
            continue

        score, parts = _fitness(p, ev)
        kept.append({**base, "fitness_score": score,
                     "score_components": parts, "flags": _flags(p, ev)})

    kept.sort(key=lambda k: (-k["fitness_score"], -k["awards"]))
    excluded.sort(key=lambda e: e["rule"])

    by_rule: dict[str, int] = {}
    for e in excluded:
        by_rule[e["rule"]] = by_rule.get(e["rule"], 0) + 1

    return {
        "kept": kept,
        "excluded": excluded,
        "summary": {
            "input": len(prospects),
            "kept": len(kept),
            "excluded": len(excluded),
            "excluded_by_rule": dict(sorted(by_rule.items())),
            "flagged_kept": sum(1 for k in kept if k["flags"]),
        },
        "rules": {
            "R0_SUPPRESSED": "Firm appears on state/suppression.json 'firms'.",
            "R1_ABOVE_SCALE_CEILING":
                f"total_amount > ${SCALE_CEILING_USD:,} in this NAICS/window. "
                "One-sided: the scan understates totals, so passing is not evidence of smallness.",
            "R2_NAME_EXCLUSION":
                "Firm name matches a curated list of large resellers, OEMs, large "
                "integrators, ANC/tribal holding subsidiaries, or non-IT trades. "
                "This rule exists because the dollar test structurally cannot catch "
                "giants that self-certified small on one small order.",
            "R3_NON_IT_DECISIVE":
                "Award description names a non-IT physical deliverable; excludes "
                "even when an IT-ish word co-occurs.",
            "R4_NON_IT_NO_COUNTERSIGNAL":
                "Weak non-IT signal and no IT signal anywhere in the firm's record.",
            "KEPT_FLAGS":
                "Kept firms may still carry flags (UNVERIFIABLE_INDUSTRY, "
                "MIXED_INDUSTRY, SINGLE_AWARD, ZERO_OBLIGATED, "
                "POP_START_NOT_AWARD_DATE). Flags inform the founder; they never drop a firm.",
        },
        "measurement_limits": [
            "total_amount is one-NAICS, one-window, page-capped: it UNDERSTATES every firm.",
            "small_business on USAspending is per-award self-certification, not a size determination.",
            "latest_award_pop_start is a period-of-performance start date, not an award date.",
            "Industry classification reads free-text descriptions written by contracting officers.",
        ],
    }
