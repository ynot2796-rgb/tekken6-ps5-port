# First compatibility route: Prospero Win

**Recommendation: test the existing Windows build in Prospero Win before writing a native PS5 port.** This is a feasibility route, not a claim that Tekken 6 Native Online already works.

Project: https://github.com/mpereiraesaa/prospero-win  
Current release page: https://github.com/mpereiraesaa/prospero-win/releases  
Getting started: https://github.com/mpereiraesaa/prospero-win/blob/main/docs/GETTING_STARTED.md  
Game install guide: https://github.com/mpereiraesaa/prospero-win/blob/main/docs/INSTALLING_GAMES.md

## Why this is the first test

Prospero Win is an experimental Windows compatibility runtime for homebrew-enabled PS5. Its upstream README describes 64-bit Windows applications running on the PS5 x86-64 CPU through Wine, Direct3D 8–11 translation through DXVK/Vulkan, DualSense/XInput, audio, and networking. The store listing for v0.2.0 also describes hostname resolution and HTTPS support.

That makes it a much smaller first experiment than immediately porting ReXGlue, GGPO, the Xenos renderer, and the Qt launcher.

## Compatibility questions to answer

- [ ] Does the user's firmware 13.60 jailbreak/loader setup support the exact Prospero Win release and its bundled helper?
- [ ] Does the Tekken Native Online Windows executable launch under its Wine runtime?
- [ ] Which graphics API does the current Xenos backend actually use, and is that API supported by Prospero Win?
- [ ] Are the required Windows DLLs and Visual C++ runtime available?
- [ ] Can the existing game builder run on-console, or must the user build the game on a PC first?
- [ ] Does DualSense input map correctly to the game's controller code?
- [ ] Does audio work and does the game hold deterministic 60 FPS?
- [ ] Does the launcher resolve the official service and validate TLS correctly with its required server configuration?
- [ ] Can a real match be completed with a PC player on the same release?

## Important limitations

Prospero Win is experimental and compatibility is game-specific. Its documented Direct3D translation covers versions 8–11; do not assume a Direct3D 12 path is supported. The Tekken project must be inspected to identify its actual graphics calls before selecting a path.

The Native Online public source omits official server configuration and the pinned certificate. Even if the game launches, online compatibility cannot be asserted until the authorized endpoint/configuration is available and a real cross-play test passes.

## Safe test sequence

1. Verify the release archive's SHA-256 against the official project listing.
2. Read the project's installation instructions and use only a build from its official release page.
3. Confirm the user's loader/payload is compatible with firmware 13.60 before installing.
4. Transfer only the homebrew runtime and the user's own game files; do not redistribute copyrighted game data.
5. Test offline launch and controller/audio first, then networking.
6. Record the exact runtime version, firmware, error text/log, and point of failure.

Never disable certificate verification or use a guessed matchmaking endpoint to force a connection.
