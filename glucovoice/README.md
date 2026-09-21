# GlucoVoice (working name)

Hands-free spoken glucose for Dexcom G6 and G7 wearers. Tap a Quick Settings tile, a home-screen
widget, a launcher shortcut, or say "open GlucoVoice" to your assistant, and your phone says your
current reading, its trend, and how old it is:

> "123, rising, 2 minutes ago."

Android first, because Dexcom's own G7 app already gives iPhone users a Siri shortcut and gives
Android users nothing. iOS (Apple Watch, CarPlay) is planned; see `docs/IOS_PLAN.md`.

**Not a medical device. Not affiliated with Dexcom.** Confirm on your Dexcom app or a meter
before any treatment decision. Read `docs/REGULATORY.md` before distributing this to anyone.

## This folder is temporary

GlucoVoice lives inside the Bid Scout repository only because the session that built it could not
create a new GitHub repository. It shares nothing with Bid Scout. Create an empty `glucovoice`
repository and move this folder (with history if wanted: `git subtree split -P glucovoice`).

## Status

| Piece | State |
| --- | --- |
| `core/` Dexcom Share client, parser, speech formatter | Done, 30 unit tests passing |
| `app/` Android app: setup, main screen, speak, tile, widget, background refresh | Written, compiles in CI, **not yet run on a phone** |
| Demo mode (fake data, no account) | Done |
| Assistant voice trigger | "open GlucoVoice" + speak-on-open only; Google has no third-party hook in Gemini yet |
| Wear OS, Android Auto, iOS | Not started |
| Regulatory opinion | Not obtained |

## Layout

```
glucovoice/
  core/   pure Kotlin/JVM: DexcomShareClient, ShareParser, SpeechFormatter, FakeGlucoseSource
  app/    Android: ui/ (Main, Setup, headless Speak), tile/, widget/, work/, data/, speech/
  docs/   SPEC.md, DATA_SOURCES.md, REGULATORY.md, IOS_PLAN.md
```

The app depends on `core` through one interface, `GlucoseSource`, so the data feed (Dexcom Share
today) can be swapped for Nightscout or an official Dexcom partner API without touching the UI.

## Build

Any machine with a JDK 17+:

```
./gradlew :core:test                      # unit tests, no Android SDK needed
./gradlew :app:assembleDebug              # needs the Android SDK (Android Studio installs it)
./gradlew :core:test -PskipAndroid=true   # core only, where dl.google.com is unreachable
```

GitHub Actions (`.github/workflows/glucovoice-android.yml`) runs both on every push touching this
folder and uploads `app-debug.apk` as an artifact. Download it from the run page and sideload it
on an Android phone (Settings > allow installs from your browser or Files app).

## Install and set up on a phone

1. Install the APK. Open GlucoVoice. It opens Settings.
2. Enter the Dexcom login you use in the G6/G7 app (the publisher account, not a follower).
3. Pick your region and units. Tap **Test login and save**. The app logs in to Dexcom Share and
   stores the login encrypted with a key in the phone's hardware keystore. Nothing is stored
   anywhere else.
4. In the Dexcom app, Share must be on and have at least one follower, or Dexcom's servers hold no
   data to return.
5. Add the **Glucose** tile to Quick Settings and the **GlucoVoice** widget to your home screen.
   Long-press the app icon for the **Speak glucose** shortcut.

Or turn on **Demo mode** to try everything with fake data.

## Safety rules built into the code

- Every spoken reading includes value, trend and age. A stale number is never dressed up as current.
- A reading older than 15 minutes is never spoken as a number; the app says how old it is and
  sends you to the Dexcom app.
- mmol/L readings always speak their unit ("6.8 millimoles per liter"), because "six point eight"
  and "sixty eight" collide.
- No alarms, no notifications, no dosing advice. The app only answers when asked.
- Credentials never leave the phone except to Dexcom Share. Backup is disabled. No analytics.

## License

MIT. Dexcom, G6 and G7 are trademarks of Dexcom, Inc. The Share application IDs and protocol
details come from the open-source pydexcom project.
