# Outreach batch — 2026-09-03

**NOTHING IN THIS FOLDER HAS BEEN SENT. Agents draft; the founder sends.**

Supersedes `state/outreach/2026-08-30/`, which is now STALE — four days passed and
four of the seven notices it was built on fell under the 10-day response bar. Do not
send anything from that folder. This batch was rebuilt against a fresh SAM pull.

## Before you send anything

1. **Fill `[POSTAL_ADDRESS]`** in every draft. CAN-SPAM requires a real physical
   postal address in every commercial email. This is the one hard legal gate.
2. **Fill `[FOUNDER_NAME]` and `[FOUNDER_EMAIL]`.**
3. **Recipient addresses are now filled in below.** 17 of 18 firms have a VERIFIED
   PUBLISHED address recorded in `contacts.json` with its source URL; 1 (AATD LLC) is
   SKIP because nothing is published. **No address was invented or pattern-guessed.**
   The `to:` line in each draft still reads `[EMAIL — look up ...]` — copy the address
   from the table below when you send. Drafts were not modified.
4. **Send from your own inbox, 20–30/day maximum.** 17 sendable — one day's send.
5. **Stop immediately if any recipient objects**, and add every opt-out to
   `state/suppression.json` the same day.
6. Fill `sent_at:` below when you actually send.

## How each address was verified — read this before trusting the table

Every address in the table was **seen published** at the recorded source URL. None was
inferred from a name/domain pattern. Full records, including alternates and caveats, are
in `contacts.json` next to this file.

Identity was pinned by **UEI**, never by name, in one of two ways:

- **UEI printed on the same page as the address.** Strongest. True for SWISH DATA,
  SDVO SOLUTIONS (both print their UEI on their own contact page), and for COLOSSAL,
  COUNTERTRADE and PANAMERICA via NITAAC GWAC contract-holder pages.
- **SAM physical address for the UEI matches the address printed beside the email.**
  Used for the rest. Every match was exact, street and suite.

`state/suppression.json` was checked: it is empty. Nothing here is suppressed.

**Three addresses (Colossal, CounterTrade, PanAmerica) come from `nitaac.nih.gov`
contract-holder pages, not the firms' own sites.** Those pages print the firm's SAM UEI
next to a named program manager, which is better identity proof than a company contact
page — but it is a different source class, so it is called out here rather than buried.
Colossal and PanAmerica also have an own-site alternate in `contacts.json`.
**CounterTrade's own site returns HTTP 403 to every automated request, so no address on
countertrade.com was actually seen.** Third parties claim `info@countertrade.com` is on
their contact page; that is unverified and deliberately not recorded. Open
`https://countertrade.com/contact-us/` in a browser if you want an own-site address.

### The one SKIP

**AATD LLC (X76KEVV61AM9)** — `aatd-llc.com/contact-us/` publishes a web form, a phone
number and a postal address, and no email address anywhere on the site. GSA eLibrary's
POC for their schedule is a GSA employee, not the firm. GSA Advantage's price list PDF
has no extractable address. Nothing published, so nothing usable. Separately, HigherGov
shows AATD at roughly $173M in federal obligations — far above this project's $5M
small-firm ceiling — so it is likely not a prospect regardless.

## The batch

