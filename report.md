# AI-Subagent Income Streams — Research Report

**Date:** 2026-08-26
**Question:** Which monthly income streams can run almost entirely on AI sub-agents (prospecting, research, production, outreach), spending nothing (free tiers only), where the only human step is the founder collecting payment from a willing buyer?
**Method:** 27 research agents in three waves — a 13-agent evidence sweep (free-tier limits, market pricing, demand, precedents), a 5-agent idea funnel (independent ideation angles), and a 9-agent Veritas council (5 adversarial lens critics + 1 completeness critic + 3 independent judges) — plus synthesis. Every load-bearing number carries a source and an as-of date; see `evidence/`.

> **Honesty note on sources:** the research environment could not open many commercial pricing pages directly (network egress restrictions). Figures marked in `evidence/evidence-sweep.md` as search-mediated snapshots of official pages should each be re-verified live before money decisions. Nothing below rests on a single unverifiable source.

---

## 1. Executive summary

**Winner: Bid Scout — a curated federal-contract intelligence subscription for one niche of small government contractors, at $49–$79/month per firm.** Agents match new SAM.gov opportunities to each subscriber and write a source-linked "should you bid" brief per opportunity (incumbent, past award prices from USAspending, set-aside fit, effort estimate). All three independent Veritas judges ranked it #1 — one judging on 12-month expected value, one on robustness, one on constraint fit.

Why it won: it is the **only candidate whose entire pipeline runs indefinitely at $0** (government open data — no scraping-quota cliff, no AI-engine ToS violations, trivial email volume); it has the **highest regulatory survivability** of the five; its market is proven by **verified incumbents at the exact price band** (Jorpex $49/$149, BidSparq $249, DemandStar $35–70/region); its buyers are **pre-qualified and publicly identifiable** (SAM registrants and past awardees, with public contact info); and it **erodes slowest** competitively (no gold rush, conservative sticky buyers, unglamorous niche).

Honest expectations, per the judges' consensus (conservative-to-base): **month 3: $0–$350; month 6: $200–$900; month 12: $400–$2,000/month.** This is a real but modest income stream at strict $0 — the budget constraint itself, not the idea, is the main ceiling, and the cheapest relaxations (a ~$10/yr domain, Bright Data pay-as-you-go funded from first revenue, E&O insurance once MRR clears ~$500) remove most of it.

The council's most important cross-cutting finding: **the "only human step is collecting payment" constraint has zero verified precedent anywhere** — every verified earner in adjacent categories keeps a human in sales and QC. Every candidate, winner included, actually requires bounded founder labor. Bid Scout won partly because its required human work is the **smallest and most schedulable** of the five: roughly 2–6 hours/week of pre-ship brief QC plus reply threads, versus 8–15 hours/week of sales labor hidden in the GEO candidates. The plan below prices that in explicitly instead of pretending it away.

Runner-up and fallback: **C1, the AI Visibility Watchdog** (GEO audit → monitoring retainer), which uses the founder's existing `geo-visibility-check` skill — sellable today but heavily discounted by the council (commoditizing fast, unevidenced local-SMB demand, Gmail-channel fragility). It remains the designated pivot if Bid Scout misses its month-2 validation gate, and the audit skill's factual-accuracy layer resurfaces inside several near-miss candidates the completeness critic flagged for a second look (GBP suspension-reinstatement prep, AI-hallucination drift monitoring, a share-of-voice data product).

---

## 2. What $0 actually buys — verified capability audit

The plan's tool assumptions were verified against current (Aug 2026) terms. Key results, with the full detail in `evidence/evidence-sweep.md`:

