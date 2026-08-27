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

    if failures:
        print("SELFTEST FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print(f"SELFTEST PASS — {len(opps)} fixture opportunities, "
          f"{sum(len(v) for v in results.values())} matches, packet OK")
    return 0
