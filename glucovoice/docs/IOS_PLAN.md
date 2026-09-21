# iOS plan (no Mac required)

## Why iOS is second

Dexcom's G7 iPhone app already has a Siri shortcut ("What's my glucose"). A clone adds nothing. The
gaps on Apple are Apple Watch (Dexcom's Siri feature does not work there), CarPlay, a lock-screen
widget that speaks, and the trend-plus-age phrasing.

## Building without a Mac

- **GitHub Actions macOS runners** build and sign iOS apps. Public repos get them free; private
  repos pay macOS minutes at a 10x multiplier. Fastlane `match` manages certificates in a private
  repo so signing works headless.
- **Apple Developer Program**: $99/year, required for TestFlight and the App Store. Enroll early;
  approval can take days.
- **Testing**: TestFlight on your own iPhone. No Mac needed once CI produces the build.
- **Xcode Cloud** is the alternative: Apple-hosted, 25 hours/month free, configured from App Store
  Connect in a browser.

## Architecture

- Swift package `GlucoVoiceCore` mirroring `core/` (Share client, parser, formatter) so the two
  platforms speak the same sentences. Port the unit tests one-for-one.
- **App Intents** (iOS 16+): a `SpeakGlucoseIntent` so "Hey Siri, what's my sugar" (user-chosen
  phrase) runs our intent and Siri speaks the result. Works on Apple Watch via the watch app's
  App Intents, and from CarPlay via Siri.
- Widgets: Lock Screen accessory widget and Home Screen widget via WidgetKit, tapping opens the
  intent.
- Apple Watch app: complication + one big button. Direct Share fetch from the watch when the phone
  is away.
- Keychain for credentials, no iCloud sync (`kSecAttrSynchronizable` false).

## Review risk

App Store guideline 1.4.1 says apps that could be used for diagnosing or treating patients get
extra scrutiny. Expect a request for a demo account (demo mode exists for this) and for the
disclaimer language. Sugarmate's presence in the store is precedent, not a guarantee.
