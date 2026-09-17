#!/usr/bin/env python3
"""Cited Labs warm-lead listener for Reddit.

READ-ONLY. This script never posts, never comments, never sends a DM. It reads
Reddit's search API with the founder's own credentials, scores what it finds for
buyer intent, and writes a queue of threads for the founder to answer by hand.

Automating posts or DMs is a sitewide Reddit ban and is not supported here.

Setup (once, ~3 minutes):
  1. https://www.reddit.com/prefs/apps -> "create another app..."
  2. Type: "script". Redirect URI: http://localhost:8080 (unused).
  3. Export the four values:
       export REDDIT_CLIENT_ID=...       # under the app name
       export REDDIT_CLIENT_SECRET=...   # the "secret" field
       export REDDIT_USERNAME=...
       export REDDIT_PASSWORD=...

Run:
  python3 reddit_listener.py                 # last week, all topics
  python3 reddit_listener.py --days 3        # tighter window
  python3 reddit_listener.py --min-score 4   # only strong hits
  python3 reddit_listener.py --out queue.md

Note: this must run somewhere Reddit is reachable. It will not work from a
Claude Code web session; that container's proxy blocks reddit.com. Run it on the
founder's laptop or any small VPS.
"""

import argparse
import base64
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "python:cited-labs-listener:0.2 (by /u/%s)"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API = "https://oauth.reddit.com"

# Subreddits worth a daily scan. See PLAYBOOK.md for why this list is short:
# most trade subs are technicians, and most SEO subs are competitors.
SUBREDDITS = [
    "smallbusiness", "Entrepreneur", "sweatystartup", "HVAC", "Plumbing",
    "electricians", "Construction", "msp", "SEO", "marketing", "local_seo",
    "AskMarketing", "PPC", "juststart",
]

# Each query is (text, weight). Weight reflects how close the phrasing sits to
# somebody who would actually pay.
QUERIES = [
    ("show up in ChatGPT", 3),
    ("ranking in AI search", 3),
    ("generative engine optimization", 3),
    ("AI overviews traffic drop", 3),
    ("ChatGPT recommends competitor", 3),
    ("get found on AI", 2),
    ("google business profile wrong", 2),
    ("NAP consistency", 2),
    ("wrong hours online", 2),
    ("listings inconsistent", 2),
    ("lost organic traffic AI", 2),
    ("automate lead follow up", 1),
    ("automating my business", 1),
    ("marketing automation help", 1),
]

# Signals that the poster owns a business and has the problem.
BUYER_SIGNALS = {
    "my business": 3, "my company": 3, "our business": 3, "my shop": 3,
    "my agency": -2, "my clients": -2, "for a client": -3, "our clients": -3,
    "i own": 3, "we own": 3, "small business owner": 3, "owner operator": 3,
    "my website": 2, "our website": 2, "my google business": 3,
    "losing leads": 3, "fewer calls": 3, "phone stopped": 3, "leads dried": 3,
    "not showing up": 2, "can't find us": 3, "doesn't list us": 3,
    "hvac": 2, "plumbing": 2, "plumber": 2, "electrician": 2, "roofing": 2,
    "garage door": 2, "landscaping": 1, "contractor": 2, "home service": 3,
    "chatgpt": 2, "perplexity": 2, "gemini": 1, "ai overview": 2,
    "how do i": 1, "how can i": 1, "anyone know": 1, "need help": 1,
}

# Signals the poster is selling, not buying.
DISQUALIFIERS = {
    "dm me": -5, "pm me": -5, "reach out": -3, "we offer": -5, "our service": -4,
    "i offer": -5, "case study": -3, "we help businesses": -5, "book a call": -5,
    "free audit": -4, "hiring": -4, "looking to hire": -3, "job posting": -5,
    "i built": -2, "launched my saas": -4, "my tool": -3, "check out": -3,
    "upvote": -3, "promo": -3, "discount code": -5,
}


def _req(url, data=None, headers=None, timeout=25):
    body = urllib.parse.urlencode(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers or {})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace")), dict(resp.headers)


def get_token():
    need = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD"]
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        sys.exit("Missing env vars: %s\nSee the setup block at the top of this file." % ", ".join(missing))
    cid, sec = os.environ["REDDIT_CLIENT_ID"], os.environ["REDDIT_CLIENT_SECRET"]
    user, pw = os.environ["REDDIT_USERNAME"], os.environ["REDDIT_PASSWORD"]
    basic = base64.b64encode(("%s:%s" % (cid, sec)).encode()).decode()
    try:
        tok, _ = _req(
            TOKEN_URL,
            data={"grant_type": "password", "username": user, "password": pw},
            headers={"Authorization": "Basic " + basic, "User-Agent": UA % user},
        )
    except urllib.error.HTTPError as e:
        sys.exit("Reddit auth failed (%s). Check the four env vars, and that the app "
                 "type is 'script' and the account has 2FA off or an app password." % e.code)
    if "access_token" not in tok:
        sys.exit("Reddit auth returned no token: %s" % tok)
    return tok["access_token"], user


