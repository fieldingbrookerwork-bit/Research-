# QC log

[PASS] demo-vasys-01 — 8 checks; clean (award-section checks N/A: award_context null)
[PASS] demo-vasys-02 — 8 checks; clean (award-section checks N/A: award_context null)
[PASS] demo-vasys-03 — 8 checks; clean (award-section checks N/A: award_context null)
[PASS] demo-guards-01 — 8 checks; clean (award-section checks N/A: award_context null; sole match.caution represented under "Check first")

## 2026-08-30 — sample outreach brief batch (independent adversarial QC)

[PASS] sample-strategic-communications-llc — 8 checks; clean (median $48,673 = floor of packet 48673.2; 12 days = floor of 12.55d from generated_utc 2026-08-30T02:47:13+00:00 to deadline; candidate_related empty and reported as such)
[PASS] sample-sdvo-solutions--llc — 8 checks; clean (12 days = floor of 12.13d; SDVOSB FAR 19.14 set-aside quoted verbatim from set_aside_desc; note: "hardware upgrade" is an unstated-but-hedged inference from title "VTC Upgrade", non-blocking)
[PASS] sample-executive-information-systems--l-l-c — 8 checks; clean (set_aside "" / set_aside_desc null: brief says "No set-aside stated", flags the blank field, and explicitly declines full-and-open — no unsupported status asserted; 11 days = floor of 11.88d; note: "no expansion in the notice record" for MRITSS is asserted beyond the packet's fields, which carry no notice description body — non-blocking)

## 2026-08-30 — post-rebrand re-verification (independent QC, "Bid Scout" → "Worth the Bid")

Re-check after the upstream rebrand rebase. `git diff HEAD -- state/briefs/` shows 1 insertion / 1 deletion per file, H1 only — no other line touched in any of the three briefs.

[PASS] sample-strategic-communications-llc — H1 matches current SKILL.md template exactly; title + company character-for-character from packet; no stale "Bid Scout"; deadline/agency/NAICS/set-aside line, sam.gov URL, median $48,673 across 25, and both footer lines unchanged from packet framing
[PASS] sample-sdvo-solutions--llc — H1 matches current SKILL.md template exactly; title + company character-for-character from packet; no stale "Bid Scout"; deadline/agency/NAICS/set-aside line, sam.gov URL, median $48,673 across 25, and both footer lines unchanged from packet framing
[PASS] sample-executive-information-systems--l-l-c — H1 matches current SKILL.md template exactly; title + company character-for-character from packet; no stale "Bid Scout"; deadline/agency/NAICS/"No set-aside stated" line, sam.gov URL, median $48,673 across 25, and both footer lines unchanged from packet framing

Out of scope, noted only: demo-*.md briefs and state/pages/demo-*.html still carry the old "Bid Scout brief for" header, and bidscout/render.py:30 still defaults `title = "Bid Scout brief"` (inert fallback — every brief has an H1 that overwrites it). Internal `bidscout` package name is correct per CLAUDE.md and is not a defect.
