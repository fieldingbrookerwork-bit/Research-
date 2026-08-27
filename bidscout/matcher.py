"""Subscriber profiles and opportunity matching.

Profiles are plain JSON (see subscribers/example.json). Matching is
deterministic and explainable: every match carries its reasons, because the
brief leads with "why you're seeing this" and irrelevant alerts are the #1
churn driver in alert products.
"""

from dataclasses import dataclass, field


@dataclass
class Subscriber:
    id: str
    company: str
    email: str
    naics: list[str]
    states: list[str] = field(default_factory=list)      # empty = nationwide
    set_asides: list[str] = field(default_factory=list)  # e.g. SBA, SDVOSBC, 8A, HZC, WOSB
    keywords_any: list[str] = field(default_factory=list)
    keywords_exclude: list[str] = field(default_factory=list)
    min_fit: int = 2
    tier: str = "brief"  # "brief" ($49-79) or "data" ($29-49 alerts-only)
    active: bool = True

    @classmethod
    def from_dict(cls, d: dict) -> "Subscriber":
        allowed = {k: d[k] for k in cls.__dataclass_fields__ if k in d}
        return cls(**allowed)


# SAM setAside codes worth knowing; anything not listed passes through verbatim.
SET_ASIDE_LABELS = {
    "SBA": "Total Small Business",
    "SBP": "Partial Small Business",
    "8A": "8(a)",
    "8AN": "8(a) Sole Source",
    "HZC": "HUBZone",
    "SDVOSBC": "Service-Disabled Veteran-Owned SB",
    "SDVOSBS": "SDVOSB Sole Source",
    "WOSB": "Women-Owned Small Business",
    "EDWOSB": "Economically Disadvantaged WOSB",
}


def match(subscriber: Subscriber, opp: dict) -> dict | None:
    """Return {score, reasons, cautions} or None if the opportunity misses."""
    reasons: list[str] = []
    cautions: list[str] = []
    score = 0

    naics = opp.get("naics", "")
    if naics in subscriber.naics:
        score += 3
        reasons.append(f"NAICS {naics} is an exact profile match")
    elif any(naics.startswith(n[:4]) for n in subscriber.naics if len(n) >= 4):
        score += 1
        reasons.append(f"NAICS {naics} is in your industry family")
    else:
        return None

    text = f"{opp.get('title','')} {opp.get('set_aside_desc','')}".lower()
    for kw in subscriber.keywords_exclude:
        if kw.lower() in text:
            return None
    hit_kws = [kw for kw in subscriber.keywords_any if kw.lower() in text]
    if hit_kws:
        score += 2
        reasons.append("Title matches your keywords: " + ", ".join(hit_kws))

    pop = opp.get("pop_state", "")
    if not subscriber.states:
        score += 1
    elif pop and pop in subscriber.states:
        score += 2
        reasons.append(f"Place of performance {pop} is in your territory")
    elif not pop:
        score += 1
        cautions.append("Place of performance not stated in the notice")
    else:
        return None

    # Certification-specific set-asides hard-block unless the profile holds the
    # certification (onboarding collects these): sending an 8(a) sole-source
    # notice to a non-8(a) firm is exactly the irrelevant-alert churn driver.
    # Total/partial small business passes with a caution when certs are unknown.
    RESTRICTED = {"8A", "8AN", "HZC", "SDVOSBC", "SDVOSBS", "WOSB", "EDWOSB"}
    sa = (opp.get("set_aside") or "").upper()
    held = {s.upper() for s in subscriber.set_asides}
    if sa:
        if sa in held:
            score += 3
            reasons.append(
                f"Set-aside ({SET_ASIDE_LABELS.get(sa, sa)}) matches your certification")
        elif sa in RESTRICTED:
            return None
        elif not held:
            cautions.append(
                f"Notice is set aside ({SET_ASIDE_LABELS.get(sa, sa)}); "
                "profile lists no certifications — confirm eligibility")

    if score < subscriber.min_fit:
        return None
    return {"score": score, "reasons": reasons, "cautions": cautions}


def match_all(subscribers: list[Subscriber], opportunities: list[dict]) -> dict:
    """{subscriber_id: [ {opportunity, score, reasons, cautions}, ... ]}"""
    out: dict[str, list] = {}
    for sub in subscribers:
        if not sub.active:
            continue
        rows = []
        for opp in opportunities:
            m = match(sub, opp)
            if m:
                rows.append({"opportunity": opp, **m})
        rows.sort(key=lambda r: -r["score"])
        out[sub.id] = rows
    return out
