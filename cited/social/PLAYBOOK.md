# Warm outreach playbook — Cited Labs

Written 2026-09-17.

## The problem with the Reddit plan, stated plainly

The buyer is an owner or GM of a home services company doing $2-10M. That person
is largely not on Reddit asking how to show up in ChatGPT.

Here is what the relevant subreddits actually contain:

| Subreddit | Who's there | Useful? |
|---|---|---|
| r/HVAC, r/Plumbing, r/electricians | Technicians, not owners | Rarely. Owner-flair and weekly business threads only |
| r/HVACAdvice, r/Plumbing help posts | Homeowners with broken equipment | No. Wrong side of the transaction |
| r/SEO, r/marketing, r/bigseo | Agencies and marketers | These are competitors or resellers, not clients |
| r/smallbusiness, r/Entrepreneur | Mixed, mostly not home services | Occasionally. Low volume, high noise |
| r/msp, r/agency | Service businesses, adjacent ICP | Some. Different pitch needed |

So Reddit is worth **monitoring**, not worth building a strategy on. Two of those
rows are genuinely worth a daily scan: owner threads in the trade subs, and
"how do I get found in AI" posts in r/smallbusiness. Expect a handful of real
leads a month, not a pipeline.

## Where the buyer actually is

In rough order of value:

1. **Facebook Groups.** This is the channel. Owners are in these daily and ask
   marketing questions constantly. Look for: HVAC/plumbing/electrical business
   owner groups, "Home Service" operator groups, ServiceTitan and Housecall Pro
   user groups, Nexstar and Service Roundtable adjacent communities. Join as a
   person, not a brand.
2. **ServiceTitan and Housecall Pro community forums.** Owners only, high intent,
   almost no competing GEO noise yet.
3. **Trade associations.** ACCA, PHCC, NECA - national forums and, more usefully,
   local chapters in metro Atlanta.
4. **LinkedIn.** Works for the $5M+ end of the ICP. Weak below that.
5. **Reddit.** Monitored, per above.

## What actually works in all of them (and what gets you banned)

Replying to a thread with "I do this for a living, DM me" gets removed by
automod within minutes on Reddit, gets you booted from Facebook groups, and
builds nothing. Every one of these communities has an explicit self-promo rule.

What works is posting the audit **as a finding**, not as an ad:

> "I checked 40 Atlanta HVAC companies to see which ones ChatGPT names when
> someone asks who to call. 9 got named consistently. Here's what those 9 had in
> common and what the other 31 had wrong."

That is content. It obeys every self-promo rule, it demonstrates the product
instead of describing it, and the DMs it generates are inbound - which converts
at a completely different rate than outbound and costs nothing in deliverability.

The founder should run one of these per metro. The data comes from the same
audit pipeline that feeds the cold email, so it is nearly free to produce once
that exists.

When replying to someone else's thread, the rule is: **answer the question
completely and for free, name nothing.** If the answer is good, people check
the profile. Put "Cited Labs, GEO for home services, Atlanta" in the profile and
let the profile do the selling. No link in the comment.

## Hard limits

- **Never automate posting or DMing.** Reddit bans for it sitewide, Facebook
  disables accounts for it, and both are permanent in practice. The listener
  script below reads only and drafts only. The founder posts, from their own
  account, by hand.
- **No new accounts.** An account with no history posting about a service gets
  filtered regardless of content. Use an aged personal account, or spend 30 days
  commenting normally before posting anything business-related.
- **Disclose when it's your service.** If a reply mentions Cited Labs at all, say
  it's yours in the same sentence. Undisclosed self-promo is the fastest ban.
- **Never scrape a logged-in or registration-gated surface.** Facebook Groups are
  read manually. The listener covers Reddit only, through Reddit's own API, with
  credentials, inside its rate limit.

## Daily routine (20 minutes)

1. Run the listener (see `reddit_listener.py`). It outputs a scored queue.
2. Open the top 5 threads. Reply to the ones where a complete free answer is
   possible. Skip the rest.
