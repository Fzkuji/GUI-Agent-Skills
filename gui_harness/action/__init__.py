"""
gui_harness.action — desktop control: mouse, keyboard, clipboard, window management.

Split into modules:
  click.py     — mouse click, double_click, right_click, drag
  keyboard.py  — key_press, key_combo, type_text, paste_text
  clipboard.py — set_clipboard, get_clipboard
  window.py    — get_frontmost_app, activate_app, get_window_bounds
  gui_action.py — unified CLI interface
  backends/    — platform-specific backends (http_remote, mac_local)
"""