| Capability | At $0, verified | Practical meaning |
|---|---|---|
| **Bright Data MCP** | 5,000 requests/month, recurring, no card (per official GitHub README, 2026-08) | The workhorse: SERP queries, scrape-as-markdown, structured scrapers (Google Maps reviews, public LinkedIn). ~165 ops/day. Hard stop at cap, no surprise bills. One caveat: a Gmail-only signup may gate some APIs until a card is added. |
| **Nimble MCP** | ~5,000 requests **one-time trial** (not renewing); business email may be required | Good for one proof-of-concept dataset (its Google Maps suite is strong). Do not build recurring operations on it. |
| **Twilio trial** | **Dead for real US SMS at $0.** Trial accounts cannot register A2P 10DLC; unregistered US traffic is carrier-blocked since 2023. SendGrid's free email tier died May 2025. | Any SMS-based service (missed-call text-back etc.) is not a $0 business. Cheapest legitimate go-live ≈ $19–25 one-time + ~$3/mo. |
| **Google APIs (no card)** | PageSpeed Insights 25k/day; CrUX 150 QPM; Search Console (own/verified properties only) | Free site-audit signals at scale. Maps Platform now **requires a credit card** (per-SKU free caps since Mar 2025); GBP API is application-gated (weeks, rejections common); Custom Search API is closed to new users and shuts down 2027-01-01. |
| **Open geo data** | Overpass API ~10k queries/day tolerated; Nominatim 1 req/s, bulk geocoding banned | Free business POI universe, but agents must be rate-limit-disciplined or get IP-banned without notice. |
| **Hosting** | Cloudflare Pages: unlimited static bandwidth, free `*.pages.dev` subdomain, no card | Best free host. Netlify free is now credit-based (tighter). GitHub Pages ToS bans commerce sites. A custom domain (~$10/yr) is the single highest-leverage non-free upgrade. |
| **Payments** | Stripe Payment Links: $0 monthly, 2.9% + $0.30. Gumroad 10% + $0.50 (30% via Discover; $100 first-payout floor for unverified accounts since Mar 2026). Lemon Squeezy 5% + $0.50. Ko-fi 0% on tips | Collecting payment — the one human step — is genuinely free to set up. |
| **Marketplaces** | Fiverr: free to list, 20% fee, 4–8 week new-seller cold start, AI deliverables allowed if customized per order. Upwork: effectively **not** $0 (Connects) | Fiverr is the only true $0 services marketplace; treat it as a slow secondary channel. |
| **Email/newsletter** | Substack free (10% of paid subs); Beehiiv free ≤2,500 subs but monetization features gated at $43/mo | Owned-audience channel is free to start, slow to monetize. |
| **Founder's existing stack** | Production-grade `geo-visibility-check` skill (evidence-only GEO audits); Ahrefs, Local Falcon, Netlify connectors in Claude; Bright Data/Nimble available as Claude connectors | The GEO audit skill + Local Falcon + Ahrefs is a genuinely differentiated production asset vs. the $99 automated-scan competitors. Local Falcon free credits (~100) are a constraint; packages start $24.99/mo. |

### The binding constraint is distribution, not production

The single most decision-relevant finding of the evidence sweep:

- **Every checked free ESP tier (Brevo, Mailjet, MailerSend, Zoho) prohibits cold email in its ToS.** The only compliant $0 channel is the founder's own Gmail at a practical **20–30 personalized sends/day (~400–600/month)**. CAN-SPAM permits cold email (opt-out model) with truthful headers, a physical address, and a working unsubscribe.
- Realistic conversion at 2026 benchmarks (Instantly: 3.43% avg reply, declining; Belkins: ~5.8% for personalized sub-50 batches; 40–60% of replies positive): **2–4 positive replies per 100 sends** — roughly 10–25 positive conversations per month at maximum compliant volume.
- **LinkedIn automation is banned** (§8.2, heavily enforced). 61% of founder-relevant subreddits ban self-promotion. Scaling cold outreach requires paid domains/inboxes — out of scope at $0.
- Precedent check: **no verified case exists of a fully agent-run service business where the human only collects payment.** Every verified earner keeps a human in sales and QC. The closest Stripe-verified comparables: AEO Engine (productized GEO service, $797–$2,997/mo, ~30 clients, ~$55.7K MRR, May 2026) and SEObot (~$61K MRR) — both human-fronted.

Every candidate below was therefore designed around: tiny-volume/high-relevance outreach, warm or inbound motions, marketplace listings, and production leverage — not bulk outbound.

---

## 3. Demand evidence for the leading category (GEO / AI visibility)

Both sides, because the council demanded it:

**For:** 45% of US consumers report having used AI for local business recommendations (BrightLocal 2026, n=1,002; up from 6% in 2025 — treat as an upper bound, possible framing inflation). ChatGPT at 700–800M weekly users (official, 2025). 408 new "generative engine optimization" GitHub repos in Jan–Aug 2026 vs 76 in all of 2025. 70+ commercial GEO tools priced $29–$499/mo; Profound raised a reported $35M Series B; a Stripe-verified productized GEO service (AEO Engine) does ~$55.7K MRR from ~30 clients.