| # | Firm | Draft | Opportunity | Days | UEI | Address to send to | Type | Source (seen published here) | sent_at |
|---|------|-------|-------------|------|-----|--------------------|------|------------------------------|---------|
| 1 | AATD LLC ⚠ scale | `sample-aatd-llc.md` | 205AE9-26-Q-00053 | 11 | X76KEVV61AM9 | **SKIP** — none published | — | `aatd-llc.com/contact-us/ (form only)` | |
| 2 | ACCESSAGILITY LLC | `sample-accessagility-llc.md` | 19AQMM26R0250 | 14 | HMXCQJ8ADNL7 | sewp@accessagility.com | role (Zaib Kaleem, PM) | `accessagility.com/sewp` | |
| 3 | BLUE TECH INC. | `sample-blue-tech-inc.md` | 205AE9-26-Q-00053 | 11 | MDC5LDZKQAM4 | info@bluetech.com | generic | `bluetech.com/contact/` | |
| 4 | COLOSSAL CONTRACTING LLC | `sample-colossal-contracting-llc.md` | 205AE9-26-Q-00053 | 11 | F4M9NB1HD785 | danv@colossal-llc.com | named (Dan Via, PM) | `nitaac.nih.gov/gwacs/cio-sp3-small-business/contract-holder/colossal-contracting-llc` | |
| 5 | COUNTERTRADE PRODUCTS, INC. | `sample-countertrade-products--inc.md` | 19AQMM26R0250 | 14 | CN4KSKX2UQY5 | adumm@countertrade.com | named (Angela Dumm, PM) | `nitaac.nih.gov/gwacs/cio-cs/contract-holder/countertrade-products-inc` | |
| 6 | CSP ENTERPRISES, LLC | `sample-csp-enterprises--llc.md` | 19AQMM26R0250 | 14 | GJJRGECWBFK9 | TeamBox@cspenterprises.com | role | `cspenterprises.com/contact` | |
| 7 | CYNERGY PROFESSIONAL SYSTEMS LLC ⚠ excluded by filter | `sample-cynergy-professional-systems-llc.md` | 205AE9-26-Q-00053 | 11 | GK55J77VGN84 | info@cynergy.pro | generic | `cynergy.pro/contact/` | |
| 8 | DISYS SOLUTIONS, INC. ⚠ SAM exp 09-08 | `sample-disys-solutions--inc.md` | 205AE9-26-Q-00053 | 11 | R15MK4RSWRD3 | sales@dsitech.com | role | `dsitech.com/contact/` | |
| 9 | ENTERPRISE TECHNOLOGY SOLUTIONS, INC. | `sample-enterprise-technology-solutions--inc.md` | CORHQ-26-Q-0317 | 10 | FBRMCGPMN963 | info@etsig.com | generic | `etsig.com/contact` | |
| 10 | GOVERNMENT ACQUISITIONS LLC | `sample-government-acquisitions-llc.md` | 19AQMM26R0250 | 14 | R98MW4ZKUUK3 | sales@gov-acq.com | role | `gov-acq.com/contact/` | |
| 11 | IMPRES TECHNOLOGY SOLUTIONS, INC ⚠ scale | `sample-impres-technology-solutions--inc.md` | 19AQMM26R0250 | 14 | MSSQQ551LG41 | civ@imprestechnology.com | role (civilian sales) | `imprestechnology.com/contact-us/` | |
| 12 | METGREEN SOLUTIONS INC | `sample-metgreen-solutions-inc.md` | 28321326RI0000041 | 25 | J4TDZHLCUGW3 | info@metgreensolutions.com | generic | `metgreensolutions.com/contact-us` | |
| 13 | PANAMERICA COMPUTERS, INC. | `sample-panamerica-computers--inc.md` | 19AQMM26R0250 | 14 | DPQEDJ6CXZM5 | mshaffer@pcitec.com | named (Michael Shaffer, PM) | `nitaac.nih.gov/gwacs/cio-cs/contract-holder/panamerica-computers-inc` | |
| 14 | SDVO SOLUTIONS, LLC | `sample-sdvo-solutions--llc.md` | 475671 | 14 | KL7DMG4LKFM5 | Inquiries@sdvosolutions.com | role | `sdvosolutions.com/contact` | |
| 15 | SOFTWARE INFORMATION RESOURCE CORP. | `sample-software-information-resource-corp.md` | CORHQ-26-Q-0317 | 10 | EJJMMJHYDFH6 | info@sirc.net | generic | `sirc.net/contact-us/` | |
| 16 | STANDARD-BLAZAR, LLC ⚠ joint venture | `sample-standard-blazar--llc.md` | 205AE9-26-Q-00053 | 11 | DZ9XM5UDFN29 | info@sbllc.com | generic | `sbllc.com/` | |
| 17 | STERLING COMPUTERS CORPORATION ⚠ scale | `sample-sterling-computers-corporation.md` | 19AQMM26R0250 | 14 | YZTLALWM4UC7 | connect@sterling.com | generic | `sterling.com/contact/` | |
| 18 | SWISH DATA CORPORATION | `sample-swish-data-corporation.md` | 28321326RI0000041 | 25 | DMERLBE3JR53 | info@swishdata.com | generic | `swishdata.com/contact-us/` | |

⚠ marks a firm whose fitness is in doubt on the evidence found while looking up its
address — see **Prospect-quality flags** below and the `prospect_concern` field in
`contacts.json`. The set-aside and SAM-registration columns were dropped from this table
to make room for the address; both are unchanged and still recorded in the sections
below and in `contacts.json`.

## Prospect-quality flags — found while looking up addresses

Six firms in this batch look like poor prospects on the evidence seen. This is worth as
much as the addresses; none of it was known when the batch was built.

