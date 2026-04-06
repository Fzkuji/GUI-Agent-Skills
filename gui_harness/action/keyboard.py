"""
gui_harness.action.keyboard — keyboard operations.

Includes: key_press, key_combo, type_text, paste_text, send_keys.
Uses pynput for cross-platform keyboard control.
"""

from __future__ import annotations

import platform
import subprocess
import time

SYSTEM = platform.system()


def _resolve_key(name):
    """Resolve a key name string to pynput Key or KeyCode."""
    from pynput.keyboard import Key, KeyCode

    key_map = {
        "return": Key.enter, "enter": Key.enter,
        "tab": Key.tab,
        "esc": Key.esc, "escape": Key.esc,
        "space": Key.space,
        "delete": Key.backspace, "backspace": Key.backspace,
        "fwd-delete": Key.delete,
        "up": Key.up, "arrow-up": Key.up,
        "down": Key.down, "arrow-down": Key.down,
        "left": Key.left, "arrow-left": Key.left,
        "right": Key.right, "arrow-right": Key.right,
        "home": Key.home, "end": Key.end,
        "page-up": Key.page_up, "page-down": Key.page_down,
        "pageup": Key.page_up, "pagedown": Key.page_down,
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
        "shift": Key.shift, "ctrl": Key.ctrl, "control": Key.ctrl,
        "alt": Key.alt, "option": Key.alt,
        "command": Key.cmd, "cmd": Key.cmd, "super": Key.cmd,
    }

    lower = name.lower()
    if lower in key_map:
        return key_map[lower]

    if len(name) == 1:
        return KeyCode.from_char(name)

    return None


def key_press(key_name):
    """Press and release a single key."""
    from pynput.keyboard import Controller
    kb = Controller()
    key = _resolve_key(key_name)
    if key:
        kb.press(key)
        kb.release(key)
    else:
        raise ValueError(f"Unknown key: {key_name}")


def key_combo(*keys):
    """Press a key combination.

    Examples: key_combo("command", "v"), key_combo("command", "shift", "s")
    """
    from pynput.keyboard import Controller
    kb = Controller()
    resolved = [_resolve_key(k) for k in keys]
    if any(k is None for k in resolved):
        bad = [keys[i] for i, k in enumerate(resolved) if k is None]
        raise ValueError(f"Unknown keys: {bad}")

    for k in resolved:
        kb.press(k)
    time.sleep(0.05)
    for k in reversed(resolved):
        kb.release(k)


def type_text(text):
    """Type text character by character. Works for ASCII.
    For CJK/special chars, use paste_text() instead.
    """
    from pynput.keyboard import Controller
    kb = Controller()
    kb.type(text)


def paste_text(text):
    """Paste text via clipboard (works for all languages including CJK)."""
    from gui_harness.action.clipboard import set_clipboard
    set_clipboard(text)
    time.sleep(0.1)
    key_combo("command" if SYSTEM == "Darwin" else "ctrl", "v")


def send_keys(combo_string):
    """Parse and execute a key combo string like "command-v", "command-shift-s", "return"."""
    parts = combo_string.lower().split("-")
    if len(parts) == 1:
        key_press(parts[0])
    else:
        key_combo(*parts)
