# Bid Scout Runbook

The founder's operating manual. Agents run everything below except the steps
marked **FOUNDER** — those are the bounded human work the Veritas council
priced in (~2–6 hrs/week at scale) plus one-time setup.

## 1. One-time setup (Day 1–3)

1. **FOUNDER — SAM.gov account + API key.** Register at sam.gov, get the public
   API key from your account details page. Roleless personal keys are reported
   at ~10 requests/day; an entity-associated role raises it (~1,000/day
   reported). **Measure yours:** run `python -m bidscout ingest --naics 541512`
   twice and watch for 429s; set `SAM_DAILY_BUDGET` to what you observed.
2. Environment: `export SAM_API_KEY=...` and optionally
   `export SAM_DAILY_BUDGET=10`. No other keys are needed (USAspending is keyless).
3. **Pick the niche.** Run `python -m bidscout score-niches --sam`.
   **Budget:** this spends 8 metered SAM requests (one count-only request per
   candidate niche) out of a 10/day roleless-key budget — do not run `ingest`
   the same day unless your key is role-based. Without `--sam` (or without a
   key) the notice-flow term is dropped and the remaining weights renormalize;
   the output says so, and that score is NOT decision-grade.

   How to read the output:
   - Terms are set-aside share 40, SAM notice flow 40, small-business win
     share 20. Distinct-firm counts are a **sample floor**, never scored.
   - `GATE FAIL` disqualifies a niche: either its firms are too large to be
     $49-79/mo buyers (median new SB award outside $10k-$1.5M) or there is too
     little small-business activity (<500 SB awards in 24 months).
   - `DEAD TERM` means that term stopped discriminating — the ranking is not
     trustworthy until it is understood. Do not pick from a table with a dead
     term carrying real weight.
   - `WARN ... set-aside count exceeds total` means `SB_SET_ASIDE_CODES` is
     wrong. Re-verify it against USAspending's `setAsideDefinitions` (see the
     comment on that constant) before trusting any share.
   - The scorer emits a **two-niche shortlist**, not a winner. Gap under 10
     points → split the 150-send smoke test 75/75 between them and let reply
     rate decide. Gap over 10 → lead with the top one, keep the second as the
     month-2 fallback.

   Record the decision in `state/niche.json` as `{"naics": "541519"}` — the
   weekly routine reads that file to know a niche has been chosen.
4. **FOUNDER — Payments: DEFERRED until a buyer says yes.** Do not set this up
   during onboarding. When a prospect actually agrees, create a Stripe Payment
   Link then (brief tier $49–79, data tier $29–49) with refund terms in the
   description ("first brief not useful → month refunded"); PayPal.me is the
   backup rail. Takes ~5 minutes and blocks nothing before that moment.
5. **FOUNDER — Identity placeholders (needed only at first SEND).** The brand
   name is already set to Worth the Bid. Still to fill in `site/index.html`:
   `[POSTAL_ADDRESS]` and `[FOUNDER_EMAIL]` (and the two price placeholders).
   CAN-SPAM requires a real postal address in every commercial email, so this
   is the one item that genuinely gates outreach — agents draft with a
   `[POSTAL_ADDRESS]` placeholder and it is filled at send time. Deploy `site/`
   to Cloudflare Pages (free, `*.pages.dev`) whenever convenient.
6. Seed `state/suppression.json` (already present) and **back it up** — the
   opt-out list must survive any machine loss.

## 2. Weekly production loop (agents; scheduled routine)

Schedule this as a weekly Claude routine per niche, off-peak:

```
python -m bidscout ingest --naics <code> --days 7   # 1 SAM request
python -m bidscout match
python -m bidscout packets                           # pulls USAspending context
# then, in Claude:
/bid-brief-writer  over state/packets/*.json  -> state/briefs/
/brief-qc          over state/briefs/         -> state/qc-log.md
```

Then the **FOUNDER QC block (weekly, 30–90 min at early scale):**
- Fix or discard every FLAG from qc-log; skim every PASS brief against 1–2 of
  its links (spot-check, not re-derivation — that was QC's job).
- Send each subscriber their briefs by email. Every delivery email includes the
  subscriber's SAM.gov saved-search link as the graceful-degradation fallback.

**Health check (agents, separate scheduled routine, +1 day):** run
`python -m bidscout selftest`; verify `state/briefs/` has files newer than 7
days and that the delivery log was updated. If not, alert the founder — a
silent missed week is the #1 cancellation trigger. Triage: selftest passes but
production failed → environment (key, quota, network); `budget` shows 0 →
ledger did its job, wait for reset or raise the measured budget.

## 3. Prospecting & outreach (validation phase: weeks 3–8)

1. `python -m bidscout prospects --naics <code> [--state ST]` → awardee list.
2. **FOUNDER-assisted enrichment:** for each target firm, look up the public
   POC email on sam.gov entity search (respect opt-outs — skip entities that
   suppressed public display). Agents can prepare the lookup queue; a key with
   Entity API access automates it later.
3. For each target: `python -m bidscout sample --firm "<name>" --notice <id>
   --reason "<public fact>"` builds the sample packet; the bid-brief-writer
   skill renders it; `python -m bidscout render` produces the HTML page to
   attach or host. Then `/outreach-drafter` writes the email around it.
4. **FOUNDER sends** from their own inbox: 20–30/day max, ~100–150 total for
   the smoke test. Fill `sent_at` in the batch log. Every reply gets a human
   answer (agent-drafted is fine); every opt-out goes into suppression.json
   the same day.
5. **FOUNDER collects payment:** when a prospect says yes, send the Stripe
   link, then add their profile to `subscribers/subscribers.json` (agents
   draft it from their reply; founder sanity-checks the set-aside certs).

## 4. Gates and metrics

- **Month-2 gate:** ≥2 paying firms OR ≥5% positive-reply→paid on 150+ sends.
  Fail once → switch niche (re-run score-niches, next candidate). Fail twice →
  stop; fall back to the GEO audit stream (see report.md §7).
- Track from client 1: subscribers by tier, gross adds, churn (target
  <10–15%/mo), replies per 100 sends, QC FLAG rate per batch.
- Churn >15%/mo → add retention artifacts (win/loss recap, quarterly pipeline
  review) or down-tier churners to the data tier before adding a second niche.

## 5. Reinvestment ladder (in order, from first revenue)

1. ~$10/yr domain + separate sending mailbox (kills the biggest fragility).
2. Bright Data pay-as-you-go if scraping needs appear (~$1.50/1k requests).
3. E&O insurance (~$40–80/mo) once MRR clears ~$500.
4. Manually-registered state/local portal accounts to widen coverage.

## 6. Never (from the compliance review)

- No cold email via free ESP tiers; founder's inbox only, at the caps above.
- No "AI-powered passive income" framing; no win probabilities; no "vetted" /
  "qualified" language; no incumbent stated as fact unless the notice names one.
- No scraping of registration-gated procurement portals; no coverage promises
  beyond verified sources.
- No delivery of any FLAGGED brief; no skipping the disclosure or the
  verify-before-bidding footer.
- Never run another product's outreach through the same inbox while Bid Scout
  is validating.
