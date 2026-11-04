# Reuse-first native PS5 integration plan

## Objective

Reach a bootable native Tekken 6 title by adapting proven PS5 title infrastructure and existing game/runtime code. Avoid writing a second title launcher, Vulkan stack, controller layer, or package pipeline.

## Reuse inventory and decisions

| Existing asset | Reuse decision | Boundary |
|---|---|---|
| `native/first_boot/` diagnostic title | Reuse title metadata/layout and the native-title packaging conventions | Its busy-loop diagnostic entry point is not game code and must be replaced |
| `native-ps5-render-input-probe.yml` | Reuse the pinned PS5 Vulkan template, RADV bootstrap, title generation, linker patch, packaging and artifact upload steps | Probe implementation is validation code, not Tekken |
| `PS5_VulkanTemplate` + pinned `PS5_Vulkan` | Reuse as the native title build/link foundation | Keep exact SDK/Mesa/RADV revisions aligned; verify firmware 13.60 on console |
| ReXGlue Xenos Vulkan plugin | Prefer this existing renderer over writing a new Xenos renderer | Must compile/link for Prospero and receive the game runtime's required services |
| Existing Tekken generated/recompiled code | Integrate locally after the PS5 runtime ABI is available | Never upload generated proprietary code or game assets |
| Native Online / GGPO | Preserve rollback/session logic and the POSIX portability overlay | Game callbacks, deterministic state and actual sockets still require integration tests |
| PS5X360 native platform work | Borrow/adapt title lifecycle, memory, clock, filesystem, input, audio and diagnostic patterns | Do not link Xenia guest CPU/kernel/emulator into a native ReXGlue game |

## Fastest build sequence

1. Finish the current ReXGlue + Xenos Vulkan Prospero configure/compile gate.
2. Keep using the already-proven PS5 Vulkan template and native-title package workflow; do not rebuild the platform stack in a separate implementation.
3. Build a ReXGlue-backed native title shell using the existing title metadata/link recipe. Start with a runtime smoke entry point, then add ReXGlue initialization and renderer/plugin loading.
4. Compile a small generated-code harness to expose unresolved Prospero imports and ABI mismatches before attempting the complete game.
5. Add the locally generated Tekken code and existing game-side adapters in stages; preserve GGPO separately until deterministic game-state callbacks pass.
6. Package each successful build as a title-folder ZIP with checksums and upload CI artifacts. Only call it installable after required user-supplied runtime dependencies are accounted for; only call it bootable after a firmware-13.60 console launch is confirmed.

## Guardrails

- No game ISO/XEX, extracted assets, generated proprietary game code, private credentials/certificates, or Sony-owned runtime modules in CI artifacts.
- Reuse code only with its license notices and required license obligations preserved.
- Do not treat a generic graphics probe, black-screen process-liveness test, or successful static-library build as Tekken gameplay.
- Keep all source revisions pinned and record exact build provenance.
