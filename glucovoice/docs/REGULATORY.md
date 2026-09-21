# Regulatory notes (not legal advice)

Get a written opinion from an FDA regulatory consultant before distributing to anyone but
yourself. Budget hours of their time, not months. Bring them this file.

## What we know

- FDA classified the **continuous glucose monitor secondary display** as a Class II device with
  special controls in 2017 (21 CFR 862.1350). Dexcom Follow is the reference device. An app whose
  purpose is to show a CGM reading from another device is squarely what that classification
  describes.
- FDA cleared Dexcom's own real-time partner APIs in 2021 for third-party display, but that
  clearance covers Dexcom's invited partners, not us.
- Sugarmate, Gluroo and others distribute real-time secondary-display apps in the app stores. We
  do not know their regulatory basis and should not assume it transfers.
- Voice adds a hazard the screen does not have: mishearing a number ("fifteen" / "fifty") before
  an insulin dose. The formatter mitigates but cannot remove this.

## Design choices made to lower risk (in code today)

1. Every utterance carries value, trend and age. A number never stands alone.
2. Readings older than 15 minutes are never spoken as numbers.
3. mmol/L values always speak their unit.
4. No alarms, alerts or notifications. The app speaks only when asked.
5. No treatment recommendations of any kind, anywhere.
6. Disclaimer on every screen that shows a number and in the store listing.
7. Data stays on-device. No account with us, no cloud, no analytics.

## Questions to put to the consultant

- Does an on-demand spoken readout of a CGM value, without alarms, fall under 862.1350 as a
  secondary display? If so, is 510(k) with Dexcom Follow as predicate the path, and what would the
  special controls require of the software (verification, human factors, labeling)?
- Does FDA's enforcement discretion for low-risk general wellness or medical device data systems
  apply to any version of this (for example, a version that only repeats what the Dexcom app
  already displays, with no independent processing)?
- Does adding "low" / "high" descriptors change the answer?
- Does an open-source, free, no-server distribution change the answer?
- What labeling and store-listing language is required or prohibited?

## Privacy

Not a HIPAA covered entity (consumer app, no provider or insurer relationship), but state privacy
laws (Washington My Health My Data Act, California CCPA/CMIA) apply to health data. The design
answer is the same: collect nothing, store nothing off-device, publish a privacy policy that says
so. Google Play's Data safety form must match.
