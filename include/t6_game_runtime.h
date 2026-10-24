#pragma once
// SPDX-License-Identifier: MIT
//
// Stable boundary between the generated Tekken 6 runtime and platform/netplay
// code. This is an adapter contract, not an implementation of the game.
// Generated ReXGlue code must be wrapped to this API; do not assume its raw
// entry points or state layout already match these signatures.

#include <cstddef>
#include <cstdint>

namespace t6::runtime {

// Captured once for a simulation frame. Rollback must replay this exact value,
// not resample the physical controller while resimulating.
struct FrameInput {
  std::uint32_t buttons = 0;
  std::int16_t left_x = 0;
  std::int16_t left_y = 0;
  std::int16_t right_x = 0;
  std::int16_t right_y = 0;
  std::uint8_t left_trigger = 0;
  std::uint8_t right_trigger = 0;
  std::uint8_t player = 0;
  std::uint8_t reserved = 0;
};

static_assert(sizeof(FrameInput) == 16);
static_assert(alignof(FrameInput) == alignof(std::uint32_t));

// The generated-game adapter owns any opaque runtime state. State snapshots
// must include every value that can affect future simulation: game memory,
// RNG state, frame counters and relevant scheduler state. They must not include
// renderer/audio-device state, sockets, or wall-clock timestamps.
struct GameCallbacks {
  void* user = nullptr;

  // Returns 0 on success. Called once before the first simulation frame.
  int (*initialize)(void* user) = nullptr;
  void (*shutdown)(void* user) = nullptr;

  // Advances exactly one deterministic simulation frame using captured input.
  // The adapter must not poll hardware or use wall-clock time here.
  int (*advance_frame)(void* user, const FrameInput* inputs,
                       std::size_t input_count) = nullptr;

  // Snapshot API used by rollback. Required size must be stable for a given
  // game build/configuration. save/load return 0 on success.
  std::size_t (*state_size)(void* user) = nullptr;
  int (*save_state)(void* user, void* destination,
                    std::size_t destination_size) = nullptr;
  int (*load_state)(void* user, const void* source,
                    std::size_t source_size) = nullptr;
};

constexpr bool callbacks_complete(const GameCallbacks& callbacks) noexcept {
  return callbacks.initialize != nullptr &&
         callbacks.shutdown != nullptr &&
         callbacks.advance_frame != nullptr &&
         callbacks.state_size != nullptr &&
         callbacks.save_state != nullptr &&
         callbacks.load_state != nullptr;
}

}  // namespace t6::runtime
