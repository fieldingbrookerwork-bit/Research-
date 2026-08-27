"""Brief packets: the deterministic, source-linked input for the brief-writer
skill. The pipeline asserts nothing it cannot link; judgment and prose belong
to the Claude skill layer, and the QC skill re-derives claims from these same
links.
"""

from datetime import datetime, timezone

from .usaspending_client import award_context_for


def build_packet(subscriber: dict, match_row: dict, with_awards: bool = True) -> dict:
    opp = match_row["opportunity"]
    packet = {
        "packet_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "subscriber": {
            "id": subscriber["id"],
            "company": subscriber["company"],
            "tier": subscriber.get("tier", "brief"),
        },
        "match": {
            "score": match_row["score"],
            "reasons": match_row["reasons"],
            "cautions": match_row["cautions"],
        },
        "opportunity": opp,
        "award_context": None,
        "framing": {
            "product_line": "Research brief — verify every detail against the "
                            "linked federal records before bidding.",
            "disclosure": "Prepared with AI assistance from public SAM.gov and "
                          "USAspending.gov data; reviewed before delivery.",
            "prohibited_claims": [
                "guaranteed or predicted win probability",
                "statements that we 'vet' or 'qualify' bids automatically",
                "incumbent stated as fact unless named in the solicitation",
            ],
        },
    }
    if with_awards and subscriber.get("tier", "brief") == "brief":
        packet["award_context"] = award_context_for(opp)
    return packet