def search(token, user, sub, query, days, seen):
    window = "week" if days <= 7 else ("month" if days <= 31 else "year")
    qs = urllib.parse.urlencode({
        "q": query, "restrict_sr": "1", "sort": "new", "limit": "50", "t": window,
    })
    url = "%s/r/%s/search?%s" % (API, sub, qs)
    try:
        data, hdrs = _req(url, headers={
            "Authorization": "Bearer " + token, "User-Agent": UA % user})
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(8)
            return []
        return []
    except Exception:
        return []

    remaining = hdrs.get("x-ratelimit-remaining")
    if remaining is not None:
        try:
            if float(remaining) < 5:
                time.sleep(10)
        except ValueError:
            pass

    cutoff = time.time() - days * 86400
    out = []
    for child in data.get("data", {}).get("children", []):
        p = child.get("data", {})
        if p.get("id") in seen or p.get("created_utc", 0) < cutoff:
            continue
        if p.get("over_18") or p.get("stickied"):
            continue
        seen.add(p.get("id"))
        out.append(p)
    return out


def score(post, query_weight):
    text = ((post.get("title") or "") + " " + (post.get("selftext") or "")).lower()
    s = query_weight
    hits = []
    for phrase, w in BUYER_SIGNALS.items():
        if phrase in text:
            s += w
            if w > 0:
                hits.append(phrase)
    for phrase, w in DISQUALIFIERS.items():
        if phrase in text:
            s += w
    # An unanswered question is worth more than one with 40 replies.
    n = post.get("num_comments", 0)
    if n == 0:
        s += 2
    elif n <= 3:
        s += 1
    elif n > 25:
        s -= 2
    if len(post.get("selftext") or "") < 60:
        s -= 2  # too thin to answer usefully
    return s, hits


def draft(post, hits):
    """A starting point, not a send. The founder rewrites it to fit the thread."""
    text = ((post.get("title") or "") + " " + (post.get("selftext") or "")).lower()
    if any(k in text for k in ("chatgpt", "perplexity", "ai overview", "ai search", "generative engine")):
        return ("Answer the mechanism for free: assistants assemble local answers from "
                "whatever the majority of their listings agree on (GBP, Yelp, BBB, the "
                "site itself), so conflicting hours/phone/address/founding-year data gets "
                "a business dropped from the answer. Give them the fix order: Google "
                "Business Profile first, then Yelp and BBB, then the site last, matched "
                "word for word. Name no service. Let the profile do the selling.")
    if any(k in text for k in ("wrong hours", "google business", "listings", "nap")):
        return ("Give the full fix for free: pick one canonical version of name, address, "
                "phone, hours and founding year; update GBP first, then the big "
                "directories, then the site. Mention that AI assistants read those same "
                "listings, which is the part most people don't know. No pitch.")
    if any(k in text for k in ("automat", "follow up", "leads")):
        return ("Different problem than ours - answer it straight if you can actually "
                "help, otherwise skip. Do not bend an automation question into a GEO "
                "pitch; that reads as a pitch and gets removed.")
    return "Read the thread before drafting. If a complete free answer isn't possible, skip it."


# Reminder rendered on every queue entry. The free-demo offer is deliberately
# NOT part of any cold comment - see the "Free demo + open scope" section of
# PLAYBOOK.md. It belongs in the profile bio and in the DM reply.
COMMENT_RULE = (
    "Answer the question completely and for free FIRST, then close with the "
    "offer: free check, no call, they keep it either way - and say the scope is "
    "open to automation and any other agency work. Paste from PITCHES.md "
    "(section 1 for normal subs, section 2 for r/SEO and r/marketing). No link "
    "and never the words 'DM me' - those are what automod filters on, the offer "
    "itself usually clears. Answer every reply the same day."
)


def main():
    ap = argparse.ArgumentParser(description="Read-only Reddit warm-lead listener. Never posts.")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--min-score", type=int, default=3)
    ap.add_argument("--limit", type=int, default=40, help="max threads in the queue")
    ap.add_argument("--out", default=None, help="write markdown here instead of stdout")
    args = ap.parse_args()

    token, user = get_token()
    seen, rows = set(), []

    for sub in SUBREDDITS:
        for q, w in QUERIES:
            for post in search(token, user, sub, q, args.days, seen):
                s, hits = score(post, w)
                if s >= args.min_score:
                    rows.append((s, sub, q, hits, post))
            time.sleep(1.1)  # stay well inside 100 req/min

    rows.sort(key=lambda r: -r[0])
    rows = rows[: args.limit]

    today = dt.date.today().isoformat()
    L = ["# Reddit warm-lead queue — %s" % today, "",
         "%d threads at score >= %d, last %d days. Read-only: nothing was posted."
         % (len(rows), args.min_score, args.days), "",
         "Rule: answer completely and for free, name nothing, let the profile sell.",
         "", COMMENT_RULE, ""]
    if not rows:
        L.append("_Nothing cleared the bar today. That is a normal result for this ICP "
                 "on Reddit - see PLAYBOOK.md. Spend the time in the Facebook groups._")
    for s, sub, q, hits, p in rows:
        age = (time.time() - p.get("created_utc", 0)) / 3600
        L += [
            "## [%d] r/%s — %s" % (s, sub, (p.get("title") or "")[:110]),
            "",
            "- https://reddit.com%s" % p.get("permalink", ""),
            "- u/%s · %.0fh old · %d comments · matched %r"
            % (p.get("author"), age, p.get("num_comments", 0), q),
            "- signals: %s" % (", ".join(hits[:8]) or "none"),
            "",
            "> " + ((p.get("selftext") or "(link post)")[:340].replace("\n", " ")),
            "",
            "**Draft approach:** " + draft(p, hits),
            "",
        ]

    md = "\n".join(L)
    if args.out:
        with open(args.out, "w") as f:
            f.write(md)
        print("wrote %s (%d threads)" % (args.out, len(rows)))
    else:
        print(md)


if __name__ == "__main__":
    main()