**Against:** AI referral traffic is still ~0.32% of total website traffic (16× growth in 2 years, but tiny) — churn risk when ROI stays invisible. C-SEO Bench (NeurIPS 2025) found most GEO content tactics "largely ineffective"; Ahrefs finds ~95% of AI citation behavior unexplained. Free AI-visibility reports are already the industry-standard lead magnet. Local-SMB willingness to pay for GEO specifically is the least-evidenced link in the chain.

**Design consequence:** anything sold here must be **measurement, monitoring, and source-hygiene** — never ranking guarantees. That happens to be exactly what the founder's `geo-visibility-check` skill produces (it is explicitly evidence-only and anti-fabrication).

---

## 4. The top 5 candidates

Selected from ~30 generated ideas across five independent ideation angles (see `evidence/idea-funnel.md`), filtered by pricing evidence and $0-feasibility. Notable kills before the top 5: **Twilio SMS services** (impossible at $0 — A2P), **accessibility audits** (audit-only willingness-to-pay is $10–50; FTC fined accessiBe $1M for automated-compliance claims), **newsletters/digital products as a primary stream** (44–54% of products earn $0; months of $0 ramp).

### C1 — AI Visibility Watchdog *(direct-to-SMB GEO audit → monthly monitoring retainer)*

- **Offer:** one-off AI-visibility audit at $149–$299 — how ChatGPT/Gemini/Perplexity/Google AI present the business vs 3 named competitors, with prioritized hygiene fixes — converting into a $99–$199/mo monitoring + interpretation retainer.
- **Pricing evidence:** live competitors sell exactly this at $99 (Optimum Web), $249 + $99/mo re-scans (BizWhiz), $297 (ShE Innovates); typical specialist audits $500–$2,000; agency monitoring-only retainers $500–$1,500/mo; self-serve SaaS $29–$489/mo (Otterly); Merchynt GBP management $125–$400/mo as the adjacent SMB budget line.
- **Agent pipeline:** Bright Data scrapes vertical+metro prospect universes → agents pre-run teaser scans → founder's Gmail sends 20–30 personalized, evidence-led emails/day ("ChatGPT recommends your competitor when asked for X — screenshot attached") → full audit delivered on Cloudflare Pages → Stripe link (human step) → scheduled monthly re-runs and delta reports.
- **Grounded model:** 500 sends/mo → 10–20 positive replies → 2–5 audit sales/mo; 40–60% retainer conversion; month 6 ≈ 8–15 retainers ($800–$2,500 MRR) + one-offs.
- **Honest weaknesses:** education-heavy sale; local-SMB GEO demand unevidenced; commoditizing wedge; AI-answer stochasticity requires multi-sample methodology; Local Falcon credit limits.

### C2 — GEO Ledger *(white-label AI-visibility reports for small local-SEO agencies)*

- **Offer:** unbranded monthly per-client-location AI-visibility report at $49–$99/location/mo wholesale (agency marks up 2–4× inside its retainers); one-off white-label audits $75–$150.
- **Pricing evidence:** an existing wholesale market for white-label local SEO audits at $49–$250 (GBPPromote $49, SEOHive $97); white-label SEO wholesale $178–$2,000/mo resold at 2–4×; agencies retail audits at $200–$5,000; Insites already sells white-label "SEO + AI visibility" audits to resellers — proof of the SKU.
- **Agent pipeline:** agents scrape Clutch/UpCity/agency SERPs (a few hundred identifiable buyers) → pre-build a sample report on one of the agency's real clients → tiny-volume personalized outreach → one close = 5–20 recurring location-reports → batch production monthly.
- **Grounded model:** 2–4 agencies closed by month 4–6 → 15–60 locations × $49–$99 = $700–$3,500/mo; month 12 base $2k–$6k/mo.
- **Honest weaknesses:** agencies may self-serve with Otterly/Peec agency plans; reliability expectations (one missed batch burns a whole account); buyer concentration; slower sales cycle.

### C3 — AI Visibility Index *(programmatic vertical/city directories + claim-your-listing)*

