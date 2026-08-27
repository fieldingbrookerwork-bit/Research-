---
name: outreach-drafter
description: Draft compliant, personalized first-touch emails to prospect firms, each built around a free sample Bid Scout brief on a live opportunity relevant to that firm. Use when preparing an outreach batch from state/prospects-*.json.
---

# Outreach Drafter

You draft; the founder sends from their own inbox. Volume and compliance rules
are hard limits, not style preferences.

## Hard limits

- **Batch size:** never draft more than 30 for one day's sending; recommended
  cadence 20–30/day, ~100–150 total during the smoke test.
- **Suppression first:** before drafting, check the recipient against
  `state/suppression.json` (emails + domains). Anyone present is skipped, with a
  note in the batch log. If the file is missing, stop — do not draft.
- **CAN-SPAM completeness:** every draft ends with the sender block containing
  the founder's real name, business name, **physical postal address placeholder
  `[POSTAL_ADDRESS]`** (founder fills in), and the line:
  "Reply 'unsubscribe' and you won't hear from me again — removals are honored
  immediately."
- **Truthful subject** describing the actual content (e.g. "[Solicitation #] —
  award-history brief for [Firm]"). No fake "Re:", no urgency theater.
- **Disclosure:** the body includes "research compiled with AI assistance" once,
  naturally placed.
- **No claims about the recipient's intent or performance** beyond what the
  public record shows (their SAM registration or a linked past award).

## Each draft

Inputs: one prospect row (from `state/prospects-<naics>.json`), one matched live
opportunity, and its sample brief (produced by bid-brief-writer with a
`sample: true` packet).

Structure (110–160 words):
1. One sentence naming the live opportunity (linked) and why it plausibly fits
   them — cite the public fact ("your firm's [award id] with [agency]" linked to
   USAspending, or "your SAM registration under NAICS [code] in [state]").
2. One sentence: attached/linked is a free research brief — incumbent context,
   past award prices, deadline — every claim linked to the federal record.
3. The offer, plainly: this is what subscribers get weekly for their NAICS+state
   at $49–79/month; reply if useful and [founder name] will set it up.
4. Sender block (above).

No follow-up sequence is drafted until the founder asks; a single respectful
touch per firm during validation.

## Output

Write drafts to `state/outreach/<date>/<slug>.md` plus a `batch-log.md` listing:
recipient, firm, opportunity id, suppression check result, and a blank
`sent_at:` field the founder fills when they actually send. Remind the founder
at the top of the log: send manually, 20–30/day max, stop immediately if any
recipient objects, and add every opt-out to suppression.json before the next
batch is drafted.
