# macOS Platform Guide

## Screenshot
```python
import subprocess
subprocess.run(["screencapture", "-x", output_path])
# -x: no sound, saves to file
```

## Input (pynput)
```python
from platform_input import click_at, paste_text, key_press, key_combo

click_at(x, y)                    # Click at logical coordinates
paste_text("hello")               # Paste via clipboard (supports CJK)
key_press("return")               # Single key
key_combo(["command", "s"])       # Key combination (Cmd+S)
```

**Coordinate system:** Logical pixels (Retina displays use 2x scaling).
- Detection space (screencapture) = physical pixels
- Click space (pynput) = logical pixels
- Use `detect_to_click(x, y)` to convert

## Clipboard
```python
import subprocess
# Copy
subprocess.run(["pbcopy"], input=text.encode())
# Paste
result = subprocess.run(["pbpaste"], capture_output=True, text=True)
text = result.stdout
```

## Window Management
```python
import subprocess
# Activate app
subprocess.run(["osascript", "-e", f'tell application "{app_name}" to activate'])
# Get frontmost app
result = subprocess.run(["osascript", "-e", 
    'tell application "System Events" to get name of first application process whose frontmost is true'],
    capture_output=True, text=True)
```

## OCR
Apple Vision framework via `scripts/ui_detector.py`:
```python
from scripts.ui_detector import detect_text
results = detect_text("/path/to/screenshot.png")
# Returns: [{"label": "text", "cx": x, "cy": y, "x": x, "y": y, "w": w, "h": h}, ...]
```

## Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| Save | Cmd+S |
| Copy | Cmd+C |
| Paste | Cmd+V |
| Close window | Cmd+W |
| Quit app | Cmd+Q |
| Undo | Cmd+Z |
| Select all | Cmd+A |
| New tab | Cmd+T |
| Address bar | Cmd+L |

## Notes
- pynput requires Accessibility permissions in System Settings
- `screencapture` captures at Retina resolution (2x)
- AppleScript can automate most native apps
- For CJK text, always use `paste_text()` instead of typing