- **Offer:** free public "How AI recommends [vertical] in [city]" indexes, recomputed monthly from the audit corpus; monetized by featured placement / verified badge at $49–$149/mo.
- **Pricing evidence:** SaaSHub ~108 featured listings × $99–130/mo ≈ $10k+ MRR; scraped-data directory portfolios at $2,500+/mo (Frey Chu, 9–12 month ramp); job-board ceiling anchors $299/post (WWR, RemoteOK).
- **Agent pipeline:** Bright Data scrapes the business universe → GEO skill batch-scores → programmatic pages to Cloudflare Pages → monthly refresh → warm "you placed #4 — claim your profile" notifications → Stripe link to claimants.
- **Grounded model:** months 1–4 ≈ $0–$300; months 6–12: 10–40 featured × $49–$99 = $500–$3,900/mo. High variance — the honest base rate is John Rush's 30 AI-built directories → 10 ever monetized.
- **Honest weaknesses:** 3–6+ month SEO ramp; Google scaled-content-abuse exposure unless the score data is genuinely unique; credibility of a badge from a `pages.dev` site; claim-conversion at low traffic unproven.

### C4 — Bid Scout *(curated gov-RFP alerts + bid/no-bid briefs for one niche trade)*

- **Offer:** $59–$149/mo per firm: weekly matched federal/state/local bid opportunities plus a one-page agent-written "should you bid" brief (incumbent, past award prices from USAspending, set-aside status, effort estimate) — the analysis layer raw-alert incumbents don't include.
- **Pricing evidence:** Jorpex $49/$149/mo; BidSparq $249/mo; DemandStar $35–70/region; the adjacent grants market (GrantWatch $22–$249, Instrumentl $179–$499/mo) proves the curation-gap price band.
- **Agent pipeline:** SAM.gov + USAspending free APIs identify every small firm that has actually bid in a NAICS+state — pre-qualified buyers with public contact info → personalized outreach leading with a free sample brief on a live bid → weekly agent-run matching and brief-writing.
- **Grounded model:** months 1–2 build; 5–15 firms by month 4–6 (~$500–$1,500/mo); month 12 base 20–40 firms = $2k–$4k/mo.
- **Honest weaknesses:** crowded low end; brittle state/local portal scraping; implicit advice liability; niche-by-niche scaling; no-name trust barrier with conservative buyers.

### C5 — Public-Record Prospect Feeds *(verified niche lead lists from public records)*

- **Offer:** enriched, verified, scored lists at $199–$499/list (~$1–$3/row) — e.g., permit-active contractors, newly licensed businesses, firms failing a specific technical check — with monthly-refresh subscription upsell. Public records (permits, licenses, SAM registrations) sidestep the Google Maps/LinkedIn data-resale ToS problem.
- **Pricing evidence:** enriched-tier lists clear $1–$3/row between raw data (~$15/1,000) and content-syndication CPL ($40–$65); Fiverr incumbents sell 500 "verified leads" for ~$50 as the floor.
- **Agent pipeline:** open-data ETL (Socrata/ArcGIS permit portals, state registries) → Bright Data enrichment → scoring/verification methodology page → Fiverr gigs + direct micro-outreach to agencies.
- **Grounded model:** 1–3 month cold start; then 3–6 list sales/mo = $600–$2,000/mo; month 12 base $1k–$2.5k/mo.
- **Honest weaknesses:** adjacent to the most commoditized tier; buyers anchor to Apollo-free/$50-Fiverr prices; lists decay and are resellable; flat economics (no compounding).

---

## 5. Veritas council — stress-test results

Nine-member adversarial council: five lens critics attacked the candidates independently, a completeness critic audited what the whole process missed, and three independent judges (expected value / robustness / constraint fit) ruled on the critiqued field. Full record: `council/veritas-council.md`.

### Verdict matrix

| Lens | C1 Watchdog | C2 GEO Ledger | C3 Index | C4 Bid Scout | C5 Prospect Feeds |
|---|---|---|---|---|---|
| Market reality & pricing | weaken | weaken | **kill** | weaken | weaken |
| Zero-budget & tool reality | weaken | weaken | weaken | **hold** | weaken |
| Compliance & platform risk | weaken | hold | **kill** | **hold** | **kill** |
| Competition & defensibility | weaken | weaken | weaken | **hold** | weaken |
| Operational autonomy | weaken | weaken | weaken | kill *(as designed)*¹ | weaken |
| **Judges (3/3)** | **2nd** | **2nd–3rd** | **5th** | **WINNER** | **4th** |

