"""
gui_harness.action.click — mouse click operations.

Includes: click, double_click, right_click, drag.
Uses pynput for cross-platform mouse control.
"""

from __future__ import annotations

import time


def mouse_click(x, y, button="left", clicks=1):
    """Click at screen coordinates (logical pixels, integers).
    After clicking, moves cursor to corner so it doesn't pollute screenshots."""
    from pynput.mouse import Button, Controller
    mouse = Controller()
    mouse.position = (int(x), int(y))
    time.sleep(0.05)
    btn = Button.right if button == "right" else Button.left
    mouse.click(btn, int(clicks))
    time.sleep(0.1)
    mouse.position = (1500, 970)


def mouse_move(x, y):
    """Move mouse to screen coordinates."""
    from pynput.mouse import Controller
    mouse = Controller()
    mouse.position = (int(x), int(y))


def mouse_double_click(x, y):
    """Double click at screen coordinates."""
    mouse_click(x, y, clicks=2)


def mouse_right_click(x, y):
    """Right click at screen coordinates."""
    mouse_click(x, y, button="right")


def mouse_drag(start_x, start_y, end_x, end_y, duration=0.5, button="left"):
    """Drag from (start_x, start_y) to (end_x, end_y)."""
    from pynput.mouse import Button, Controller
    mouse = Controller()
    btn = Button.right if button == "right" else Button.left

    mouse.position = (int(start_x), int(start_y))
    time.sleep(0.1)
    mouse.press(btn)
    time.sleep(0.05)

    steps = max(20, int(duration * 60))
    for i in range(1, steps + 1):
        progress = i / steps
        x = start_x + (end_x - start_x) * progress
        y = start_y + (end_y - start_y) * progress
        mouse.position = (int(x), int(y))
        time.sleep(duration / steps)

    mouse.position = (int(end_x), int(end_y))
    time.sleep(0.05)
    mouse.release(btn)
    time.sleep(0.1)
    mouse.position = (1500, 970)


# Convenience alias
click_at = mouse_click
