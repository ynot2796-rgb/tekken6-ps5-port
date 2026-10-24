# Native Tekken 6 package build gate

This document distinguishes three outputs that must not be conflated.

1. **Native graphics probe** — a generated PS5 Vulkan-template title used to validate the toolchain, graphics stack, link script, and controller/camera input. It is not Tekken 6.
2. **Native title folder / ZIP** — the PS5 title layout with `eboot.bin`, `sce_sys/param.json`, and staged runtime components. This is useful for homebrew launch/testing, but a ZIP of the title directory is not automatically an installable encrypted `.pkg`.
3. **Native Tekken 6 package** — requires generated Tekken 6 C++ from a compatible user-owned Xbox 360 disc image, the pinned ReXGlue runtime and Xenos Vulkan plugin compiled for Prospero, PS5-specific runtime/input/audio/file/memory adapters, and successful packaging plus console validation.

## What CI has proved

- The template-based native graphics/input probe built and packaged twice:
  - https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40066666719
  - https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40067130875
- The guarded Prospero CMake patch tests pass:
  - https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40067358848
- These are toolchain and probe results, not a Tekken executable and not proof of console boot.

## Local game-source requirement

The public Native Online builder supports only the verified Tekken 6 Xbox 360 USA/Europe Rev 1 image. Its builder validates the SHA-256 of `Default.xex` as `ee138a4fe8d32a0edc131451377f4377041a49626153fa992db24f5420a7f15c`. A different revision needs separate validation and code-generation fixes.

The ISO and generated game code must remain on the user's own machine; do not upload the disc image, proprietary generated C++, or game assets to public CI or this repository. CI can validate platform code and build public components without those files, but cannot honestly claim a native Tekken package exists until the local game code is compiled into the PS5 title.

## Remaining gates in order

1. Fix and pass the PS5 source-preparation / GGPO cross-compile CI.
2. Compile the pinned ReXGlue runtime plus Xenos Vulkan plugin with the Prospero toolchain.
3. Add a deterministic native frame/input bridge and port remaining OS-specific dependencies; no Win32 APIs may be assumed to exist on PS5.
4. Run the user's locally generated Tekken game sources through the PS5 build and resolve compile/link/runtime errors.
5. Produce and checksum a title-folder ZIP (and only create an installable `.pkg` if the chosen homebrew packaging tool and target format are verified).
6. Test launch, rendering, controller, sound, gameplay, exit/relaunch and memory stability on the user's PS5 firmware 13.60.

**Do not label the game bootable/playable until step 6 has passed.**