¹ The autonomy critic killed C4 *as designed* (briefs shipping with zero human QC); all three judges explicitly overrode this to weaken-with-conditions, because the critic's own cross-cutting finding — no candidate satisfies strict autonomy, zero precedent exists — makes it a level effect, not a differential. C4's required human labor (2–6 hrs/week of schedulable brief QC) is the smallest in the set.

### What the critics established

**Pricing needs a "no-name discount."** Comps in the brief are list prices of established, branded vendors; an anonymous founder on a free subdomain clears 30–70% less. C1's audit clears $79–$149 (not $149–$299) against an industry whose funded competitors give the same report away free; C2's wholesale price inverts against Local Falcon's $24.99/mo self-serve AI-visibility tiers; C4 must price at $49–$79 against Jorpex's $49 AI-summarized alerts.

**The free tiers break specific designs, verifiably.** C1's "teaser scan in every cold email" would burn 40–80% of the entire Bright Data 5,000-request pool on prospects who never reply. C2 caps at ~20–25 white-label locations. C3's metro recompute alone can consume the whole pool. C4 is the exception: government data is free and keyless-generous, and its Gmail load is trivial. Critical discovery: **there is no lawful $0 way to programmatically sample ChatGPT at scale** (no free API; OpenAI ToS bans automated extraction; Bright Data's free tier covers ChatGPT/Perplexity answers only logged-out and non-personalized, with no Gemini scraper at all) — a structural problem for every GEO candidate's methodology claims.

**Compliance kills two candidates outright.** C3 (directory): its data source violates Google Maps ToS, its traffic plan sits in Google's scaled-content-abuse crosshairs, its paid-placement-inside-an-objective-index model matches the FTC's LendEDU precedent ($350k), and its notification motion is form spam. C5 (lead lists): public-record sourcing beats platform ToS but walks into data-broker law — California's DROP deletion-request enforcement went live **Aug 1, 2026**; registration fees break the $0 constraint and deletion-processing labor breaks the no-human constraint. C4 ranked highest survivability (open government data, no republication, minimal outreach); its residual tail is uninsured advice — mitigated by source-linked "verify before bidding" framing and E&O insurance once revenue allows. Also material: cold email from Gmail is CAN-SPAM-*lawful* but violates Gmail's own program policies at any volume — the channel is "tolerated until flagged," with a 15–25% estimated year-one suspension risk at C1's volumes (and far lower at C4's).

**No supply-side moat exists for anyone.** Verified: 411 "generative engine optimization" and 1,255 "AI visibility" GitHub repos created Jan–Aug 2026, several of them open-source Claude skills replicating the founder's audit asset — replication cost is `git clone`. Defensibility can only come from demand-side assets (relationships, brand, domain equity, longitudinal data), which the strict constraint set forbids or starves. C4 erodes slowest: unglamorous niche, conservative sticky buyers, and the binding constraint for any competitor is go-to-market grind, not technology.

**All five candidates are actually "founder-run with agent leverage."** Realistic founder hours at month-6 scale: C1 ≈ 8–15 hrs/week (sales threads, QC, deliverability management); C2 ≈ 3–6 plus on-call; C4 ≈ 2–6 (batch QC + replies) — the smallest and most schedulable. The constraint should be restated honestly: agents do ~95% of the work; the founder QCs deliverables, answers humans, and collects payment.

### What the completeness critic added

