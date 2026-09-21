# Where the glucose numbers come from

## Options considered

| Source | Real time? | Open to us? | Notes |
| --- | --- | --- | --- |
| Dexcom official API v3 | No: 1 hour delay in the US, 3 hours elsewhere | Yes, OAuth | Built for retrospective apps. Useless for "what is it now". |
| Apple HealthKit / Health Connect | No: Dexcom writes each value 3 hours late | Yes | Same problem. |
| Dexcom Partner Web APIs (real-time, FDA-cleared 2021) | Yes | Invite only (Garmin, Livongo...) | The right long-term answer. Apply once there are users. |
| Nightscout | Yes | Yes, if the user runs one | Good second adapter; small share of users. |
| **Dexcom Share (what the Follow app uses)** | Yes, ~5 min cadence | Undocumented, tolerated | What Sugarmate, Gluroo, xDrip+ and Nightscout's bridge use. **Used here.** |

## Dexcom Share protocol (as implemented in `core/DexcomShareClient.kt`)

Base URLs: `share2.dexcom.com` (US), `shareous1.dexcom.com` (outside US), `share.dexcom.jp` (Japan),
path `/ShareWebServices/Services/`. All calls are HTTPS POST with a JSON body.

1. `General/AuthenticatePublisherAccount` with `{accountName, password, applicationId}` returns the
   account UUID as a JSON string.
2. `General/LoginPublisherAccountById` with `{accountId, password, applicationId}` returns a session
   UUID.
3. `Publisher/ReadPublisherLatestGlucoseValues?sessionId=..&minutes=1440&maxCount=1` with body `{}`
   returns `[{"WT":"Date(1691455258000)","ST":..,"DT":..,"Value":85,"Trend":"Flat"}]`.

Errors come back as HTTP 500 with `{"Code": "...", "Message": "..."}`. `SessionNotValid` and
`SessionIdNotFound` mean re-login (done once, automatically). `AccountPasswordInvalid` and
`SSO_AuthenticateMaxAttemptsExceeded` are credential problems and are never retried in the
background. The application IDs are the ones the Dexcom Follow app presents; they are public in
pydexcom and many other projects.

The user must have Share enabled in the Dexcom app with at least one follower, or the servers hold
no data.

## Risks and what we do about them

- **Dexcom can shut it off or change it any day.** The app depends on one interface,
  `GlucoseSource`. Swapping in Nightscout or the partner API touches no UI code. If Share dies,
  the app says so plainly ("Dexcom Share gave an unexpected answer") instead of speaking stale data.
- **Terms of service.** Using an undocumented endpoint with the user's own credentials, on the
  user's own device, for the user's own data, is what a decade of community tools do. It is still
  a risk. Do not add a server, do not proxy Share through anything we operate, do not scrape.
- **Rate limits.** One request per user action plus one every 15 minutes in the background.
  Nothing polls faster than that.
- **Credential handling.** Stored only on-device, AES-256-GCM with a hardware-keystore key,
  backup disabled, sent only to Dexcom Share over TLS.
