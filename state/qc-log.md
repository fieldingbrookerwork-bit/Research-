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

## 2026-08-30 — independent QC pass, 20 sample briefs (packets generated_utc 2026-08-30)

[PASS] sample-aatd-llc — 13 checks; clean (minor, non-blocking: "Your cited award is a guest Wi-Fi build for a VA facility" is sourced from state/prospect_scan-541519.json "GUEST WI-FI FOR DES MOINES", not from the packet; "build" is an inference)
[PASS] sample-accessagility-llc — 13 checks; clean (minor: "incumbent" appears only in the compliant negation "This notice record does not name an incumbent"; cited-award description and the Presolicitation-duplicate sentence are sourced from state/prospect_scan-541519.json and state/opportunities.json, not the packet — both verified true)
[PASS] sample-blue-raster-l-l-c — 13 checks; clean (minor: record says "ARBORETUM BOTANICAL EXPLORER (ABE) MOBILE APPLICATION"; brief characterises it as a "mapping application" — an inference, not in the record text)
[PASS] sample-blue-tech-inc — 13 checks; clean
[PASS] sample-colossal-contracting-llc — 13 checks; clean ("your record also shows Webex for Government" verified against award 49100426F0154 in state/prospect_scan-541519.json)
[PASS] sample-countertrade-products--inc — 13 checks; clean (minor: compliant "does not name an incumbent" negation)
[PASS] sample-csp-enterprises--llc — 13 checks; clean (minor: compliant "does not name an incumbent" negation)
[PASS] sample-cynergy-professional-systems-llc — 13 checks; clean (minor: record says "FY26 SECURE PDS"; brief expands to "secure protected distribution system installation" — expansion is reasonable but "installation" is inferred)
[PASS] sample-disys-solutions--inc — 13 checks; clean
[PASS] sample-enterprise-technology-solutions--inc — 13 checks; clean (3 candidate_related awards re-derived: $292,227.80 / $69,547.42 / $18,032.00, dates and URLs all exact)
[PASS] sample-government-acquisitions-llc — 13 checks; clean (minor: compliant "does not name an incumbent" negation; "same buying office (State Department)" verified — cited award 19AQMA26F0544 is Dept of State and the notice agency is STATE, DEPARTMENT OF)
[PASS] sample-impres-technology-solutions--inc — 13 checks; clean (minor: compliant "does not name an incumbent" negation)
[PASS] sample-metgreen-solutions-inc — 13 checks; clean (minor, judgment call: "That distinction decides whether your record qualifies" uses a word on the banned list, but not as a verdict — it is a question about the solicitation's past-performance criterion, and no verdict is offered. Founder may prefer to reword.)
[PASS] sample-minburn-technology-group--llc — 13 checks; clean (Presolicitation-duplicate claim verified: 36C25226R0071 appears in state/opportunities.json as both Presolicitation and Solicitation)
[PASS] sample-panamerica-computers--inc — 13 checks; clean (minor: compliant "does not name an incumbent" negation)
[PASS] sample-sdvo-solutions--llc — 13 checks; clean (packet generated_utc 2026-08-30T15:43:32+00:00, so in scope for this run)
[PASS] sample-software-information-resource-corp — 13 checks; clean (3 candidate_related awards re-derived exactly)
[PASS] sample-standard-blazar--llc — 13 checks; clean
[PASS] sample-sterling-computers-corporation — 13 checks; clean (minor: compliant "does not name an incumbent" negation)
[PASS] sample-swish-data-corporation — 13 checks; clean (minor: same "whether your record qualifies" wording as sample-metgreen-solutions-inc)

Award-ID/URL integrity (batch-specific check): all 20 "Why you're seeing this" lines were tested — the award ID in the sentence matches the CONT_AWD_<id> segment of the accompanying usaspending.gov URL in every case, and each line is reproduced character-for-character from its packet match.reasons. No mismatches.

Systemic observation (non-blocking, applies to the batch not to any one brief): the "Your cited award is ..." sentence in 19 of 20 briefs, and the "also appears ... as a separate Presolicitation notice" sentence in 8 of 20, are true and verifiable against state/prospect_scan-541519.json and state/opportunities.json, but neither fact is carried in state/packets/*.json. A QC pass restricted to the packet alone cannot verify them. Recommend the packet builder copy the subscriber award's `description` and a `duplicate_notices` field into the packet so these claims are packet-derivable.

Out of scope, not QC'd: demo-*.md, sample-strategic-communications-llc (no packet), sample-executive-information-systems--l-l-c (no packet).

### Re-check after reword (same 2026-08-30 pass, artifacts re-read from disk at mtime 15:56:28)

[PASS] sample-metgreen-solutions-inc — 13 checks re-run in full; clean. Reworded bullet now reads "...That distinction decides which of your past projects you can actually cite." Diffed byte-for-byte against the text QC'd earlier: that one sentence is the ONLY change to the file. Banned-list sweep now returns zero hits (previous "qualifies" token gone); the new wording asserts no new fact — it is a question about the solicitation's past-performance criterion. Days-remaining 29 re-derived: 2026-08-30T15:43:37+00:00 → 2026-09-28T17:00:00-04:00 = 29.22 → floor 29. Correct.
[PASS] sample-swish-data-corporation — 13 checks re-run in full; clean. Same reworded bullet, zero banned-list hits. Re-derived every field from the packet independently (packet unchanged, mtime 15:43): deadline, NAICS, agency, solicitation number, blank-set-aside disclosure, blank pop_state, notice type, median $113,119.59, 25 sampled awards, 36 months, empty candidate_related, both URLs verbatim, sam.gov URL notice_id == fa0630b52e8643468f1c7d0cba7ba961, award-ID/URL match (7571TE26F80249 both sides), match.reason verbatim, caution present, both footer lines exact. Days-remaining 29 re-derived: 2026-08-30T15:43:36+00:00 → 2026-09-28T17:00:00-04:00 = 29.22 → floor 29. Correct. Structural diff against sample-metgreen-solutions-inc shows the two files differ only in the three firm-specific lines (H1, "Why you're seeing this", cited-award bullet), all three re-verified.

[PASS] outreach state/outreach/2026-08-30/sample-metgreen-solutions-inc.md and sample-swish-data-corporation.md — regenerated drafts re-checked: zero URLs of any kind (only prose mentions of SAM.gov / USAspending.gov, no http/www/links); [POSTAL_ADDRESS] placeholder present; unsubscribe line present verbatim; AI-assistance disclosure present twice (body "research compiled with AI assistance" and footer framing.disclosure); `to:` line is still `[EMAIL — look up on sam.gov entity search]` with no real address anywhere in either file; [FOUNDER_NAME]/[FOUNDER_EMAIL] still placeholders. All packet-derived figures in the drafts re-verified (solicitation number, notice ID, agency, NAICS, deadline, median, 25 sampled awards, 36 months, subscriber award ID, caution, both framing lines, 29 days). Zero banned-list tokens. The only non-packet dollar figure is the "$49–79 a month" price line, which is the founder's own pricing and is identical across all 20 drafts in the batch.
