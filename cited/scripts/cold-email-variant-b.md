# Variant B — the "AI is where your customers are now" angle

This is the script the founder asked for, written as strongly as it can be
written. It leads with the shift instead of with the prospect's specific error.

One change from what was asked: the line "search engines are dying / falling out
of usage" is not in it. That claim is false (Google is still ~5 trillion searches
a year, ~80% of query volume, still growing in absolute terms) and any owner with
an SEO vendor will stop reading at it. Everything else in the requested angle is
kept, and the true version of the trend is sharper than the false one anyway:
the loss to AI is invisible in your analytics.

Run this as the B side of a split test against v2. Do not replace v2 with it
until the data says to.

## TOUCH 1

Subject options:
- `the search your customers run that you can't see`
- `{Company} vs {Competitor} when someone asks AI`
- `your next customer is asking ChatGPT, not Google`

Body:

```
Hi {FirstName},

Your customers still Google you. But a growing share of them now open ChatGPT
first and ask "who should I call for {service} in {city}" - it's the #2 place
people ask questions now, ahead of Bing, and it's the "who should I call"
questions it's taking most.

Here's the part that matters for you: when an assistant answers that question,
it names two or three companies and the person calls one. It sends no click, no
referral, no trace. If it names {CompetitorA} instead of {Company}, nothing
shows up in your analytics. You never find out.

I asked it for {city} this week. {Company} {was/wasn't} named.

That outcome isn't random and it isn't about your website's design. Assistants
build the answer out of what your listings agree on - name, address, hours,
phone, how long you've been in business, what you do. When those disagree, you
get left out of the answer.

That's what I fix. It's SEO, but for the thing answering instead of the thing
listing. Reply "send it" and I'll send you {Company}'s check free: the queries,
who got named, and what's causing it. No call, nothing to sign.

Fielding Brooker
Cited Labs
770-626-6299
fieldingbrookerwork@gmail.com
530 Owens Farm Road, Alpharetta, GA 30004

Reply "no thanks" and I won't email again.
```

Touches 2-4: reuse v2's, they work for either opener.

## Why I expect B to lose, and what would change my mind

- B's first two paragraphs are about the industry. v2's are about the recipient.
  Specific beats general on cold email almost every time.
- Every GEO agency is sending a version of B right now. Owners have started
  pattern-matching it to spam. v2's opener does not look like a pitch.
- B still needs the per-prospect query result to have any teeth, so it does not
  actually save any research time over v2. If it did save time, it would be
  worth running for volume alone. It doesn't.

What would prove me wrong: B gets a materially better reply rate over 200+ sends
per side. That is the only thing that settles it. Run the test.

## How to run the test honestly

- Split by prospect, not by day. Odd-numbered rows get v2, even get B.
- Same trades, same metros, same mailboxes, same send times on both sides.
- 200 sends per side minimum before reading the result. At 25 sends you cannot
  tell a 2% reply rate from a 6% one.
- Measure replies, not opens. Open tracking needs a pixel, a pixel needs a
  tracking domain, and a tracking domain on a cold send hurts deliverability
  more than the open data is worth.
