# AI-Subagent Income Streams — Research Report

**Date:** 2026-08-26
**Question:** Which monthly income streams can run almost entirely on AI sub-agents (prospecting, research, production, outreach), spending nothing (free tiers only), where the only human step is the founder collecting payment from a willing buyer?
**Method:** 27 research agents in three waves — a 13-agent evidence sweep (free-tier limits, market pricing, demand, precedents), a 5-agent idea funnel (independent ideation angles), and a 9-agent Veritas council (5 adversarial lens critics + 1 completeness critic + 3 independent judges) — plus synthesis. Every load-bearing number carries a source and an as-of date; see `evidence/`.

> **Honesty note on sources:** the research environment could not open many commercial pricing pages directly (network egress restrictions). Figures marked in `evidence/evidence-sweep.md` as search-mediated snapshots of official pages should each be re-verified live before money decisions. Nothing below rests on a single unverifiable source.

---

## 1. Executive summary

*(final verdict — see section 6/7)*

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

*(placeholder — council in session)*

---

## 6. The winner and why

*(placeholder)*

---

## 7. Implementation plan

*(placeholder)*

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
