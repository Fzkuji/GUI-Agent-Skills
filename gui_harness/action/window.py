"""
gui_harness.action.window — window management operations.

Includes: get_frontmost_app, activate_app, get_window_bounds.
"""

from __future__ import annotations

import platform
import subprocess
import time

SYSTEM = platform.system()


def get_frontmost_app():
    """Get the name of the currently frontmost application."""
    if SYSTEM == "Darwin":
        try:
            r = subprocess.run(["osascript", "-e",
                'tell application "System Events" to return name of first process whose frontmost is true'],
                capture_output=True, text=True, timeout=5)
            return r.stdout.strip()
        except Exception:
            return "unknown"
    else:
        raise NotImplementedError(f"{SYSTEM} get_frontmost_app not yet implemented")


def verify_frontmost(expected_app):
    """Check if the expected app is still frontmost. Returns (is_correct, actual_app)."""
    actual = get_frontmost_app()
    return actual == expected_app, actual


def activate_app(app_name):
    """Bring app window to front."""
    if SYSTEM == "Darwin":
        try:
            subprocess.run(["osascript", "-e",
                f'tell application "System Events" to set frontmost of process "{app_name}" to true'],
                capture_output=True, timeout=5)
            time.sleep(0.3)
        except Exception:
            subprocess.run(["open", "-a", app_name], capture_output=True, timeout=5)
            time.sleep(0.5)
    elif SYSTEM == "Windows":
        raise NotImplementedError("Windows activate_app not yet implemented")
    else:
        raise NotImplementedError("Linux activate_app not yet implemented")


def get_window_bounds(app_name):
    """Get window position and size: (x, y, w, h)."""
    if SYSTEM == "Darwin":
        try:
            r = subprocess.run(["osascript", "-l", "JavaScript", "-e", f'''
var se = Application("System Events");
var ws = se.processes["{app_name}"].windows();
var best = null;
var bestArea = 0;
for (var i = 0; i < ws.length; i++) {{
    try {{
        var p = ws[i].position();
        var s = ws[i].size();
        var area = s[0] * s[1];
        if (area > bestArea) {{
            bestArea = area;
            best = [p[0], p[1], s[0], s[1]];
        }}
    }} catch(e) {{}}
}}
if (best) best.join(","); else "";
'''], capture_output=True, text=True, timeout=5)
            parts = r.stdout.strip().split(",")
            if len(parts) == 4:
                return tuple(int(x) for x in parts)
        except Exception:
            pass
        return None
    else:
        raise NotImplementedError(f"{SYSTEM} get_window_bounds not yet implemented")
