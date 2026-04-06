"""
gui_harness.action.input — backward-compatible re-exports.

All functions are now split into separate modules:
  click.py, keyboard.py, clipboard.py, window.py

This file re-exports everything so existing code that imports
from gui_harness.action.input continues to work.
"""

# Mouse operations
from gui_harness.action.click import (
    mouse_click,
    mouse_move,
    mouse_double_click,
    mouse_right_click,
    mouse_drag,
    click_at,
)

# Keyboard operations
from gui_harness.action.keyboard import (
    key_press,
    key_combo,
    type_text,
    paste_text,
    send_keys,
)

# Clipboard operations
from gui_harness.action.clipboard import (
    set_clipboard,
    get_clipboard,
)

# Window management
from gui_harness.action.window import (
    get_frontmost_app,
    verify_frontmost,
    activate_app,
    get_window_bounds,
)
