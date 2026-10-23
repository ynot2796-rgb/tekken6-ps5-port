# Tekken 6 Native Online — PS5 Compatibility Port

**Status: early feasibility work; not a playable port.**

Goal: reuse the existing Tekken 6 Native Online project and determine the shortest viable route to run it on a jailbroken PS5 running firmware 13.60, while preserving online compatibility with the existing PC community wherever technically possible.

## Strategy: reuse before rewrite

First test the existing Windows application through MihawkOS, with Prospero Win as a secondary compatibility option. MihawkOS documents Wine/Proton, DXVK and VKD3D-Proton support, but this does not guarantee compatibility with the project's custom Xenos graphics backend or Qt launcher. If compatibility fails, port only the unsupported platform layers. Do not rewrite the game logic or GGPO rollback code unless testing proves a change is necessary.

See [the native PS5 homebrew port plan](docs/NATIVE_PS5_HOMEBREW_PORT.md) for the preferred long-term direction, plus [the MihawkOS evaluation](docs/MIHAWKOS_EVALUATION.md) and [the Prospero Win evaluation](docs/PROSPERO_WIN_EVALUATION.md) as fallback experiments.

## Upstream projects

- Native Online source: https://github.com/Ekspym/tekken6-native-online-source
- Native Online releases: https://github.com/Ekspym/Tekken6-native-online/releases (latest checked: v2.4.2, published Oct 23, 2026; includes upstream Windows package and patch)
- ReXGlue SDK: https://github.com/rexglue/rexglue-sdk
- Original recompilation work: https://github.com/mahmoud-mess/tekken6-recomp
- PS5 homebrew SDK: https://github.com/ps5-payload-dev/sdk
- MihawkOS: https://github.com/mihawk-99/PS5_MihawkOS

## Confirmed constraints

The upstream project is a native Windows PC port using ReXGlue static recompilation, a Xenos graphics backend, a GGPO fork, and a Qt/Win32 launcher. It does not include game code/data; the player generates the game from their own compatible Tekken 6 Xbox 360 copy.

The upstream README says official matchmaking server configuration and the pinned certificate are not published in the public source. Running the game on PS5 therefore does not by itself prove it can use the same official lobbies. Preserve protocol/version behavior and do not guess endpoints or disable TLS validation.

## Milestones

1. **Compatibility-runtime test:** test the Windows build through MihawkOS first, then Prospero Win if needed. Record the exact runtime version, firmware, and error/log output.
2. **Build/toolchain test:** establish a reproducible build of the public components and identify what requires the user's own game files.
3. **Game launch:** test the existing game build before replacing any components.
4. **Input/audio/performance:** verify DualSense input, sound, stable timing and rendering.
5. **Online:** verify official service access and test cross-play with an unmodified PC client, only where permitted by the service operator.

## Current status

The upstream project published v2.4.2 on Oct 23, 2026, with a Windows package and a separate patch. This is the most practical baseline to test before attempting a full source build; it is not a PS5 build and is not yet confirmed to run under MihawkOS. A GitHub Actions Windows launcher build check is running to validate the public launcher build path, but a successful launcher build would not mean the game itself has been built. Track the run at https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/workflows/windows-launcher-build.yml.

No PS5 executable has been built or tested. The code in this repository is an initial porting scaffold, not the game. The user currently has source code only, so a Windows build and the user's own compatible game files are still needed before an on-console game test. No copyrighted game files, credentials, server secrets, or guessed server addresses are included.
