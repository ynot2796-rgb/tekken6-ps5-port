# First-boot native diagnostic

This source is the first milestone for the native PS5 title route. It sends a
notification if launched and exits after 15 seconds. It is not Tekken 6 and
does not test the renderer, controllers, network, GGPO or matchmaking.

## Build approach

Use the public [ps5link SDK](https://github.com/Rufidj/ps5link-sdk) with its
matching ps5-payload-sdk compiler and SharpProspero signing tool. The SDK's
documented title process is: compile with `prospero-clang`, link with
`linker/link_real` and `linker/crt1_ps5.o`, then sign the ELF into
`eboot.bin`.

The complete ShadowMountPlus folder also needs a runtime module under
`sce_module/libc.prx` compatible with the target firmware. That Sony-owned
file is not included here. A locally supplied runtime must be legitimate,
signed, and compatible; do not download random PRX files from untrusted sites.

## Install target

The intended folder name is `PPSA99873`, with this metadata and the signed
`eboot.bin`. Copy the finished folder into a configured ShadowMountPlus scan
path such as `/data/homebrew/PPSA99873`.

Title ID `PPSA99873` is a proposed development ID; verify it is not already
registered on the console before use. Reusing an ID can cause cached metadata
or stale app files to appear.

## Acceptance test

- Build the current source from a clean checkout.
- Verify `eboot.bin`, metadata, and required runtime module exist.
- Register the folder with the user's ShadowMountPlus version.
- Launch it from the home screen on firmware 13.60.
- Confirm the notification appears; capture kernel logs if it fails.

No working package is claimed until these checks pass on the target console.
