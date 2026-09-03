"""Offline end-to-end selftest on fixtures: normalize -> match -> packet.

This is what the scheduled routine's health check runs. It touches no network,
so a pass means the code path is sound and a production failure is environmental
(key, quota, connectivity) — exactly the triage split the runbook uses.
"""

from . import config
from .brief_packet import build_packet
from .matcher import Subscriber, match_all
from .sam_client import normalize_opportunity


def run() -> int:
    failures: list[str] = []

    raw = config.load_json(config.FIXTURES_DIR / "sam_opportunities.json")
    opps = [normalize_opportunity(o) for o in raw]
    if len(opps) < 3:
        failures.append(f"expected >=3 fixture opportunities, got {len(opps)}")
    for o in opps:
        if not o["notice_id"] or not o["sam_url"].startswith("https://sam.gov/"):
            failures.append(f"bad normalize: {o}")

    subs_raw = config.load_json(config.REPO_ROOT / "subscribers" / "subscribers.json")
    subs = [Subscriber.from_dict(s) for s in subs_raw]
    results = match_all(subs, opps)

    demo = results.get("demo-vasys", [])
    if not demo:
        failures.append("demo-vasys matched nothing; matcher or fixtures broken")
    else:
        top = demo[0]
        if top["score"] < 5:
            failures.append(f"top match score {top['score']} < 5")
        if not top["reasons"]:
            failures.append("top match has no reasons")
        if any("security guard" in r["opportunity"]["title"].lower() for r in demo):
            failures.append("keyword-excluded opportunity leaked through")

    wrong_sa = [r for r in results.get("demo-guards", [])
                if r["opportunity"]["set_aside"] == "SDVOSBC"]
    if wrong_sa:
        failures.append("set-aside gate failed: non-SDVOSB firm matched SDVOSBC notice")

    if demo:
        sub = next(s for s in subs_raw if s["id"] == "demo-vasys")
        packet = build_packet(sub, demo[0], with_awards=False)
        for key in ("opportunity", "match", "framing"):
            if key not in packet:
                failures.append(f"packet missing {key}")
        if "verify every detail" not in packet["framing"]["product_line"].lower():
            failures.append("packet framing lost the verify-before-bidding line")

    from .brief_packet import build_sample_packet
    sample = build_sample_packet("Example Firm, LLC", opps[0],
                                 "Your SAM registration under NAICS 541512 in VA",
                                 with_awards=False)
    if not sample.get("sample") or "framing" not in sample:
        failures.append("sample packet missing sample flag or framing")
    if not sample["match"]["cautions"]:
        failures.append("sample packet lost its outreach caution")

    # Niche scorer. Regression guard for all three 2026-08-29 failures: the
    # all-tied-at-91.0 saturation, the "one live term, three dead ones" version,
    # and the gate that measured sample yield instead of the market. Drives
    # score_niche itself with real probed population counts, so a scorer that
    # stops discriminating fails HERE rather than in front of the founder.
    from . import niche_scorer as ns

    # (total_new, set_aside, sb_won, notices_30d, median_sb_award)
    real = {
        "541519": (43608, 15263, 21804, 117, 59_998.0),
        "541330": (41436, 3315, 20330, 127, 159_268.0),
        "541512": (21752, 1305, 7265, 41, 185_071.0),
        "561612": (9292, 372, 2037, 9, 306_394.0),
    }
    import bidscout.sam_client as _sc
    saved = (ns.award_count, ns.sb_award_scan, ns.config.SAM_API_KEY)
    _saved_count = getattr(_sc, "count_opportunities", None)
    try:
        def _fake_count(n, months_back=24, set_aside_codes=None,
                        small_business_only=False, **kw):
            t, sa, sb, _, _ = real[n]
            if set_aside_codes:
                return sa
            return sb if small_business_only else t
        ns.award_count = _fake_count
        ns.sb_award_scan = lambda n, **kw: {
            "rows": [{"amount": real[n][4]}] * 400,
            "prospects": [{"recipient": f"F{i}"} for i in range(120)],
            "rows_scanned": 400, "scan_capped": True}
        ns.config.SAM_API_KEY = "test"
        _sc.count_opportunities = lambda n, days_back=30, **kw: real[n][3]
        scored = sorted([ns.score_niche(n, n) for n in real],
                        key=lambda r: -r["composite"])
    finally:
        ns.award_count, ns.sb_award_scan, ns.config.SAM_API_KEY = saved
        if _saved_count is not None:
            _sc.count_opportunities = _saved_count

    for term in ("set_aside", "notice_flow", "sb_win"):
        if len({r["terms"][term] for r in scored}) == 1:
            failures.append(f"score_niche: '{term}' scored identically across "
                            "four real niches — the term is saturated and "
                            "contributes nothing to the ranking")
    if len({r["composite"] for r in scored}) < len(scored):
        failures.append("score_niche: real counts produced duplicate composites")
    if not all(0 <= r["composite"] <= 100.01 for r in scored):
        failures.append("score_niche: composite outside 0-100")
    if abs(sum(scored[0]["terms"].values()) - scored[0]["composite"]) > 0.2:
        failures.append("score_niche: terms do not sum to composite")
    # A capped scan must never be scored, only reported.
    if any("distinct" in k and k in r.get("terms", {})
           for r in scored for k in r.get("terms", {})):
        failures.append("score_niche: scored a scan-bounded firm count")

    out = ns.render_table(scored)
    if "SHORTLIST" not in out:
        failures.append("render_table: must emit a two-niche shortlist")
    dead = [dict(r, terms=dict(r["terms"], set_aside=40.0)) for r in scored]
    if "DEAD TERM: set_aside" not in ns.render_table(dead):
        failures.append("render_table: must name a term that stops discriminating")
    # Buyer-size gate must reject a niche whose firms are too big to be buyers.
    big = ns.render_table([dict(scored[0], median_sb_award=9_000_000.0,
                                gates={"buyer_size": "FAIL", "activity": "pass"},
                                gates_pass=False)])
    if "GATE FAIL" not in big:
        failures.append("render_table: must report gate failures")

    # Prospect filter. The raw awardee list is not a buyer list: 541519 is a
    # catch-all NAICS and USAspending's small_business flag is per-award
    # self-certification. These cases are the real 2026-08-30 failures, kept as
    # a regression guard so a rule edit that stops catching them fails HERE.
    from .prospect_filter import SCALE_CEILING_USD, filter_prospects

    pf_prospects = [
        # kept: genuine small IT services firm
        {"recipient": "SDVO SOLUTIONS, LLC", "awards": 4, "total_amount": 149_995,
         "latest_award": "2027-01-01", "example_award_url": "https://x/1"},
        # excluded R1: over the scale ceiling
        {"recipient": "EPOCH CONCEPTS LLC", "awards": 1, "total_amount": 25_000_000,
         "latest_award": "", "example_award_url": "https://x/2"},
        # excluded R2: giant that self-certified small on a $4.5k order — the
        # dollar test CANNOT catch this one, which is the whole point of R2.
        {"recipient": "CARAHSOFT TECHNOLOGY CORP", "awards": 1, "total_amount": 4_500,
         "latest_award": "", "example_award_url": "https://x/3"},
        # excluded R2: ANC subsidiary
        {"recipient": "ASRC FEDERAL TECHNOLOGY SOLUTIONS, LLC", "awards": 1,
         "total_amount": 3_053_454, "latest_award": "", "example_award_url": "https://x/4"},
        # excluded R3: non-IT deliverable
        {"recipient": "SNYDER PARTY RENTAL INC", "awards": 1, "total_amount": 24_985,
         "latest_award": "", "example_award_url": "https://x/5"},
        # excluded R3: IT-ish word ("WORKSTATION") next to a decisive non-IT one
        {"recipient": "ELECTRICAL EQUIPMENT CO", "awards": 1, "total_amount": 77_449,
         "latest_award": "", "example_award_url": "https://x/6"},
        # kept: name reads non-IT, description proves it resells software
        {"recipient": "OFFICE REMEDIES, INC.", "awards": 1, "total_amount": 55_440,
         "latest_award": "", "example_award_url": "https://x/7"},
        # kept but flagged: description carries no industry information
        {"recipient": "PARROCO PRODUCTION GROUP INC", "awards": 1, "total_amount": 132_082,
         "latest_award": "", "example_award_url": "https://x/8"},
        # excluded R3: neutral name, decisive non-IT description. Isolates the
        # description rule from the name list.
        {"recipient": "SUMMIT SERVICES GROUP LLC", "awards": 1, "total_amount": 31_000,
         "latest_award": "", "example_award_url": "https://x/10"},
        # excluded R0: on the opt-out list
        {"recipient": "OPTED OUT LLC", "awards": 2, "total_amount": 100_000,
         "latest_award": "", "example_award_url": "https://x/9"},
    ]
    pf_rows = [
        {"recipient": "SDVO SOLUTIONS, LLC", "description": "IT SUPPORT SERVICES AND NETWORK REFRESH",
         "award_id": "A1", "agency": "Air Force", "pop_state": "AZ"},
        {"recipient": "EPOCH CONCEPTS LLC", "description": "ENTERPRISE ASSET MANAGEMENT",
         "award_id": "A2", "agency": "VA", "pop_state": "VA"},
        {"recipient": "CARAHSOFT TECHNOLOGY CORP", "description": "SANS SECURITY AWARENESS TRAINING RENEWAL",
         "award_id": "A3", "agency": "MSPB", "pop_state": "VA"},
        {"recipient": "ASRC FEDERAL TECHNOLOGY SOLUTIONS, LLC",
         "description": "INFRASTRUCTURE AND APPLICATION DESIGN", "award_id": "A4",
         "agency": "HHS", "pop_state": "MD"},
        {"recipient": "SNYDER PARTY RENTAL INC",
         "description": "PROVIDE TENTS, FANS, GENERATORS", "award_id": "A5",
         "agency": "DHS", "pop_state": "PA"},
        {"recipient": "ELECTRICAL EQUIPMENT CO",
         "description": "ALLEN-BRADLEY CLX WORKSTATION & CONTROLLOGIX 5590 CONTROLLER",
         "award_id": "A6", "agency": "NASA", "pop_state": "AL"},
        {"recipient": "OFFICE REMEDIES, INC.", "description": "TALEND LICENSES",
         "award_id": "A7", "agency": "NASA", "pop_state": "MD"},
        {"recipient": "PARROCO PRODUCTION GROUP INC", "description": "NEW AWARD",
         "award_id": "A8", "agency": "DHS", "pop_state": "DC"},
        {"recipient": "SUMMIT SERVICES GROUP LLC",
         "description": "ROOFING REPAIR AND HVAC REPLACEMENT AT BUILDING 4",
         "award_id": "A10", "agency": "GSA", "pop_state": "TX"},
        {"recipient": "OPTED OUT LLC", "description": "CLOUD MIGRATION SERVICES",
         "award_id": "A9", "agency": "GSA", "pop_state": "VA"},
    ]
    pf = filter_prospects(pf_prospects, pf_rows, {"firms": ["OPTED OUT LLC"]})
    verdict = {k["recipient"]: ("kept", k) for k in pf["kept"]}
    verdict.update({e["recipient"]: ("excluded", e) for e in pf["excluded"]})

    if len(pf["kept"]) + len(pf["excluded"]) != len(pf_prospects):
        failures.append("prospect_filter: a firm was silently dropped — every "
                        "input must appear in exactly one of kept/excluded")

    expect = {
        "SDVO SOLUTIONS, LLC": ("kept", None),
        "OFFICE REMEDIES, INC.": ("kept", None),
        "PARROCO PRODUCTION GROUP INC": ("kept", None),
        "EPOCH CONCEPTS LLC": ("excluded", "R1_ABOVE_SCALE_CEILING"),
        "CARAHSOFT TECHNOLOGY CORP": ("excluded", "R2_NAME_EXCLUSION"),
        "ASRC FEDERAL TECHNOLOGY SOLUTIONS, LLC": ("excluded", "R2_NAME_EXCLUSION"),
        # Name rule fires before the description rule, so this firm is caught
        # by R2 even though its description is also decisively non-IT.
        "SNYDER PARTY RENTAL INC": ("excluded", "R2_NAME_EXCLUSION"),
        "SUMMIT SERVICES GROUP LLC": ("excluded", "R3_NON_IT_DECISIVE"),
        "ELECTRICAL EQUIPMENT CO": ("excluded", "R2_NAME_EXCLUSION"),
        "OPTED OUT LLC": ("excluded", "R0_SUPPRESSED"),
    }
    for firm, (want_side, want_rule) in expect.items():
        got = verdict.get(firm)
        if got is None:
            failures.append(f"prospect_filter: {firm} missing from output")
            continue
        side, rec = got
        if side != want_side:
            failures.append(f"prospect_filter: {firm} was {side}, expected {want_side}")
        elif want_rule and rec.get("rule") != want_rule:
            failures.append(f"prospect_filter: {firm} excluded by "
                            f"{rec.get('rule')}, expected {want_rule}")

    # The CARAHSOFT case is the load-bearing one: it must NOT be reachable by
    # the dollar rule, or the name list looks redundant and gets deleted later.
    car = next(p for p in pf_prospects if p["recipient"].startswith("CARAHSOFT"))
    if car["total_amount"] > SCALE_CEILING_USD:
        failures.append("prospect_filter: the CARAHSOFT fixture no longer proves "
                        "that the dollar ceiling cannot catch a self-certified giant")

    # Every exclusion must be auditable without re-running anything.
    for e in pf["excluded"]:
        if not e.get("why") or not e.get("matched"):
            failures.append(f"prospect_filter: {e['recipient']} excluded without "
                            "a why/matched pair — not auditable")

    parroco = verdict["PARROCO PRODUCTION GROUP INC"][1]
    if not any(f.startswith("UNVERIFIABLE_INDUSTRY") for f in parroco["flags"]):
        failures.append("prospect_filter: an uninformative description must flag "
                        "UNVERIFIABLE_INDUSTRY rather than drop the firm")

    sdvo = verdict["SDVO SOLUTIONS, LLC"][1]
    if not any(f.startswith("FUTURE_POP_START") for f in sdvo["flags"]):
        failures.append("prospect_filter: a future latest_award must be flagged "
                        "as a period-of-performance start, not an award date")
    if "latest_award" in sdvo:
        failures.append("prospect_filter: the mislabeled 'latest_award' key must "
                        "not be carried through under its wrong name")

    if not pf["kept"] or pf["kept"] != sorted(pf["kept"],
                                              key=lambda k: (-k["fitness_score"], -k["awards"])):
        failures.append("prospect_filter: kept list is not ranked by fitness")

    # SAM entity matching. Regression guard for the 2026-09-03 defect: a
    # legalBusinessName lookup returned multiple registrations and the first was
    # a namesake for 3 of 8 firms tried -- one of them a registration that lapsed
    # in 2018, which would have dropped a live prospect as "inactive". A record
    # not matched by UEI must never drive a keep/drop decision.
    from .sam_entity import is_biddable

    verified_active = {"matches": 1, "verified": True, "match_basis": "uei",
                       "registration_status": "Active"}
    verified_dead = {"matches": 1, "verified": True, "match_basis": "uei",
                     "registration_status": "Inactive",
                     "registration_expires": "2018-11-09"}
    name_matched = {"matches": 3, "verified": False, "match_basis": "legal_name",
                    "ambiguous": True, "registration_status": "Inactive",
                    "registration_expires": "2018-11-09"}

    if is_biddable(verified_active)[0] is not True:
        failures.append("sam_entity: a UEI-verified Active registration must be biddable")
    if is_biddable(verified_dead)[0] is not False:
        failures.append("sam_entity: a UEI-verified Inactive registration must be a drop")
    verdict, why = is_biddable(name_matched)
    if verdict is not False and verdict is not None:
        failures.append(f"sam_entity: unexpected verdict {verdict!r} for a name match")
    if verdict is False:
        failures.append("sam_entity: a NAME-matched record must never produce a DROP -- "
                        "this is the exact 2026-09-03 defect, where a namesake's lapsed "
                        "registration would have disqualified a live prospect")
    if verdict is None and "namesake" not in (why or ""):
        failures.append("sam_entity: the unknown verdict must explain WHY it is unknown")
    for empty in ({}, {"matches": 0}):
        if is_biddable(empty)[0] is not None:
            failures.append("sam_entity: a missing record is UNKNOWN, not a drop")

    from .render import markdown_to_html
    title, body = markdown_to_html(
        "# Test Brief\n\n> note\n\n## Section\n- **bold** and "
        "[link](https://sam.gov/opp/X/view)\n\n---\n*footer line*")
    if title != "Test Brief" or '<a href="https://sam.gov/opp/X/view">' not in body:
        failures.append("render: title or link lost")
    if "**" in body or "<script" in body.lower():
        failures.append("render: markdown leaked or unexpected markup")

    if failures:
        print("SELFTEST FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print(f"SELFTEST PASS — {len(opps)} fixture opportunities, "
          f"{sum(len(v) for v in results.values())} matches, packet OK")
    return 0
