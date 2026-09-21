# GlucoVoice product spec

## Who it is for

People wearing a Dexcom G6 or G7 who want the number without looking: blind and low-vision users,
drivers, people cooking or holding a child, anyone on Android (Dexcom gives Android no voice at all).

## What version 1 does

- Speaks the latest reading on demand: value, trend, age. English only.
- Entry points: Quick Settings tile, home-screen widget, launcher shortcut, "open GlucoVoice" via
  the phone's assistant (the app speaks on open when that setting is on), and the big Speak button.
- Shows the same information on screen with the same words as the toast, for sighted confirmation.
- Demo mode with fake data so the app can be tried and reviewed without a Dexcom account.
- Background refresh every 15 minutes so the widget and tile are roughly current.

## What version 1 deliberately does not do

- No alarms or push notifications. Dexcom already does that, and alarms move the regulatory
  question from "secondary display" toward "alerting device".
- No treatment advice, no insulin math, no trend prediction.
- No cloud. No account with us. No analytics.
- No speaking a number older than 15 minutes.
- No "low" / "high" words yet. Useful for blind users; decide after the regulatory opinion.

## Phases

1. **Android core** (this code): Share client, app, tile, widget. Sideload builds from CI.
2. **On-phone hardening**: run on a real G6 and G7 account for two weeks; fix Share edge cases
   (sensor warm-up gaps, signal loss, timezone changes); accessibility pass with TalkBack.
3. **Voice in**: Gemini App Functions or whatever Google ships for third-party apps; on-device
   wake word (Picovoice Porcupine) as a fallback inside the app; Wear OS tile; Android Auto.
4. **Play Store**: regulatory opinion in hand, privacy policy, data-safety form, closed test with
   20+ testers for 14 days (Play requirement for personal accounts), then production.
5. **iOS**: see IOS_PLAN.md. Apple Watch and CarPlay are the gaps Dexcom's Siri shortcut leaves.
6. **Official data**: apply to Dexcom's partner program once there are real users.

## Non-negotiables

- Value + trend + age in every utterance.
- Stale readings never spoken as numbers.
- Disclaimer visible on every screen that shows a number.
- Credentials on-device only, hardware-keystore encrypted.
