# Porting status

## Confirmed from upstream source

- Native Online is a native Windows PC project, not an emulator package.
- It recompiles Xbox 360 game code through ReXGlue.
- It includes rollback networking based on a GGPO fork and game-side netplay/session/input integration.
- The public source does not include game code/data.
- The public source README says the official server address, release API, pinned server certificate, and launcher artwork are not published.
- The upstream CMake configuration links GGPO with Windows-specific libraries (`ws2_32`, `winmm`), uses a Xenos GPU plugin, applies x86-specific compiler flags, and configures Windows GUI entry points. This is not currently a PS5 build configuration.

## Route selection

**Primary route: native PS5 homebrew title.** The deliverable must be a real title folder registered by ShadowMountPlus, not a Windows executable or a payload-only demo.

The target is the updated Native Online experience—not merely offline Tekken 6. Desired retained functionality includes rollback netplay, online sessions/lobbies and matchmaking, and newer features such as group lobbies/spectating where their code and compatible service protocol permit.

## Work recorded

- `docs/NATIVE_PS5_HOMEBREW_PORT.md`: native-port strategy and phased milestones.
- `docs/NATIVE_PS5_SOURCE_AUDIT.md`: source-level portability findings.
- `docs/ONLINE_PORTABILITY_NOTES.md`: session, rollback and input reuse points.
- `docs/PS5_TITLE_PACKAGING_AND_BOOT.md`: native title folder, runtime, signing, ShadowMountPlus and firmware-specific validation requirements.
- `native/first_boot/main.c`: first-boot notification diagnostic source, explicitly not the game.
- `native/first_boot/sce_sys/param.json`: proposed title metadata for the diagnostic.
- `native/first_boot/make_icon.py`: deterministic icon generator.
- `native/first_boot/BUILD_STATUS.md`: build record, ZIP SHA-256 and console test procedure.
- `.github/workflows/native-ps5-diagnostic.yml`: CI build/package route using the public ProsperoStore native-app build tooling pinned to commit `3290ee0d43c5e8ac49870e7c7e84639374a56bf1`.

## Current status — do not overstate

The first native diagnostic title ZIP has been built successfully by CI and its contents were checked. SHA-256: `3b4b2eaa6ce4358fe8ef408bd8c43c5da64434804e7dec8a5b5db68b49c7fc74`. It contains `eboot.bin`, title metadata, icon, and the checksum-verified clean-room runtime; the unused helper is absent. **It has not yet been tested on a physical PS5**, so firmware 13.60 launch/registration is still unverified. See `native/first_boot/BUILD_STATUS.md`.

## Unknown / blockers

- Whether the resulting title launches on firmware 13.60 and the user's installed ShadowMountPlus version.
- ReXGlue runtime and generated-game integration with the native app runtime is unverified.
- A PS5-compatible graphics backend is a major unresolved task; upstream currently uses a Xenos GPU plugin.
- Windows networking/timer/input/audio dependencies must be replaced or isolated without changing online protocol behavior.
- The public source does not contain official lobby endpoint and pinned certificate configuration. Do not invent endpoints or bypass authentication/certificate checks.
- Official server/operator compatibility with a PS5 client is unverified.
- Cross-play with PC Native Online must be tested against the same compatible release/protocol; it cannot be promised from a successful build alone.

## Acceptance criteria

- Diagnostic title builds and launches from the home screen on firmware 13.60.
- Reproducible native PS5 build and launch instructions.
- No game image, extracted assets, generated game code, credentials, private certificates, or proprietary Sony modules bundled in the public repository.
- Correct controller input, audio, rendering, and stable gameplay timing.
- Existing rollback netplay preserved and tested.
- Updated online features implemented where their code and service protocol permit.
- Official matchmaking access only with legitimate configuration and verified compatibility.
- A cross-play test against the matching PC Native Online client passes before cross-play is described as working.