3. Check the two or three Facebook groups by hand. Same rule.
4. Once a week, post one metro finding as content.

---

# Free demo + open scope

Standing instruction from the founder: offer a free demo on everything, and take
any automation or agency work that produces a client. That is right, with one
correction about *where* the offer goes.

## The trap

Putting "happy to give you a free demo, DM me" inside a cold Reddit comment is
the single most-removed pattern on the site. Automod in r/smallbusiness,
r/Entrepreneur and every trade sub filters it on sight, and doing it repeatedly
gets the account shadowbanned. The offer is good. Putting it in a cold comment
destroys the account that would have delivered it.

Second trap, smaller but real: leading with "we do anything - automation,
websites, whatever you need" reads as unserious to an owner running a $5M shop.
Generalists get dismissed; specialists get hired and then asked to do everything
else. The scope opens *after* they're talking to you, not in the first line.

## So: where each thing goes

| Surface | Free demo offer? | Open scope? |
|---|---|---|
| Reddit comment (cold) | **No.** Answer free, name nothing | No |
| Reddit profile bio | Yes, one line | Yes, one line |
| Reddit DM (they messaged first) | **Yes, lead with it** | Yes |
| Facebook group comment | Yes, groups tolerate it | Soft |
| Facebook group post (your content) | Yes, offer it to the group | Soft |
| Facebook DM (they engaged first) | **Yes, lead with it** | Yes |
| ServiceTitan / HCP forums | Follow each forum's rule, usually no in-thread | No |
| Anyone who replies to a cold email | **Yes, lead with it** | Yes |

The rule underneath: **the free demo is the response, not the approach.** It is
the most valuable thing on offer and it converts hard, but only after they've
raised a hand. Spent as an opener it gets filtered; spent as a reply it closes.

## Profile bio (set this on both Reddit and Facebook)

```
Fielding Brooker — Cited Labs, Atlanta.
I check whether AI assistants recommend your business when customers ask,
and fix it when they don't. Free check for anyone who asks.
Also do automation and marketing work for home service companies.
770-626-6299
```

That does all the selling a cold comment shouldn't. It's visible on every reply
you leave, it carries the free offer, and it carries the open scope, without a
single comment ever having to pitch.

## Reply script — when someone DMs or answers

```
Happy to just show you.

Send me your business name and city and I'll run the check tonight - the
queries a customer would actually type, who the assistants name, and what's
causing it if it isn't you. Takes me about 20 minutes, costs you nothing,
and there's no call attached to it. If it's useful we can talk, if not you
keep the findings.

And if what you actually need is something else - follow-up automation,
review requests, getting your CRM to stop dropping leads, the website itself -
tell me what it is. GEO is the thing I specialize in but I do the rest of it
too, and I'd rather fix the thing that's actually costing you money.

Fielding — Cited Labs
770-626-6299
```

That leads with the free demo, keeps the specialist credibility, and opens the
scope in the same breath. Use it verbatim on Reddit DMs, Facebook DMs, and cold
email replies.

## Group content post — the version that carries the offer

Facebook groups tolerate this. Reddit mostly does not; on Reddit post the
finding and drop the last paragraph.

```
I checked 40 Atlanta HVAC companies to see which ones ChatGPT and Gemini
actually name when a homeowner asks "who should I call."

9 got named consistently. 31 didn't. The 9 had one thing in common and it
wasn't budget, reviews, or how good their website looked - it was that their
name, address, phone, hours and years-in-business said the same thing
everywhere. The 31 contradicted themselves somewhere, usually between their
own About page and their Google profile, and the assistants resolved the
conflict by naming someone else.

Full breakdown of what I found is below. The fix order, if you want to do it
yourself: Google Business Profile first, then Yelp and BBB, then your own
site last, matched word for word.

If anyone wants me to run theirs, comment or DM me your business name and
city and I'll do it free - no call, no pitch, you keep the findings either
way. Same goes if you've got some other thing bleeding leads; I do automation
and marketing work for home service companies too.
```
