---
name: brief-qc
description: Adversarially verify a Worth the Bid brief against its packet before delivery. Run on every brief in state/briefs/; the founder reviews only what this flags. Use before any delivery batch.
---

# Brief QC

You are the second, independent pass. Assume the brief contains an error and try
to find it. One hallucinated award amount reaches every subscriber matched to
this notice, and these readers know their own market — a visible error ends the
account and the referral loop.

## Procedure

For each `state/briefs/<id>.md` with its packet `state/packets/<id>.json`:

1. **Re-derive every number.** Deadline, NAICS, set-aside, each award amount,
   each date, median: locate the exact value in the packet JSON. Any value not
   present character-for-character in the packet is a FLAG (severity: fatal).
2. **Re-check every link.** Each `sam.gov` and `usaspending.gov` URL must appear
   verbatim in the packet. Invented or altered URLs: fatal.
3. **Incumbent language audit.** Search the brief for "incumbent", "currently
   held", "the current contractor". Any such phrase stated as fact (rather than
   "candidate related award") without the solicitation naming an incumbent: fatal.
4. **Outcome-language audit.** Any of: win/winnable, vetted, qualified (as a
   verdict), guarantee, probability, "strong chance", "easy": fatal.
5. **Footer check.** The verify-before-bidding line and the AI disclosure must
   both be present: fatal if either is missing.
6. **Cautions check.** Every `match.cautions` item represented: major if missing.
7. **Staleness check.** If packet `generated_utc` is >7 days old or the deadline
   has passed: major (do not deliver stale briefs).
8. **Days-remaining arithmetic.** Recompute deadline minus generated date; a
   wrong count is major.

## Output

Append one line per brief to `state/qc-log.md`:

`[PASS|FLAG] <id> — <n> checks; <list of findings with severity, or "clean">`

Then print a summary block:

- **PASS list** — cleared for the founder's skim.
- **FLAG list** — each with the exact finding, the packet value, and the brief
  value side by side. These the founder must fix or discard; never deliver a
  FLAG unfixed.

Do not fix briefs yourself unless explicitly asked; QC and authorship stay
separate so this pass remains adversarial.
