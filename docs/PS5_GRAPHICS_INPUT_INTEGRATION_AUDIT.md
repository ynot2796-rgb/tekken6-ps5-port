# PS5 graphics and controller integration audit

## Result of the next-step investigation

The current native diagnostic is not a graphics test: `native/first_boot/main.c`
sends a notification and then spins forever. Its black screen is expected. The
next milestone must replace that liveness-only loop with a bounded native
render/input probe before attempting to boot generated Tekken game code.

A public reference project, [TheSimpsonsGame-PS5-Builder](https://github.com/LoZazaMastro/TheSimpsonsGame-PS5-Builder),
documents a native Prospero runtime using Vulkan/RADV for rendering,
`scePad` for DualSense input, and `sceAudioOut` for audio. Its README pins a
specific PS5 Payload SDK and Mesa/RADV source revision and documents title
packaging. This establishes a plausible public implementation route, not
drop-in compatibility with Tekken 6.

Reference findings:
- `prospero/README.md`: pinned build environment, native title packaging,
  and separate user-supplied game-data staging.
- `tools/rexglue-sdk/src/input/prospero/prospero_input_driver.cpp`: maps
  native `scePad` state to the XInput-style state expected by recompiled games.
- `prospero/radv/README.md`: display integration is tied to a specific Mesa
  revision and PS5 SDK; host-side tests do not prove behavior on a real console.
- `prospero/tests/prospero_input_host.cpp`: extensive host-fixture tests cover
  input mapping and edge cases, but mocked native APIs are not a physical PS5
  controller test.

## Integration decision

Do not copy the reference runtime wholesale or mix arbitrary SDK/Mesa versions.
First inventory the reference project's license notices and build pins, then
create a small native graphics/input probe using a single consistent public
PayloadSDK + RADV/Vulkan dependency set. The probe should:
1. initialize the display/graphics API and render a changing, clearly visible
   frame (not just a notification or black clear);
2. poll DualSense input through `scePad` and visibly change a marker/state;
3. log initialization failures and exit/close cleanly where supported;
4. be packaged as a native title and tested on the user's firmware 13.60 console;
5. only after that, become the platform shell for the ReXGlue-generated game
   target and its Xenos graphics-backend replacement.

## Gate before game integration

The current port repository does not yet have a linked Vulkan renderer, native
input loop, generated Tekken game target, or a complete game executable. The
successful GGPO/compatibility builds remain component-level evidence only.
The graphics/input milestone is **not complete** until the probe visibly renders
on the actual PS5 and responds to the controller. Online service endpoints,
certificates, and PC cross-play must remain unclaimed until independently
verified.


## Reuse implementation added

Rather than inventing a renderer or guessing at controller APIs, the repository now
has `.github/workflows/native-ps5-render-input-probe.yml`. It checks out
[Mihawk's PS5 Vulkan Template](https://github.com/mihawk-99/PS5_VulkanTemplate)
at fixed commit `91179df760df1e6c6f2d4d172bc435319d79ff3c`, bootstraps its matching
PS5_Vulkan / Mesa / PayloadSDK stack, generates a separate `PPSA99874` title named
`Tekken 6 Port Probe` from the upstream 3D starter, and packages the result as a
GitHub Actions artifact. This reuses the upstream title lifecycle, RADV/Vulkan
rendering, DualSense platform layer, and build/package scripts instead of copying
unverified API snippets into the old black-screen diagnostic.

The workflow is intentionally a **probe**, not Tekken gameplay: its purpose is to
produce a visible, controller-responsive native title that can be installed and
tested on the target console before ReXGlue game integration. It does not replace
the current diagnostic until the artifact builds successfully and the user verifies
visible output and controller response on firmware 13.60. The workflow is manually
runnable and also runs when this workflow or this audit document changes.

The upstream template's foundation is MIT-licensed; its optional UI kit is
GPL-3.0-or-later. This probe is generated without the optional UI kit. Its stack
still contains separately licensed dependencies, which must remain attributed in
any redistributed source or binary package. The pinned source revision is
recorded in the workflow so future upstream changes do not silently alter this
build.


## Build result and corrected next step (24 October 2026)

The pinned render/input probe was attempted in CI at run
https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40062184218.
Its C++ sources compiled, but the final native link failed with:

`error: no public SDK stub exports required symbol radv_EnumeratePhysicalDevices`

This is a dependency/import-stub compatibility failure. It is not a successful package, and it does not justify adding a fake implementation of a Vulkan entry point. Before retrying the full RADV build, inspect the pinned build tool's import-stub resolution and the exact dependency that declares this import. If the pinned public SDK cannot support it, switch to a compatible pinned renderer/runtime stack rather than mixing unrelated SDK or Mesa revisions.

Input-source review found a more defensible integration reference:
https://github.com/LoZazaMastro/TheSimpsonsGame-PS5-Builder/blob/main/tools/rexglue-sdk/src/input/prospero/prospero_input_driver.cpp
That BSD-3-Clause implementation owns the native pad lifecycle, calls `scePadReadState` into the SDK's typed `PadData`, maps through `MapPadState`, handles device-not-connected/reconnect cases, and exposes XInput-style state to recompiled code. It is a candidate for reuse only after matching the chosen ReXGlue revision, required headers, SDK version, and license notices. It should be preferred over the PS5X360 sample's hard-coded raw pad byte offsets when the same typed adapter is available.

**Current gate:** resolve native renderer import/link compatibility and produce a visible, controller-responsive native title. Only then integrate the generated Tekken runtime and game renderer. No Tekken gameplay package is currently available.


## Second probe attempt — 24 October 2026

Run https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40064368326 compiled all 29 title objects and failed at the same final link check: `no public SDK stub exports required symbol radv_EnumeratePhysicalDevices`. No package artifact was produced. The failure is reproducible; treat it as a toolchain/link-contract problem until the import is traced to its declaring object and expected resolution. Do not add a stub that returns fake device data: that would hide the error and leave the renderer nonfunctional.

The workflow currently combines a pinned PS5_VulkanTemplate revision with a separately cloned PS5_Vulkan checkout. Before another expensive full build, pin and compare the template's expected RADV archive, native linker tool, PayloadSDK fork, and link recipe revisions as one set, then validate the failing symbol against the actual archive and SDK stub tables. The latest public PS5_Vulkan link recipe uses whole-archive for RADV plus a matching platform layer; this is a useful reference for the audit, not yet a verified fix. No visible-render or controller test can happen until an artifact is produced and installed on firmware 13.60.


## Link-stage localization — 24 October 2026

Inspection of the full CI command line narrows the failure further. All 29 objects compile, `prospero-lld` produces `build/ps5/llvm-pie.elf`, and the next command is PS5_Vulkan's `ps5-native-tool link`. That converter rejects the ELF with `no public SDK stub exports required symbol radv_EnumeratePhysicalDevices`. So this is not an ordinary unresolved-symbol error emitted by the ELF linker: the ELF has reached the SDK title-conversion/import validation stage, and the converter cannot associate a RADV-prefixed entry point with a public SDK stub export.

Do not treat the SDK-pin alignment experiment as a fix. The template explicitly pins SDK fork revision `611893fc25ef3e138f5bc2c90d829d8b58174cd2`, whose platform layer includes the `ps5_localeconv` and related libc bindings expected by the RADV title link recipe. PS5_Vulkan's own host tools separately pin `b83202be73e930050e00de0f1b4d9ec46c0391bf`; these are distinct roles in the upstream bootstrap, not evidence that the title SDK should be downgraded. The workflow has been restored to the template's documented SDK pin.

Next investigation: inspect the exact `ps5-native-tool` linker's stub-resolution rules and the RADV archive's exported/undefined symbols at the pinned Mesa revision. Compare with the upstream project's own RADV smoke title, which uses the same RADV link recipe but links a small C smoke-test object and an explicit C++ runtime object. A defensible fix must identify whether the problematic RADV-prefixed symbol is an archive export, an undefined reference, or an entry-point alias expected by the converter; no fake SDK stub should be added.


## Build pipeline correction — 24 October 2026

The render/input probe workflow was updated after the RADV smoke-title linker investigation:

- Pin the sibling `PS5_Vulkan` checkout to `f410e67a0241b3e8edcdbcd2a9b285dfc4a412ed`, rather than following its moving default branch.
- Reuse cached outputs for the pinned RADV release archive, payload SDK, native host tool, control payload, and `libc.prx` across CI retries.
- Patch the pinned upstream `tools/build-radv-title.sh` link invocation to pass `--no-dynamic-linker`, using a strict one-match guard. This follows the documented LLVM 18 weak-entry-point workaround and fails rather than silently drifting if upstream changes the command.

The same workaround is now present in both `native-ps5-radv-smoke.yml` and `native-ps5-render-input-probe.yml`. The workflows have been checked in source for the pinned revision, cache step, patch string, and step order. **A successful CI rerun and an installable artifact are still unverified**; the prior failures did not produce packages. Do not mark the visible-render/controller milestone complete until a package is built and physically tested on the target PS5.


## Verified native probe package — 24 October 2026

The corrected workflow completed successfully: https://github.com/ynot2796-rgb/tekken6-ps5-port/actions/runs/40066666719 (commit `a82e75f8665683b2e7d4ba3bf5d1b852e4451903`). The run passed the pinned RADV/runtime bootstrap, helper tests, patching of the actual generated title's `ps5/tools/link-title.sh`, native build, ZIP package creation, and artifact upload. GitHub reports the `Tekken6-PS5-render-input-probe` artifact at 15,592,796 bytes; download it from the workflow run while it remains available.

This closes the CI package-build gate for the template-based native probe and demonstrates the link-script fix works for that generated title. The probe is based on the PS5 Vulkan template's 3D starter, whose documented controls use the pad sticks for the camera and D-pad for settings navigation. CI success alone does not prove actual render/input behavior on firmware 13.60; that requires installing and running this artifact on the target console.

Next: on-console rendering/input test, then make the Tekken source-generation path repeatable using a user-owned compatible game image. No Tekken 6 native executable or gameplay package has been produced yet. Do not confuse the probe artifact with the finished game.
