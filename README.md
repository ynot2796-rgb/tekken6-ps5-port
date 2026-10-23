# Tekken 6 Native Online — PS5 Compatibility Port

**Status: early feasibility work; not a playable port.**

Goal: reuse the existing Tekken 6 Native Online project and determine the shortest viable route to run it on a jailbroken PS5 running firmware 13.60, while preserving online compatibility with the existing PC community wherever technically possible.

## Strategy: reuse before rewrite

First evaluate whether a PS5 Windows-compatibility runtime can run the existing PC build with acceptable graphics, controller, audio, networking, and timing. If that route fails, port only the unsupported platform layers. Do not rewrite the game logic or GGPO rollback code unless testing proves a change is necessary.

## Upstream projects

- Native Online source: https://github.com/Ekspym/tekken6-native-online-source
- Native Online releases: https://github.com/Ekspym/Tekken6-native-online/releases
- ReXGlue SDK: https://github.com/rexglue/rexglue-sdk
- Original recompilation work: https://github.com/mahmoud-mess/tekken6-recomp
- PS5 homebrew SDK: https://github.com/ps5-payload-dev/sdk

## Confirmed constraints

The upstream project is a native Windows PC port using ReXGlue static recompilation, a Xenos graphics backend, a GGPO fork, and a Qt/Win32 launcher. It does not include game code/data; the player generates the game from their own compatible Tekken 6 Xbox 360 copy.

The upstream README says official matchmaking server configuration and the pinned certificate are not published in the public source. Running the game on PS5 therefore does not by itself prove it can use the same official lobbies. Preserve protocol/version behavior and do not guess endpoints or disable TLS validation.

## Milestones

1. **Compatibility-runtime test:** verify whether a current PS5 Windows compatibility runtime can launch the existing build on firmware 13.60, and document required payload/runtime versions and limits.
2. **Build/toolchain test:** if needed, compile a minimal native PS5 homebrew probe with a toolchain known to support the target firmware.
3. **Game launch:** test the existing game build before replacing any components.
4. **Input/audio/performance:** verify DualSense input, sound, stable timing and rendering.
5. **Online:** verify official service access and test cross-play with an unmodified PC client, only where permitted by the service operator.

## Current status

No PS5 executable has been built or tested. The code in this repository is an initial porting scaffold, not the game. No copyrighted game files, credentials, server secrets, or guessed server addresses are included.
