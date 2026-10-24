#pragma once
// SPDX-License-Identifier: MIT
//
// Convert a platform-neutral, already button-mapped pad sample into the exact
// input record consumed by one deterministic simulation frame. The PS5 poller
// owns scePadReadState and button-layout interpretation; this header deliberately
// does not assume an undocumented raw SDK structure or button bit assignment.

#include "t6_game_runtime.h"

#include <cstdint>

namespace t6::runtime {

// Axes use the common unsigned 8-bit range returned by the current PS5 pad
// adapter: 0 is minimum, 128 is center, 255 is maximum. Button bits must already
// be translated to the port's stable game-action mask by the platform adapter.
struct PadSample {
  std::uint32_t game_buttons = 0;
  std::uint8_t left_x = 128;
  std::uint8_t left_y = 128;
  std::uint8_t right_x = 128;
  std::uint8_t right_y = 128;
  std::uint8_t left_trigger = 0;
  std::uint8_t right_trigger = 0;
  bool connected = false;
};

constexpr std::int16_t normalize_axis(std::uint8_t value) noexcept {
  const int delta = static_cast<int>(value) - 128;
  if (delta < 0) return static_cast<std::int16_t>((delta * 32768) / 128);
  return static_cast<std::int16_t>((delta * 32767) / 127);
}

// Capture once before advancing a simulation frame. Disconnected controllers
// produce neutral input; rollback must store/replay this result and must never
// call this function to resample hardware during resimulation.
constexpr FrameInput capture_frame_input(const PadSample& sample,
                                         std::uint8_t player) noexcept {
  FrameInput result{};
  result.player = player;
  if (!sample.connected) return result;
  result.buttons = sample.game_buttons;
  result.left_x = normalize_axis(sample.left_x);
  result.left_y = normalize_axis(sample.left_y);
  result.right_x = normalize_axis(sample.right_x);
  result.right_y = normalize_axis(sample.right_y);
  result.left_trigger = sample.left_trigger;
  result.right_trigger = sample.right_trigger;
  return result;
}

}  // namespace t6::runtime
