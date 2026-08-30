# Outreach batch — 2026-08-30

**NOTHING IN THIS FOLDER HAS BEEN SENT. Agents draft; the founder sends.**

## Before you send anything

1. **Fill `[POSTAL_ADDRESS]`** in every draft. CAN-SPAM requires a real physical
   postal address in every commercial email. This is the one hard legal gate.
2. **Fill `[FOUNDER_NAME]` and `[FOUNDER_EMAIL]`.** Both are placeholders in every
   draft; `site/index.html` still carries `[FOUNDER_EMAIL]` too.
3. **Look up each recipient's email** (procedure below). The `to:` line of every
   draft reads `[EMAIL — look up on sam.gov entity search]`. **No contact address
   was known to this session and none was invented.** Do not guess one.
4. **Send from your own inbox, 20–30/day maximum.** This batch is 20 — one day's
   sending. One touch per firm; no follow-up sequence is drafted.
5. **Stop immediately if any recipient objects**, and add every opt-out to
   `state/suppression.json` the same day, before the next batch is drafted.
6. Fill the `sent_at:` field in the table below when you actually send.

## How to find each firm's public POC email on SAM.gov

SAM.gov entity search is public and needs no login for the basic record; a free
account is needed to see some POC fields. For each firm:

1. Go to **sam.gov** → **Search** → set the domain filter to **Entity Information**
   (not Contract Opportunities).
2. Search the **exact legal name** in the table below. If the name returns nothing,
   search the **award ID** on **USAspending.gov** first, open the award, and copy the
   recipient's **UEI** from the award page — then search that UEI on SAM.gov. The UEI
   is the reliable key; legal names in USAspending are not always SAM's spelling.
3. Open the entity record → **Entity Information** → **Points of Contact**. Use the
   **Electronic Business POC** (that is the contracting-facing mailbox), not the
   Government Business POC's personal line if a shared mailbox is offered.
4. **Respect opt-outs.** If the record shows the entity has restricted public display
   of its information, **skip the firm** and add it to `state/suppression.json`. Do
   not work around a suppressed record.
5. If no public POC email is exposed, **skip the firm**. Do not substitute a guessed
   address, a `info@`/`sales@` pattern, or a LinkedIn contact.

UEIs were **not** available to this session: the USAspending fields this pipeline
collects (`normalize_award`) do not include recipient UEI, so the award ID below is
the lookup key. That is a known gap, not an omission by choice.

## The batch

| # | Firm | Draft | Opportunity | Set-aside | Days out | Award ID (lookup key) | Suppression | sent_at |
|---|------|-------|-------------|-----------|----------|----------------------|-------------|---------|
| 1 | AATD LLC | `sample-aatd-llc.md` | FA480026Q0082 | Small Business (total) | 12 | 36C10B26F0285 | clear (no suppression entries match) | |
| 2 | ACCESSAGILITY LLC | `sample-accessagility-llc.md` | 19AQMM26R0250 | Small Business (total) | 18 | 1331L526P13OS0053 | clear (no suppression entries match) | |
| 3 | BLUE RASTER L.L.C. | `sample-blue-raster-l-l-c.md` | 68HE0926Q0036 | BLANK field | 11 | 1232SA26F0547 | clear (no suppression entries match) | |
| 4 | BLUE TECH INC. | `sample-blue-tech-inc.md` | FA480026Q0082 | Small Business (total) | 12 | 70FA3026P00000035 | clear (no suppression entries match) | |
| 5 | COLOSSAL CONTRACTING LLC | `sample-colossal-contracting-llc.md` | FA480026Q0082 | Small Business (total) | 12 | 1331L526F13OS1227 | clear (no suppression entries match) | |
| 6 | COUNTERTRADE PRODUCTS, INC. | `sample-countertrade-products--inc.md` | 19AQMM26R0250 | Small Business (total) | 18 | 15F06726F0001374 | clear (no suppression entries match) | |
| 7 | CSP ENTERPRISES, LLC | `sample-csp-enterprises--llc.md` | 19AQMM26R0250 | Small Business (total) | 18 | 1331L526F0353 | clear (no suppression entries match) | |
| 8 | CYNERGY PROFESSIONAL SYSTEMS LLC | `sample-cynergy-professional-systems-llc.md` | FA480026Q0082 | Small Business (total) | 12 | 15F06726F0001244 | clear (no suppression entries match) | |
| 9 | DISYS SOLUTIONS, INC. | `sample-disys-solutions--inc.md` | FA480026Q0082 | Small Business (total) | 12 | 140P5426F0013 | clear (no suppression entries match) | |
| 10 | ENTERPRISE TECHNOLOGY SOLUTIONS, INC. | `sample-enterprise-technology-solutions--inc.md` | CORHQ-26-Q-0317 | none stated ("No Set aside used") | 15 | 28321326FDX030123 | clear (no suppression entries match) | |
| 11 | GOVERNMENT ACQUISITIONS LLC | `sample-government-acquisitions-llc.md` | 19AQMM26R0250 | Small Business (total) | 18 | 19AQMA26F0544 | clear (no suppression entries match) | |
| 12 | IMPRES TECHNOLOGY SOLUTIONS, INC | `sample-impres-technology-solutions--inc.md` | 19AQMM26R0250 | Small Business (total) | 18 | 1331L526F0362 | clear (no suppression entries match) | |
| 13 | METGREEN SOLUTIONS INC | `sample-metgreen-solutions-inc.md` | 28321326RI0000041 | BLANK field | 29 | 89243326FFE400802 | clear (no suppression entries match) | |
| 14 | MINBURN TECHNOLOGY GROUP, LLC | `sample-minburn-technology-group--llc.md` | 36C25226R0071 | BLANK field | 10 | 36C26226F0388 | clear (no suppression entries match) | |
| 15 | PANAMERICA COMPUTERS, INC. | `sample-panamerica-computers--inc.md` | 19AQMM26R0250 | Small Business (total) | 18 | 80NSSC26FA713 | clear (no suppression entries match) | |
| 16 | SDVO SOLUTIONS, LLC | `sample-sdvo-solutions--llc.md` | FA488726Q0058 | SDVOSB (FAR 19.14) | 11 | 63NLRB26F0072 | clear (no suppression entries match) | |
| 17 | SOFTWARE INFORMATION RESOURCE CORP. | `sample-software-information-resource-corp.md` | CORHQ-26-Q-0317 | none stated ("No Set aside used") | 15 | 1331L526F0387 | clear (no suppression entries match) | |
| 18 | STANDARD-BLAZAR, LLC | `sample-standard-blazar--llc.md` | FA480026Q0082 | Small Business (total) | 12 | 70B02C26F00000650 | clear (no suppression entries match) | |
| 19 | STERLING COMPUTERS CORPORATION | `sample-sterling-computers-corporation.md` | 19AQMM26R0250 | Small Business (total) | 18 | 140D0426F0976 | clear (no suppression entries match) | |
| 20 | SWISH DATA CORPORATION | `sample-swish-data-corporation.md` | 28321326RI0000041 | BLANK field | 29 | 7571TE26F80249 | clear (no suppression entries match) | |

