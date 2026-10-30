#!/usr/bin/env python3
"""Regression test for the pinned ReXGlue timer-queue compatibility patch."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

script = Path(__file__).resolve().parents[1] / "tools" / "patch_rexglue_jthread.py"
spec = importlib.util.spec_from_file_location("patch_rexglue_jthread", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

fixture = """#include <algorithm>
#include <forward_list>
class TimerQueue {
 public:
  TimerQueue() {
    dispatch_thread_ =
        std::jthread([this](std::stop_token stop_token) { TimerThreadMain(stop_token); });
  }
  ~TimerQueue() {
    dispatch_thread_.request_stop();
    // Kick dispatch thread to check stop token
    // std::jthread auto-joins on destruction
  }
  void TimerThreadMain(std::stop_token stop_token) {
    while (!stop_token.stop_requested()) {}
  }
  std::jthread::id dispatch_thread_id() const { return dispatch_thread_.get_id(); }
 private:
  std::jthread dispatch_thread_;
};
"""
with TemporaryDirectory() as tmp:
    path = Path(tmp) / "timer_queue.cpp"
    path.write_text(fixture)
    assert module.patch(path) is True
    result = path.read_text()
    assert "std::jthread" not in result
    assert "std::stop_token" not in result
    assert "std::thread dispatch_thread_" in result
    assert "std::atomic<bool> stop_requested_{false}" in result
    assert "dispatch_thread_.join()" in result
    assert module.patch(path) is False
print("ReXGlue Prospero timer-queue compatibility tests passed.")
