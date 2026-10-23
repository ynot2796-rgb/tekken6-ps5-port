# Porting status

## Confirmed from upstream source

- Native Online is a native Windows PC project, not an emulator package.
- It recompiles Xbox 360 game code through ReXGlue.
- It includes rollback networking based on a GGPO fork.
- The public source does not include game code/data.
- The public source README says the official server address, release API, pinned server certificate, and launcher artwork are not published.
- The launcher depends on Qt 6 and Windows system libraries.

## Route selection

**Preferred first attempt:** test a PS5 Windows-compatibility runtime against the already-built PC release before attempting a native port. This best matches the requirement to reuse the existing game, launcher, and online stack. Compatibility, architecture support, graphics API support, controller behavior, network access, and firmware 13.60 support must all be verified; do not assume they work.

**Fallback:** build a minimal native PS5 probe and port only the platform-dependent runtime/graphics/input/audio/launcher layers while preserving game logic and GGPO code where possible.

## Unknown / blockers

- Whether the compatibility runtime supports the PC build's architecture and required graphics APIs on firmware 13.60.
- Whether the official server/operator permits a PS5 client.
- Official matchmaking protocol details and whether they are documented.
- Whether the exact official client protocol can be implemented on PS5 without private configuration.
- ReXGlue runtime compatibility with an available PS5 SDK and target firmware 13.60.
- A viable Xenos graphics backend on PS5 if compatibility translation is insufficient.
- Availability and licensing of any required generated files and patches for a third-party port.

## Acceptance criteria

- Reproducible steps with no game data bundled.
- Launches on the user's actual PS5 firmware 13.60.
- Correct controller input and audio.
- Stable gameplay timing.
- Official matchmaking service access only if authorized and protocol-compatible.
- Cross-play test against an unmodified PC Native Online client passes.
