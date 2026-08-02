# Chickadee — device integration

The Home Assistant device integration for **Chickadee**: screen and brightness
control, sensors, cameras (including Frigate), media and music for a Chickadee
kiosk on your network.

Chickadee is free and source-published, with no account and no metered service.

## Installing it

Add this repository to [HACS](https://hacs.xyz) as a custom repository, install
**Chickadee**, and restart Home Assistant. It is only useful alongside the
Chickadee Android app running on a tablet or TV on the same network — without a
device to talk to, it has nothing to control.

This is **not** the voice integration; the
[Chickadee add-on](https://github.com/jwlerch78/chickadee) installs that one for
you.

Related: [chickadee](https://github.com/jwlerch78/chickadee) ·
[chickadee-voice-integration](https://github.com/jwlerch78/chickadee-voice-integration)

## Provenance

Chickadee shares a codebase with **Dashie**, a paid family-dashboard product by
the same author. The Chickadee trees are **generated** from that codebase rather
than written here, so this repository's history is machine-authored — commits read
`Regenerate from <source> @ <sha>`, and there may be no human-authored commits at
all.

That is normal for a generated artifact, and it is stated here rather than left
to be discovered. The generator, its substitution tables and the checks that gate
them are part of the source it is generated from.

The full disclosure — including the brand's own history, which reversed twice and
is corrected by appending rather than by editing — is on the Dashie side, where
the source lives:
[PROVENANCE.md](https://github.com/jwlerch78/dashie-ha/blob/main/PROVENANCE.md).

## Licence

AGPL-3.0-only.
