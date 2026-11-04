#!/usr/bin/env python3
"""Replace ReXGlue's C++20 jthread use with an equivalent joinable std::thread for PS5 libc++."""
from pathlib import Path
import argparse

REPLACEMENTS = [
    ("    dispatch_thread_ =\n        std::jthread([this](std::stop_token stop_token) { TimerThreadMain(stop_token); });",
     "    dispatch_thread_ = std::thread([this] { TimerThreadMain(); });"),
    ("    dispatch_thread_.request_stop();",
     "    stop_requested_.store(true, std::memory_order_release);"),
    ("    // std::jthread auto-joins on destruction",
     "    if (dispatch_thread_.joinable()) dispatch_thread_.join();"),
    ("  void TimerThreadMain(std::stop_token stop_token) {",
     "  void TimerThreadMain() {"),
    ("    while (!stop_token.stop_requested()) {",
     "    while (!stop_requested_.load(std::memory_order_acquire)) {"),
    ("  std::jthread::id dispatch_thread_id() const { return dispatch_thread_.get_id(); }",
     "  std::thread::id dispatch_thread_id() const { return dispatch_thread_.get_id(); }"),
    ("  std::jthread dispatch_thread_;",
     "  std::thread dispatch_thread_;\n  std::atomic<bool> stop_requested_{false};"),
]

def patch(path: Path) -> bool:
    source = path.read_text()
    if "#include <atomic>" not in source:
        marker = "#include <algorithm>\n"
        if source.count(marker) != 1:
            raise ValueError("Could not find unique standard include insertion point")
        source = source.replace(marker, marker + "#include <atomic>\n#include <thread>\n", 1)
    changed = False
    for old, new in REPLACEMENTS:
        if old in source:
            if source.count(old) != 1:
                raise ValueError(f"Expected one occurrence of: {old[:72]!r}")
            source = source.replace(old, new, 1)
            changed = True
        elif new not in source:
            raise ValueError(f"Neither original nor patched code found: {old[:72]!r}")
    if "std::jthread" in source or "std::stop_token" in source:
        raise ValueError("C++20 jthread/stop_token use remains after patch")
    if changed or path.read_text() != source:
        path.write_text(source)
    return changed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sdk_root", type=Path)
    args = parser.parse_args()
    target = args.sdk_root / "src/core/timer_queue.cpp"
    if not target.is_file():
        parser.error(f"Missing pinned ReXGlue source: {target}")
    changed = patch(target)
    print("Applied Prospero std::thread timer-queue compatibility patch." if changed else "Prospero timer-queue patch already present.")
if __name__ == "__main__":
    main()
