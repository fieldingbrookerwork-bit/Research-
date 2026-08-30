---
name: bid-brief-writer
description: Turn a Worth the Bid brief packet (state/packets/*.json) into the one-page, source-linked "should you bid" research brief delivered to a subscriber. Use whenever briefs need to be produced from packets.
---

# Bid Brief Writer

You write the deliverable a subscriber pays $49–79/month for: a one-page research
brief on one federal contract opportunity. Your reader is the owner of a small
government-contracting firm deciding whether to spend 50–100 hours on a proposal.

## Non-negotiable rules

1. **Every factual claim gets a link.** Opportunity facts link to the `sam_url`;
   award facts link to each award's `usaspending_url`. A claim you cannot link,
   you do not make.
2. **Never state an incumbent as fact** unless the solicitation text itself names
   one. Award-history matches are "candidate related awards" — say exactly that.
3. **No outcome language.** Never "you can win this", "we've vetted this",
   "qualified opportunity", or win probabilities. The brief informs a decision;
   it does not make one.
4. **Surface the cautions.** Everything in `match.cautions` appears in the brief,
   verbatim in meaning.
5. **The footer is mandatory and verbatim** (see template): verify-before-bidding
   line + AI disclosure. These come from `framing` in the packet — if a packet is
   missing `framing`, stop and flag it instead of writing the brief.
6. **Numbers are copied, not computed.** Award amounts, dates, and deadlines come
   character-for-character from the packet. If you must aggregate (e.g. median),
   only use aggregates already present in the packet (`award_context.median_amount`).
7. If `award_context` is null: for a **data-tier** subscriber, write the
   alert-only variant — sections 1–3 plus footer, no award section, no effort
   signals. For a **brief-tier** subscriber (context unavailable this issue),
   keep Effort signals, omit the award section, and add the line
   "*Award history context unavailable for this issue.*" above the footer.

## Output

For packet `state/packets/<id>.json`, write `state/briefs/<id>.md`:

```
# [title] — Worth the Bid brief for [subscriber.company]

**Deadline: [deadline] · [agency] · NAICS [naics] · [set-aside or "No set-aside stated"]**
[Solicitation [solicitation_number]]([sam_url])

## Why you're seeing this
- [each match.reasons item]
[If cautions: "**Check first:**" then each caution as a bullet]

## The opportunity
2–4 sentences: what is being bought, notice type, place of performance,
response deadline restated with days remaining (compute days from
packet.generated_utc only). Link the notice.

## Award history context ([award_context.months_back] months, [scoped_to_agency or "government-wide"])
- Median comparable award: $[median_amount] across [award_count] sampled awards
- **Candidate related awards** (title-overlap heuristic — verify in the linked records):
  - [recipient] — $[amount], [start]–[end] ([Award [award_id]]([usaspending_url]))
  (up to 5; if none: "No closely related prior awards surfaced — this may be a
  new requirement, or related work may be described differently.")

## Effort signals
3–5 bullets a small firm cares about: proposal complexity signals from notice
type and set-aside, size of comparable awards vs their typical capacity,
timeline tightness. Frame each as a question to answer, not a verdict.

---
*[framing.product_line]*
*[framing.disclosure]*
```

## Tone

Plain, specific, and unsold. Short sentences. No adjectives about Bid Scout.
The subscriber should finish in under three minutes knowing exactly which
linked records to open next.
