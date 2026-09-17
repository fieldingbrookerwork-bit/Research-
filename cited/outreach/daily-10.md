# The daily ten — operating procedure

Standing cadence: **10 new prospects a day, using `scripts/cold-email-v2.md`,
starting now.** Do not wait for the October infrastructure. This runs from the
personal Gmail in the meantime.

## The volume math nobody expects

v2 has four touches. 10 new prospects a day means that by week three you are
also sending three days' worth of follow-ups every day:

| | new | touch 2 | touch 3 | touch 4 | total/day |
|---|---|---|---|---|---|
| Full sequence | 10 | 10 | 10 | 10 | **40** |
| Two touches | 10 | 10 | — | — | **20** |

40 cold sends a day from a consumer Gmail is the number that gets that account
restricted, and that account is also your Anthropic, Namecheap, Cloudflare and
Airwallex login.

**So until the new domains come online: 10 new + touch 2 only. 20/day total.**
Touch 2 is the highest-yield follow-up anyway, so this keeps most of the lift.
Add touches 3 and 4 on October 20 when the 12 mailboxes take over.

## Why ten is the right number right now

Each v2 email needs a real audit behind it: run the assistant queries for that
city and trade, log who got named, pull their name/address/phone/hours/founding
claims off their site, Google Business Profile, Yelp and BBB, and find the
conflict. That is 15-25 minutes of honest work.

Ten a day is 2.5 to 4 hours. That is the most one person can do without the
research going shallow, and shallow research is what turns v2 back into a
generic email. Ten specific emails beat forty vague ones. This is not a
placeholder number, it is the correct number until the audit pipeline exists.

## The daily loop

**1. Source ten (15 min).**
One trade, one metro per day. Rotating on one metro builds the density you need
for the "I checked 40 companies in your city" post.

**2. Verify the addresses before anything else (5 min).**
Two of the first 25 hard-bounced. `woodsplumbingaz.com` did not resolve at all.
Check the domain resolves and the address is actually published on their own
site. Never guess `info@`. If nothing is published, drop the prospect and pick
another — a bounce costs more than a skipped lead.

**3. Audit each one (15-25 min each).**
Run at minimum:
- `who should I call for {service} in {city}`
- `best {trade} in {city}`
- `emergency {service} {city}`
- `{trade} open Saturday {city}`

Log which companies get named. Then pull from their site, GBP, Yelp and BBB:
business name, street address, phone, hours, founding year / years-in-business,
services listed. Find where two of them disagree. That disagreement is the email.

**4. Draft from v2 (5 min each).**
Fill the brackets with what you actually observed. Every quoted value has to be
one you read. A wrong "your site says X" ends the conversation permanently.

**5. Send, spaced.**
Not ten at 9am. Spread across the working day, 20-40 minutes apart. A consumer
Gmail firing ten identical-shaped messages in four minutes is the pattern that
gets flagged.

**6. Log it.** `cited/outreach/log.md`, format below.

## Follow-up schedule

Touch 2 goes out three days after touch 1, as a reply in your own sent thread.
So each morning: send touch 2 to the ten from three days ago, then do today's ten.

Any reply at all — including "no thanks" — stops the sequence for that prospect
immediately and gets a same-day response. Every reply gets answered. The reply
script is in `cited/social/PITCHES.md` section 4: lead with the free check, then
open the scope to automation and anything else.

## Log format

```
| date | company | metro | trade | email | verified | finding | t1 | t2 | reply | outcome |
```

Fill `finding` with the actual conflict in six words, so a month from now you can
tell which kinds of findings get replies. That is the only data that will tell
you what to automate first.

## When this changes

- **Oct 20:** twelve warmed mailboxes come online. Go to four touches and ramp
  toward 100/day — but only if the audit pipeline is built. If it isn't, stay at
  ten a day and keep building it. Volume without the audit is worse than no
  volume.
- **First paying client:** stop sourcing for a week and over-deliver. One
  referral from a happy home service owner is worth more than 500 cold sends
  into that trade.
