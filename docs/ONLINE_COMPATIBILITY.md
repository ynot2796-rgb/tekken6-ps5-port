# Online compatibility checklist

Goal: preserve the existing Native Online ecosystem rather than creating a separate incompatible lobby.

- [ ] Identify the PC release/version to target.
- [ ] Establish whether the official lobby/matchmaking service permits third-party clients.
- [ ] Obtain server endpoint and TLS certificate/pinning behavior from an authorized source.
- [ ] Verify login/guest identity, profile, matchmaking, lobby, and match setup.
- [ ] Verify version gating and game build identity checks.
- [ ] Verify peer connection/NAT traversal behavior.
- [ ] Preserve GGPO packet layout, session start, input delay, rollback window, and disconnect handling.
- [ ] Verify deterministic simulation parity between PC and PS5.
- [ ] Test against a PC player on the same released version.

The public upstream source says official server configuration and the pinned certificate are not published. Do not guess endpoints, bypass TLS, or claim cross-play without a real test.
