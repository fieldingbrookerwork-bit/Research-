# Outreach batch — 2026-09-03

**NOTHING IN THIS FOLDER HAS BEEN SENT. Agents draft; the founder sends.**

Supersedes `state/outreach/2026-08-30/`, which is now STALE — four days passed and
four of the seven notices it was built on fell under the 10-day response bar. Do not
send anything from that folder. This batch was rebuilt against a fresh SAM pull.

## Before you send anything

1. **Fill `[POSTAL_ADDRESS]`** in every draft. CAN-SPAM requires a real physical
   postal address in every commercial email. This is the one hard legal gate.
2. **Fill `[FOUNDER_NAME]` and `[FOUNDER_EMAIL]`.**
3. **Look up each recipient's email.** Every `to:` line reads
   `[EMAIL — look up on sam.gov entity search]`. **No contact address was known to
   this session and none was invented.**
4. **Send from your own inbox, 20–30/day maximum.** This batch is 18 — one day's send.
5. **Stop immediately if any recipient objects**, and add every opt-out to
   `state/suppression.json` the same day.
6. Fill `sent_at:` below when you actually send.

## Finding each firm's POC email — use the UEI, never the name

Each row below carries the firm's **UEI**, taken from USAspending's `Recipient UEI`
on the award actually cited in that firm's brief. Go straight to
`https://sam.gov/entity/<UEI>/coreData` — that is an exact record, no searching.

**Do not search SAM by company name.** Measured this run: a name search returns 2–3
registrations for most of these firms, and taking the first was WRONG for 3 of the 8
tried. One of those namesakes had a registration that lapsed in 2018 — matching on
name would have told you a live prospect was defunct. The UEI is the only safe key.

Then: **Entity Information → Points of Contact → Electronic Business POC.**

- **Respect opt-outs.** If the entity has restricted public display, SKIP the firm and
  add it to `state/suppression.json`. Do not work around it.
- **If no public POC email is exposed, SKIP the firm.** Do not substitute a guessed
  address, an `info@`/`sales@` pattern, or a LinkedIn contact.

The SAM Entity API (which this session can call) returns UEI, registration status and
POC **names**, but **not POC email** — that sits behind SAM's FOUO tier, which a
standard API key does not reach. So the email is the one field that stays manual.

## The batch

| # | Firm | Draft | Opportunity | Set-aside | Days | UEI (open sam.gov/entity/UEI/coreData) | SAM reg. | POC name | sent_at |
|---|------|-------|-------------|-----------|------|------|------|------|---------|
| 1 | AATD LLC | `sample-aatd-llc.md` | 205AE9-26-Q-00053 | Small Business (total) | 11 | X76KEVV61AM9 | not yet checked | — | |
| 2 | ACCESSAGILITY LLC | `sample-accessagility-llc.md` | 19AQMM26R0250 | Small Business (total) | 14 | HMXCQJ8ADNL7 | Active (exp 2027-05-04) | Zaib Kaleem | |
| 3 | BLUE TECH INC. | `sample-blue-tech-inc.md` | 205AE9-26-Q-00053 | Small Business (total) | 11 | MDC5LDZKQAM4 | not yet checked | — | |
| 4 | COLOSSAL CONTRACTING LLC | `sample-colossal-contracting-llc.md` | 205AE9-26-Q-00053 | Small Business (total) | 11 | F4M9NB1HD785 | not yet checked | — | |
| 5 | COUNTERTRADE PRODUCTS, INC. | `sample-countertrade-products--inc.md` | 19AQMM26R0250 | Small Business (total) | 14 | CN4KSKX2UQY5 | not yet checked | — | |
| 6 | CSP ENTERPRISES, LLC | `sample-csp-enterprises--llc.md` | 19AQMM26R0250 | Small Business (total) | 14 | GJJRGECWBFK9 | Active (exp 2027-08-31) | Brian Vesper | |
| 7 | CYNERGY PROFESSIONAL SYSTEMS LLC | `sample-cynergy-professional-systems-llc.md` | 205AE9-26-Q-00053 | Small Business (total) | 11 | GK55J77VGN84 | not yet checked | — | |
| 8 | DISYS SOLUTIONS, INC. | `sample-disys-solutions--inc.md` | 205AE9-26-Q-00053 | Small Business (total) | 11 | R15MK4RSWRD3 | not yet checked | — | |
| 9 | ENTERPRISE TECHNOLOGY SOLUTIONS, INC. | `sample-enterprise-technology-solutions--inc.md` | CORHQ-26-Q-0317 | none stated ("No Set aside used") | 10 | FBRMCGPMN963 | not yet checked | — | |
| 10 | GOVERNMENT ACQUISITIONS LLC | `sample-government-acquisitions-llc.md` | 19AQMM26R0250 | Small Business (total) | 14 | R98MW4ZKUUK3 | Active (exp 2027-07-24) | Todd Brown | |
| 11 | IMPRES TECHNOLOGY SOLUTIONS, INC | `sample-impres-technology-solutions--inc.md` | 19AQMM26R0250 | Small Business (total) | 14 | MSSQQ551LG41 | Active (exp 2027-03-02) | Richard Fu | |
| 12 | METGREEN SOLUTIONS INC | `sample-metgreen-solutions-inc.md` | 28321326RI0000041 | BLANK field | 25 | J4TDZHLCUGW3 | not yet checked | — | |
| 13 | PANAMERICA COMPUTERS, INC. | `sample-panamerica-computers--inc.md` | 19AQMM26R0250 | Small Business (total) | 14 | DPQEDJ6CXZM5 | not yet checked | — | |
| 14 | SDVO SOLUTIONS, LLC | `sample-sdvo-solutions--llc.md` | 475671 | SDVOSB (FAR 19.14) | 14 | KL7DMG4LKFM5 | Active (exp 2027-08-26) | Vinnie Ahearn | |
| 15 | SOFTWARE INFORMATION RESOURCE CORP. | `sample-software-information-resource-corp.md` | CORHQ-26-Q-0317 | none stated ("No Set aside used") | 10 | EJJMMJHYDFH6 | not yet checked | — | |
| 16 | STANDARD-BLAZAR, LLC | `sample-standard-blazar--llc.md` | 205AE9-26-Q-00053 | Small Business (total) | 11 | DZ9XM5UDFN29 | not yet checked | — | |
| 17 | STERLING COMPUTERS CORPORATION | `sample-sterling-computers-corporation.md` | 19AQMM26R0250 | Small Business (total) | 14 | YZTLALWM4UC7 | not yet checked | — | |
| 18 | SWISH DATA CORPORATION | `sample-swish-data-corporation.md` | 28321326RI0000041 | BLANK field | 25 | DMERLBE3JR53 | not yet checked | — | |

`SAM reg.` is filled only where the record was retrieved **by UEI** and came back with
that same UEI. Rows reading *not yet checked* are unknown — today's SAM request budget
(10/day) ran out. Unknown is NOT a reason to skip a firm.

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