## Suppression check

`state/suppression.json` read at draft time: {"emails": [], "domains": []}

It is empty, so no firm was skipped. Because no contact addresses are known yet, the
check was run against **firm names** rather than addresses — it will have to be re-run
against the actual email addresses once you have looked them up, before sending.

## How these 20 were chosen

Source list: `state/prospects-541519-filtered.json` (100 kept of 121 raw awardees;
21 excluded with a recorded rule and evidence — audit them there before trusting this
list). These 20 are the highest-fitness kept firms whose federal award record plausibly
matches one of the few currently-open opportunities.

**Supply, stated plainly:** a 45-day SAM ingest of NAICS 541519 returned 119 notices.
Only 14 are open with 10+ days to respond, and only **3 distinct solicitations** carry
a small-business set-aside. 14 of these 20 drafts therefore sit on a set-aside notice;
the other 6 sit on notices whose set-aside field is blank or states none. Several firms
share the same opportunity — unavoidable at this supply, and not a problem in itself
(SAM.gov is public), but be aware you are introducing competitors to each other.

## Known weaknesses in this batch — read before sending

- **6 of 20 drafts are built on a notice with no small-business set-aside.** Those
  firms would be competing against companies of any size. The brief says so; make sure
  you are comfortable leading with it.
- **3 of the 7 notices have a BLANK set-aside field, not a stated 'none'.** Every brief
  says explicitly that blank is not confirmation of full-and-open. Do not let anyone
  read it as one.
- **The SDVOSB draft (SDVO SOLUTIONS, LLC) assumes nothing about their certification.**
  Their eligibility is a question in the brief, not a claim. Their name suggests SDVOSB
  status; that was never verified and must not be asserted.
- **'Candidate related awards' on the two FDIC/Copado drafts are weak matches.** They
  come from a title-overlap heuristic that fired on generic words ('software',
  'subscription', 'renewal'). The label says heuristic; the founder should decide
  whether showing them helps or hurts.
- **`latest_award` in the prospect data is a period-of-performance start date, not an
  award date**, and is frequently in the future. It is not used anywhere in these
  drafts, and must not be.

## Compliance checks run on every draft

- No URLs anywhere in any draft (asserted programmatically; the batch generator fails
  if a `http://`, `https://` or `www.` appears). Federal records are cited by
  solicitation number, SAM notice ID and USAspending award ID instead.
- No attachments. The sample brief is inline plain text.
- Call to action is a reply to the founder's inbox. No click, no website reference.
- Truthful subject line naming the solicitation and the firm. No 'Re:', no urgency.
- AI-assistance disclosure appears once in the message and once in the brief footer.
- Message body word count 130–145 (skill limit 110–160).
- Verify-before-bidding line and AI disclosure present in every inline brief.
