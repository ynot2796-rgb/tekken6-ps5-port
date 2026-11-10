# TTT2 PS5 Engineering Reuse Audit

Date: 10 November 2026

## Source and license

Reference project: [PrimetimeFluff/tekken-tag-tournament2-ps5](https://github.com/PrimetimeFluff/tekken-tag-tournament2-ps5).

Its root `LICENSE` is the MIT License, copyright PrimetimeFluff (2026). This permits reuse and modification of covered project code and documentation provided the copyright and permission notice are retained. The reference repository's own engineering and build documentation also warns that its public source snapshot/release materials do not yet establish a fully reproducible clean-machine PS5 build. Treat every component as something to audit and validate, not as a proven turnkey dependency.

This document records engineering practices and integration lessons for Tekken 6. It does not copy game code, binaries, generated game code, game assets, Sony runtime modules, private credentials, or release-package contents.

## What we should reuse

1. **Stage-separated build pipeline.** Keep game-derived code generation, portable host tests, PS5 component compilation, final native linking, signing, and packaging as distinct stages. A successful earlier stage must not be reported as a successful later stage.
2. **Fresh-environment tests.** Run host tests with a new temporary HOME/output directory so stale objects and caches cannot make a broken test pass. Keep fixtures synthetic and independent of the user's game dump.
3. **Pinned dependency provenance.** Record exact upstream commits, patches, compiler/toolchain versions, and hashes for every external dependency. Do not silently mix SDK, Mesa/RADV, DXVK, vkd3d, CRT, or compiler revisions from separate projects.
4. **Generated game inputs stay local.** Generate the Tekken 6 ReXGlue C++ and CPU archive from the user's own compatible game image in a private workspace. Do not commit or upload game-derived files to public GitHub or public CI artifacts.
5. **Strict runtime failure gates.** Preserve explicit rejection of unresolved guest imports, unsupported indirect calls, and missing runtime services. Do not replace unknown imports with success stubs to force a link.
6. **Separate compiler work from renderer warmup.** If/when shader translation is integrated, measure bytecode compilation, cache persistence, and graphics-pipeline warmup separately. A completed shader compile pass does not prove rendering pipelines are ready.
7. **Benchmark methodology.** Report input count, compiled/deduplicated/unsupported counts, failures, output count/size, worker count, and whether cache I/O is included. Compare repeated runs under equivalent conditions; do not claim a speedup from a single noisy measurement.
8. **Install validation.** Distinguish ELF creation, title-folder packaging, registration by ShadowMountPlus, and actual launch on the target firmware. Record the exact artifact hash and console result for each test.

## What is not a drop-in reuse

The TTT2 guide documents an architecture built around its own upstream game port, XenonRecomp, PS5 SDK fork, PS5 Mesa/RADV integration, DXVK, vkd3d, FFmpeg, OpenSSL, and generated CPU archive. Those exact dependency commits and build paths are not automatically compatible with Tekken 6's pinned ReXGlue SDK, Xenos plugin, GGPO fork, or our current PS5 SDK/linker setup.

In particular:

- Do not replace our ReXGlue runtime with TTT2's XenonRecomp game runtime. They are different game translation/runtime stacks.
- Do not import TTT2's DXVK/vkd3d/FFmpeg/OpenSSL archives or its modified platform libraries without an ABI, SDK, license, and link-compatibility audit.
- Do not treat TTT2's shader compiler benchmark or worker settings as Tekken 6 performance data.
- Do not assume its title package, firmware behavior, renderer, or input/audio integration is validated for our title.
- Do not copy the TTT2 release executable or any game-specific content.

## Tekken 6 adaptation plan

| Area | Action in this repository | Acceptance evidence |
|---|---|---|
| CI stages | Keep host tests, PS5 compile probes, native link, and package checks separately named | Each workflow reports only the stage it actually completes |
| Dependency pinning | Record exact SDK, ReXGlue, renderer, linker, and runtime revisions | Clean checkout resolves the same revisions |
| ReXGlue generated code | Build from local user-owned game inputs | Generated outputs remain outside tracked/public paths |
| Runtime imports | Keep fail-closed import and indirect-call checks | Negative tests prove unknown imports fail |
| Renderer | First compile and launch a minimal native graphics/input loop using our chosen PS5 graphics stack | Visible frame and controller input confirmed on firmware 13.60 |
| Final link | Link actual Tekken 6 generated target with the verified runtime/platform archives | No unresolved imports; ELF and title metadata validated |
| Package/boot | Package only distributable files and document local runtime requirements | Exact ZIP hash and user-confirmed launch on firmware 13.60 |

## Immediate priority

Use the TTT2 project as a build-engineering reference, not as a replacement architecture. Our next useful comparison is between its documented staged dependency/link requirements and the current Tekken 6 CI jobs. The existing Tekken 6 project already has a separate ReXGlue/GGPO direction; the highest-value reuse is the discipline around provenance, fail-closed linking, clean tests, and honest stage-by-stage validation.

## Attribution

Engineering practices summarized here were informed by the MIT-licensed project [PrimetimeFluff/tekken-tag-tournament2-ps5](https://github.com/PrimetimeFluff/tekken-tag-tournament2-ps5), particularly its `docs/BUILDING.md`, `docs/ENGINEERING.md`, and `docs/REVIEWING.md`. The original project and its contributors retain their respective copyright. Third-party dependencies retain their own licenses.
