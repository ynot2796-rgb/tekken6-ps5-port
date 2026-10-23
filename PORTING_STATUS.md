# Porting status

## Confirmed from upstream source

- Native Online is a native Windows PC project, not an emulator package.
- It recompiles Xbox 360 game code through ReXGlue.
- It includes rollback networking based on a GGPO fork and game-side netplay/session/input integration.
- The public source does not include game code/data.
- The public source README says the official server address, release API, pinned server certificate, and launcher artwork are not published.
- The launcher depends on Qt 6 and Windows system libraries.
- The upstream CMake configuration links GGPO with Windows-specific libraries (`ws2_32`, `winmm`), uses a Xenos GPU plugin, applies x86-specific compiler flags, and configures Windows GUI entry points. This is not currently a PS5 build configuration.

## Route selection

**Primary route: native PS5 homebrew port.** Do not prioritize running the Windows release through MihawkOS / Prospero Win. Preserve the current upstream online/gameplay code where possible and port the platform layers needed for PS5.

The target is the updated Native Online experience—not merely offline Tekken 6. Desired retained functionality includes rollback netplay, online sessions/lobbies and matchmaking, and newer features such as group lobbies/spectating where they exist in the selected upstream release and can be supported by the same compatible server/protocol.

**Fallback only:** Windows compatibility runtime experiments may be useful as diagnostics, but are not the main deliverable.

## Work recorded

- `docs/NATIVE_PS5_HOMEBREW_PORT.md`: native-port strategy and phased milestones.
- `docs/NATIVE_PS5_SOURCE_AUDIT.md`: source-level portability findings and online-feature preservation plan.
- Existing Windows launcher CI is only a launcher build check; it is not a PS5 build and does not validate the game.

## Unknown / blockers

- No PS5 executable or installable package has been built.
- A minimal homebrew ELF/toolchain proof on the user's actual firmware 13.60 setup is still required.
- ReXGlue runtime and generated-code integration with the available PS5 SDK/toolchain is unverified.
- A PS5-compatible graphics backend is a major unresolved task; upstream currently uses a Xenos GPU plugin.
- Windows networking/timer/input/audio dependencies must be replaced or isolated without changing online protocol behavior.
- The public source does not contain official lobby endpoint and pinned certificate configuration. Do not invent endpoints or bypass authentication/certificate checks.
- Official server/operator compatibility with a PS5 client is unverified.
- Cross-play with PC Native Online must be tested against the same compatible release/protocol; it cannot be promised from a successful build alone.

## Acceptance criteria

- Reproducible native PS5 build and launch instructions for the user's actual firmware 13.60 setup.
- No game image, extracted assets, generated game code, credentials, private certificates, or server secrets bundled in the public repository.
- Correct controller input, audio, rendering, and stable gameplay timing.
- Existing rollback netplay preserved and tested.
- Updated online features implemented where their code and service protocol permit.
- Official matchmaking access only with legitimate configuration and verified compatibility.
- A cross-play test against the matching PC Native Online client passes before cross-play is described as working.