Strongest near-miss candidates dropped without disposition — worth revisiting after the winner is live: a **remediation/hygiene implementation SKU** (schema, entity consistency, citations into AI-cited sources — the one thing engine docs endorse, answering "nothing changed" churn); the **Local Visibility Retainer** (GBP + review-response management — the market-first angle's top pick, with the deepest purchase evidence in the whole sweep); **GBP suspension-reinstatement prep** (a Fiverr seller at $100/fix with 2,600+ reviews — arguably the strongest marketplace-verified willingness-to-pay datum found anywhere in this research); a **share-of-voice data product** (Exploding Topics model — one production run, unlimited buyers); and **Substack B2B data digests** as a low-tier delivery format for Bid Scout itself. Unpriced risks now priced into the plan: Claude-subscription usage caps as the compute substrate, Gmail *account* termination cascading into the founder's operating identity, payment-rail fragility for new accounts selling information services, the unmodeled sales conversation, and churn missing from every original revenue model. Evidence downgrades: the cold-email benchmarks are vendor-published (Smartlead's raw median is 0.83%), AEO Engine's MRR is self-reported and upmarket of the SMB tier, and Bright Data's "5,000/month, no card" carries an unresolved report that Gmail-only signups are gated. Process verdict: supply-side research strong; buyer-side evidence zero — **run a $0 smoke test before scaling anything.**

### The judges' ruling

**Unanimous: C4 Bid Scout, rescoped.** Consensus ranking C4 > C1 ≈ C2 > C5 > C3. Judges' consolidated income estimates (conservative-to-base monthly revenue):

| Candidate | Month 3 | Month 6 | Month 12 | Confidence |
|---|---|---|---|---|
| **C4 Bid Scout (rescoped)** | $0–$350 | $200–$900 | $400–$2,000 | medium |
| C1 Watchdog | $0–$400 | $100–$1,000 | $200–$1,500 | low–medium |
| C2 GEO Ledger | $0–$300 | $0–$1,000 | $0–$1,600 | low |
| C5 Prospect Feeds | $0–$150 | $50–$600 | $100–$1,000 | low–medium |
| C3 Index | $0–$50 | $0–$300 | $0–$700 | low–medium |

Notable: even C4's *salvage floor* (federal data-only alerts at $29–$49 if the analysis layer fails) exceeds the full expected value of C3 and C5. No two-candidate combination beat C4 solo — every pairing splits the one Gmail pipe and (for the GEO pair) contends for the same Bright Data pool.

---

## 6. The winner and why

**Bid Scout (rescoped): weekly federal-contract opportunity matching + source-linked bid/no-bid research briefs for small government contractors in one or two federal-heavy niches, at $49–$79/month per firm, with a $29–$49 data-only tier as the degradation floor.**

The judges' mandatory rescope, integrated:

1. **Federal-first, not state/local.** The data moat is federal-shaped: SAM.gov and USAspending are free, API-accessible, and legally clean; state/local portals are registration-gated with anti-bot ToS. Pick a federal-heavy NAICS niche (e.g., IT services/cybersecurity, professional services, facilities support with federal award history) — not janitorial/landscaping, whose bidding is mostly local. Add state coverage only from verified open-data portals, and never promise coverage the stack can't warrant.
2. **Price under the incumbent anchor.** Jorpex ships AI-summarized alerts at $49. The premium tier ($49–$79) is carried entirely by the brief layer: incumbent identification, past award prices, set-aside fit, effort estimate — each claim hyperlinked to the underlying federal record.
3. **Prospect what is actually public.** Bidder lists don't exist publicly (only awardees + offer counts). The reachable universe: SAM entity registrants by NAICS+state with public POC emails (excluding opted-out entities) plus USAspending past awardees. These are pre-qualified buyers — firms that verifiably participate in this market — reachable at ~100–300 personalized sends/month, far under the channel's danger zone.
4. **The hook is a free sample brief on a live bid** relevant to that specific firm — the council's consensus best outreach artifact across all five candidates: concrete, self-evidently valuable, and cheap to produce from data already in the pipeline.
5. **Honest framing is load-bearing.** Every brief is a "research brief — verify before bidding," with hyperlinked sources, no automated-vetting capability claims (the accessiBe/FTC pattern), no outcome guarantees, and AI-assistance disclosure. This is both the compliance posture and the trust posture for conservative buyers.
6. **One explicit constraint bend, accepted and bounded:** the founder QC-skims every unique brief before it ships (2–6 hrs/week). Deduplication means one hallucinated incumbent price would reach every subscriber in a niche simultaneously — zero-QC is not survivable, and no candidate on any design survives with literally zero human touch. This is the smallest, most schedulable bend available.

**Why it beat the GEO plays despite the founder's GEO asset:** the audit skill is genuinely good, but the council showed its market is the wrong shape for these constraints — the deliverable is the industry's free lead magnet, the buyer needs education the constraint forbids delivering (no calls), the methodology requires AI-engine sampling with no lawful $0 path at scale, and 400+ new competitors entered in eight months. Bid Scout's buyers already pay for exactly this SKU, its data is legally free forever, and nobody is rushing into unglamorous government-contracting niches. The GEO asset is not wasted — it remains the fallback (C1 as a modest audit shop) and powers several near-miss candidates worth testing later with revenue-funded infrastructure.

---

## 7. Implementation plan

### Phase 0 — Day 1–3: verify before building *(founder: ~1 hr; agents: the rest)*

The council flagged these as load-bearing unknowns; resolve them before any build:

- **SAM.gov API key tier:** register at SAM.gov, obtain a public API key, and measure the actual rate limit (reported ~10 requests/day for roleless personal keys vs ~1,000/day with a role — single-sourced; design batch pulls to fit whatever is measured). Each Opportunities call returns up to 1,000 records, so one niche+state fits even the low tier.
- **USAspending joins:** validate that award-history queries (incumbent, award amounts, IDV vs delivery-order) produce clean briefs for the chosen NAICS. Pick the niche where this data is densest.
- **Bright Data pool reality:** confirm the 5,000-request/month free tier activates on a Gmail signup (one report says some APIs gate until a card is added), and whether MCP requests and account credits are one pool. Bid Scout barely needs Bright Data, but the answer matters for the fallback stream.
- **Claude compute headroom:** estimate weekly brief volume (15–40 briefs/week at scale) against subscription usage caps; schedule production batches off-peak.
- **Niche selection (agents):** score 3–5 candidate NAICS niches by federal opportunity flow, small-business award share, average award size, and SAM registrant density with public POC emails. Founder picks one.

### Phase 1 — Weeks 1–2: build the pipeline *(agents ~95%)*

- **Ingest:** scheduled agent pulls new SAM.gov opportunities daily for the niche; USAspending enrichment per opportunity (incumbent, past awards, pricing history); dedupe and classify.
- **Match:** per-subscriber profile (NAICS, geography, set-asides, capacity) → relevance scoring. Onboarding intake is a simple form the agent parses; the founder sanity-checks each new profile once (set-aside nuance is a judgment call).
- **Brief generator:** one page per matched opportunity — summary, incumbent, past award prices (hyperlinked to the federal record), set-aside status, deadline, effort estimate, "verify before bidding" footer with AI disclosure.
- **Delivery:** weekly email per subscriber (Gmail; delivery volume is tens of sends/month) + a per-subscriber page on Cloudflare Pages. Embed native SAM.gov saved-search links in every issue so a failed automation week degrades visibly and gracefully.
- **Self-monitoring:** a scheduled check that verifies each weekly batch actually shipped (the council counted ~26 silent-failure windows by month 6; the founder must never be the last to know). Alert on missed batch, quota exhaustion, or OAuth expiry.
- **Payment:** Stripe Payment Links ($49–$79/mo subscription + $29–$49 data-only tier), written refund terms, real entity name, PayPal as backup rail (new accounts selling information services face holds — keep dispute rate near zero).

### Phase 2 — Weeks 3–8: the $0 smoke test *(the validation gate the council demanded)*

- Agents build the prospect list: SAM entity registrants + past awardees in the niche, public POC emails only, opted-out entities excluded.
- ~100–150 personalized sends total (well under Gmail's danger zone; 20–30/day max), each leading with a **free sample brief on a live, relevant bid** for that firm. CAN-SPAM complete: truthful headers, physical address, working unsubscribe with a zero-miss suppression list the agent maintains and the founder spot-checks.
- Founder handles reply threads (this is the sales conversation the constraint pretends away — budget 2–4 hrs/week) and sends payment links to closes.
- **Gate (end of month 2): ≥2 paying firms, or ≥5% positive-reply-to-paid conversion on 150+ sends.** Pass → Phase 3. Fail → switch niche once and re-test; fail twice → pivot to the C1 audit-shop fallback or the grant-digest variant of the same pipeline.

### Phase 3 — Months 3–12: scale and retention

- Grow within the channel budget: ~200–300 sends/month, compounding with referrals (ask every win; conservative niches run on word-of-mouth) and 3–5 testimonials as they accrue.
- **Churn instrumentation from client 1.** If monthly churn exceeds ~10–15%: add a retention artifact (win/loss recaps, quarterly pipeline review) and/or move churners to the $29–$49 data-only Substack digest tier (Substack's 10% cut is an allowed variable fee) before opening a second niche.
- Weekly rhythm at month-6 scale: agents produce everything; founder QC block (2–6 hrs — skim every unique brief against its linked sources), reply threads, payment links. Everything else is scheduled routines.
- Second niche only after the first is retention-stable and the QC block has headroom.

### Reinvestment ladder (first revenue dissolves the $0 ceilings, in this order)

1. **~$10/yr custom domain** + non-Gmail sending identity — fixes the no-name trust discount and the single-account outreach fragility (the council's highest-leverage upgrade).
2. **Bright Data pay-as-you-go** (~$1.50/1k requests) — removes the scraping cap for the fallback/expansion streams at ~$0.15–0.35 per client-month.
3. **E&O insurance (~$40–80/mo) once MRR clears ~$500** — covers the uninsured-advice tail the council named as the residual risk $0 cannot fix.
4. State/local portal accounts (manually registered, ToS-respecting) to widen coverage — the differentiation the $0 version can't warrant.

### Risk register (top 6, with mitigations)

| Risk | Likelihood | Mitigation |
|---|---|---|
| Hallucinated brief content reaching subscribers | Certain without QC | Founder pre-ship QC of every unique brief; every claim hyperlinked to its federal record; "verify before bidding" framing |
| Jorpex-class incumbents ship equivalent briefs | Moderate, ~12 mo | Price at/under anchor; niche depth (award-history context per firm) they won't build per-vertical; retention artifacts |
| Gmail account action from outreach | Low at ≤300/mo, personalized B2B | Volume discipline, suppression hygiene, move sending to custom domain at first revenue |
| Silent pipeline failure before a weekly send | High over 6 mo without monitoring | Self-checking routine + visible SAM saved-search links as graceful degradation |
| Churn from irrelevant matches | Moderate | Founder-reviewed onboarding profiles; match-quality feedback loop; down-tier instead of losing subscribers |
| Payment-rail hold/termination | Low–moderate | Real entity, clear terms, near-zero disputes, PayPal backup |

### What NOT to do (council-mandated)

- No "AI-powered passive income" marketing, ever (active FTC enforcement target).
- No automated-vetting capability claims ("our AI decides which bids you'll win") — accessiBe pattern.
- No scraping of registration-gated state/local portals; no coverage promises beyond verified sources.
- No unreviewed briefs, no undisclosed bots in commercial conversations, no free-ESP cold email.
- Don't run a second candidate's outreach through the same Gmail pipe while Bid Scout is validating.

---

## 8. Compliance guardrails (non-negotiable)

Drawn from the evidence sweep's legal findings; these are cheap to follow and expensive to ignore:

1. **CAN-SPAM on every send:** truthful headers/subject, identification as commercial, physical postal address, working unsubscribe honored promptly. Volume stays at 20–30/day per inbox.
2. **Never use free ESP tiers for cold email** — their ToS ban it and enforcement is account termination.
3. **Disclose the bot.** CA B.O.T. Act, Utah AIPA, and EU AI Act Art. 50 (applicable since 2026-08-02) variously require disclosure of automated agents in commercial interactions; disclosure is a complete safe harbor and costs nothing. A simple "this report/message was prepared by our automated analysis system and reviewed on request" line suffices in most flows.
4. **Never market "AI passive income" or guaranteed results** — that exact framing is an active FTC enforcement target (Operation AI Comply). Sell measurement and monitoring, never ranking guarantees (C-SEO Bench shows GEO tactics are unreliable; ~95% of citation behavior is unexplained).
5. **Public data only.** No login-gated scraping; respect Bright Data's public-data policy; prefer government/open-data sources for anything resold; no Google Maps data resale as a product.
6. **Marketplace honesty:** Fiverr permits AI-generated deliverables only when customized per order; the account is identity-bound and non-replaceable — never bulk-deliver identical reports.
7. **FTC review rules:** no fake/incentivized reviews, no review gating, in any reputation-adjacent service.

---

## 9. Appendices

- `evidence/evidence-sweep.md` — 13-agent evidence sweep: free-tier limits, market pricing, demand signals, precedents (all key numbers with sources, confidence, and as-of dates).
- `evidence/idea-funnel.md` — 5-angle ideation results (~30 candidate ideas with price-point evidence).
- `council/veritas-council.md` — full council critiques and judge rulings.
