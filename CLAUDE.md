# Bid Scout — project conventions

This repo is a running business system, not just research. Any Claude session
working here (including autonomous weekly routine runs) follows this file.

## Name

Customer-facing brand: **Worth the Bid** (site, briefs, outreach, anything a
buyer reads). Internal codename and Python package: `bidscout` — repo paths,
module names and CLI stay as they are; renaming them is churn with no external
benefit. Do not "fix" one into the other.

Niche: **NAICS 541519** (Other computer related services), recorded in
`state/niche.json`. Fallback 561210. See report.md for how it was chosen.

## What this is

Worth the Bid: weekly federal-contract opportunity matching + source-linked
"should you bid" research briefs for small government contractors, $49–79/mo
(brief tier) / $29–49/mo (data tier). `report.md` holds the research and
verdict; `RUNBOOK.md` is the operating manual and takes precedence on process.

## Absolutes (from the compliance review — never override)

- NEVER send outreach email from a session. Agents draft; the founder sends.
- NEVER deliver a brief to a subscriber; the founder delivers after their skim.
- The writer of a brief never QCs it — QC is always a separate agent
  (`.claude/skills/brief-qc/SKILL.md`).
- No outcome/win-probability claims, no "vetted/qualified" language, no
  incumbent stated as fact unless the notice names one, no free-ESP cold email,
  no scraping of registration-gated portals, no "AI passive income" framing.
- Every factual claim in a deliverable links to its federal record.
- Every deliverable carries the verify-before-bidding line + AI disclosure.

## The pipeline

`python3 -m bidscout <cmd>` — stdlib-only, no installs. Commands: `score-niches`,
`ingest --naics <code>`, `match`, `packets`, `sample`, `render`, `prospects
--naics <code>`, `budget`, `selftest`. Run `selftest` after any code change;
it must pass before committing.

- SAM.gov requests are metered by `state/sam_request_ledger.json` against
  `SAM_DAILY_BUDGET` (default 10/day). Never bypass the ledger.
- USAspending is keyless. Never call AI chat services for data collection.

## State & persistence

Containers are ephemeral: anything that must survive lives in git.
Tracked: `state/suppression.json` (opt-out list — append-only, never trim),
`state/niche.json` (the founder's niche pick), `state/niche_scores.json`,
`state/last_run_status.json`, `state/qc-log.md`, `state/briefs/`,
`state/outreach/`. Everything else in `state/` is regenerable and ignored.
Always `git pull` before working and commit+push tracked state before ending.

## Branch

All work on `claude/ai-subagent-income-research-3kqam0`. Push after committing;
retry once after 30s on failure and report if it still fails.

## Founder contact contract

Autonomous runs are summarized by email to the founder. When founder action is
required, the summary's FIRST line starts with `FOUNDER ACTION NEEDED:` and
says exactly what and why in one line each. No action → say so plainly or stay
brief. The founder's steps are only: environment unlocks, niche pick, brief
skim, sending outreach, replying to humans, and payment links.
