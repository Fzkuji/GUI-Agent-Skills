"""
gui_harness.action.clipboard — clipboard operations.

Includes: set_clipboard, get_clipboard.
"""

from __future__ import annotations

import platform
import subprocess

SYSTEM = platform.system()


def set_clipboard(text):
    """Set clipboard content."""
    if SYSTEM == "Darwin":
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE,
                              env={"LANG": "en_US.UTF-8"})
        p.communicate(text.encode("utf-8"))
    elif SYSTEM == "Windows":
        subprocess.run(["clip"], input=text.encode("utf-16le"), check=True)
    else:
        subprocess.run(["xclip", "-selection", "clipboard"],
                       input=text.encode("utf-8"), check=True)


def get_clipboard():
    """Get clipboard content."""
    if SYSTEM == "Darwin":
        r = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return r.stdout
    elif SYSTEM == "Windows":
        r = subprocess.run(["powershell", "-command", "Get-Clipboard"],
                            capture_output=True, text=True)
        return r.stdout.strip()
    else:
        r = subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                            capture_output=True, text=True)
        return r.stdout