- **CYNERGY PROFESSIONAL SYSTEMS LLC — should not be in this batch.** It is the only one
  of the 18 that this project's own prospect filter already **excluded**, under
  `R1_ABOVE_SCALE_CEILING`: $39,059,824 in NAICS 541519 obligations against a $5M
  ceiling. Both of its scanned awards are radios, not IT services — "MOBILE TACTICAL
  COMMUNICATION RADIOS AND BATTERIES FOR ICE AGENTS" ($39.0M, DHS/ICE) and "MOTOROLA
  DUPLEX AND PARTS" ($11K, State) — and its evidence record has zero IT and zero
  services markers. Something let an excluded firm through into drafting; that is a
  pipeline bug, not just a bad row.
- **STERLING COMPUTERS CORPORATION — out of segment.** Large national federal reseller;
  SAM records its primary NAICS as 334111 (computer manufacturing), not 541519. It
  entered on a $665K sliver of 541519 activity. Runs its own capture function.
- **IMPRES TECHNOLOGY SOLUTIONS — likely too big.** Public profiles for UEI
  MSSQQ551LG41 show ~$68.4M in federal obligations across 309 awards, ~$45M revenue,
  ~106 employees. It slipped under the $5M ceiling only because the filter scans NAICS
  541519 alone and saw $490,698.
- **AATD LLC — likely too big, and unmailable.** ~$173M in obligations per HigherGov,
  mostly VA. Already SKIP for lack of a published address.
- **STANDARD-BLAZAR, LLC — a joint venture, not an operating firm.** SBA registers it as
  a "Small Business Joint Venture" / "Veteran Joint Venture". JVs are stood up per
  pursuit; the buying decision sits with the parents. Its site also markets VA/VHA
  healthcare-IT sustainment while its awards are Cribl/Illumio security software for
  CPSC/DOE/DHS.
- **DISYS SOLUTIONS, INC. — timing, not fitness.** SAM registration for UEI
  R15MK4RSWRD3 expires **2026-09-08**, tomorrow. Send today or re-check first.

The scale ceiling is measured on NAICS 541519 obligations alone, so it systematically
understates firm size and lets large resellers through. Three of the six flags above are
that same hole. Worth fixing in the filter before the next batch.

## Two firms were dropped from the previous batch

- **BLUE RASTER L.L.C.** — paired with the EPA Region 9 GIS call order, now 7.2 days
  out. No GIS notice is currently open with 10+ days, and no other open notice fits a
  geospatial firm. Re-pair them when one appears rather than forcing a bad match.
- **MINBURN TECHNOLOGY GROUP, LLC** — paired with the VA hands-free clinical
  communication notice, now 5.9 days out. Same reasoning.

## Supply, stated plainly

A 30-day SAM pull of NAICS 541519 returned 108 notices. **11 distinct solicitations are
open with 10+ days; only 3 carry a small-business set-aside.** 14 of these 18 drafts
sit on a set-aside notice, which is the most the supply allows. Several firms share an
opportunity — unavoidable, and not a problem in itself (SAM.gov is public), but you are
introducing competitors to each other.

## Known weaknesses — read before sending

- **4 of 18 drafts sit on a notice with no small-business set-aside** (2 FDIC/Copado,
  2 SSA AI Strategy). Those firms compete against companies of any size.
- **The SSA notice has a BLANK set-aside field, not a stated 'none'.** The briefs say
  explicitly that blank is not confirmation of full-and-open. Do not read it as one.
- **The SDVOSB draft (SDVO SOLUTIONS, LLC) assumes nothing about their certification.**
  Their eligibility is a question in the brief, not a claim.
- **The IRS notice is a master IDIQ**, not a single job. The brief says so and asks
  about ceiling, guaranteed minimum, and number of awards — the three numbers that
  decide whether an IDIQ pursuit is worth anything.
- **`latest_award` in the prospect data is a period-of-performance start date**, not an
  award date. Used nowhere in these drafts, and must not be.

## Compliance checks run on every draft

- No URLs anywhere (asserted programmatically). Federal records cited by solicitation
  number, SAM notice ID and USAspending award ID.
- No attachments; sample brief inline as plain text.
- Reply-to-inbox call to action. Truthful subject. No 'Re:', no urgency.
- AI-assistance disclosure once in the message, once in the brief footer.
- Body word count 130–151 (skill limit 110–160).
- Zero banned-list tokens across all briefs and drafts.
