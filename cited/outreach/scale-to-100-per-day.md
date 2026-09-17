# Getting Cited Labs to 100 cold emails a day

Written 2026-09-17. Current state: ~25 sent between Sep 7 and Sep 11, all from
fieldingbrookerwork@gmail.com, zero replies, two hard bounces.

## Read this part first

**Stop sending cold mail from fieldingbrookerwork@gmail.com today.**

That address is the login for Anthropic, Namecheap, Cloudflare, HubSpot,
Airwallex and Google Drive. Consumer Gmail has no cold-email tolerance. Once
enough recipients mark it spam, Google restricts sending, and a restriction on
that account takes the business's payment processor and domain registrar with
it. Sending 100 a day from it is not a slow risk, it's a two-week fuse.

Personal Gmail's job from here is to receive replies. Nothing else.

## The bounce rate is a bigger problem than the volume

2 hard bounces out of 25 is 8%. The tolerance is 3%. Over 5% and mailbox
providers start throttling you regardless of content. `woodsplumbingaz.com`
did not resolve at all and `txt.att.net` does not exist.

At 100/day an 8% bounce rate is 8 dead sends a day. No warmup survives that.
Email verification before every send is not optional at this volume. See costs
below.

## The build

Target 100-120/day, arrived at by spreading across mailboxes rather than by
pushing any one mailbox hard.

**4 domains x 3 mailboxes = 12 mailboxes, 8-10 sends each per day.**

Vendors will tell you a warmed mailbox handles 30-50/day. That is the number
sold by people who sell sequencers. Operators who have burned domains run
10-20. Start at 8-10 and test upward a couple at a time. A burned domain costs
three weeks; an extra mailbox costs four dollars.

### Domains
Buy at Namecheap (account exists). Never the primary brand domain - keep
citedlabs.com clean for the website and for replies.

Buy variants that a human would believe: `citedlabs.co`, `getcitedlabs.com`,
`citedlabshq.com`, `cited-labs.com`. Avoid hyphens-plus-numbers and avoid
anything that reads as disposable.

### DNS on each domain
- SPF, DKIM, DMARC. DMARC starts at `p=none` and moves to `p=quarantine` after
  two clean weeks.
- No tracking domain. We send no links and measure replies, not opens. A
  tracking pixel costs more deliverability than the open rate is worth knowing.
- Reply-to must be an address **on the sending domain** that forwards to the
  personal Gmail. A gmail.com reply-to on a cited-labs.com send is a
  misalignment flag.

### Mailboxes
Google Workspace at $7.20/mailbox is the highest-trust option but is 12 separate
signups. Cold-email mailbox providers (Maildoso, Mailreef, Zapmail) run $3-4 and
provision all 12 with DNS pre-set in an afternoon. For 12 mailboxes the
provisioning time saved is worth more than the trust difference at this volume.

### Sequencer
Instantly (~$37/mo) or Smartlead (~$39/mo). Either one handles mailbox rotation,
built-in warmup, bounce suppression and the 4-touch sequence. Pick one, don't
evaluate both.

### Verification
MillionVerifier, ~$37 for 50,000 credits. Run every address through it before
import. This alone takes the 8% bounce rate to under 1%.

## Cost

| Item | Monthly |
|---|---|
| 4 domains (amortized) | $4 |
| 12 mailboxes @ $3.50 | $42 |
| Sequencer | $37 |
| Verification (amortized) | $6 |
| **Total** | **~$90/mo** |

## Timeline

| Dates | What happens | Sends/day |
|---|---|---|
| Sep 17-18 | Buy 4 domains, provision 12 mailboxes, set SPF/DKIM/DMARC | 0 |
| Sep 19 - Oct 10 | Warmup running on all 12, no cold sends at all | 0 |
| Oct 11-13 | Cold ramp begins, 2 per mailbox | 24 |
| Oct 14-16 | 4 per mailbox | 48 |
| Oct 17-19 | 6 per mailbox | 72 |
| Oct 20-22 | 8 per mailbox | 96 |
| Oct 23 onward | 10 per mailbox, steady | **120** |

**First 100-send day: October 20.** There is no honest way to compress this. A
domain sending 100 cold emails on day three goes to spam on day four and the
three weeks get spent anyway, just later and with worse data.

### What to do during the three warmup weeks

Do not idle. Keep sending 20-25/day from the personal Gmail **only to prospects
sourced from a warm path** (referrals, people who engaged with a post, anyone
who has heard the name). That is not cold volume and it will not trip anything.
Use the time to build the audit pipeline below, which is the actual constraint.

## The real bottleneck is not the sending

This is the part that matters more than any of the above.

The v2 script works because it names a specific verified thing about that
specific business. Producing that for one prospect means: running 3-5 assistant
queries for their city and trade, recording who got named, pulling their name,
address, phone, hours and founding claims from their site, Google Business
Profile, Yelp and BBB, and diffing them.

By hand that is 15-25 minutes per prospect. **100 a day is 25 to 40 hours of
research a day.** It cannot be done manually, and the moment it is done manually
at speed it stops being specific, which removes the only reason the email works.

So the sequence is:

1. Buy domains and start warmup today (2 hours of work, then it runs itself).
2. **Spend the three warmup weeks building the audit pipeline.** That is the
   deliverable that makes 100/day mean anything.
3. Turn on volume in mid-October against a pipeline that can actually feed it.

Turning on 100/day without step 2 produces 100 generic emails a day, which
performs worse per send than 25 specific ones and burns four domains doing it.
