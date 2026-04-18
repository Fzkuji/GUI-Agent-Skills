"""Shared constants for gui_harness."""

GUI_SYSTEM_PROMPT = """\
GUI automation context: each call provides a screenshot, OCR results,
and detected UI elements. Identify target elements and their exact
pixel coordinates, decide the action that best advances the task, and
return a structured JSON response as requested.

Rules:
- ALWAYS use coordinates from OCR/detector output — never estimate from visual inspection
- Be precise: wrong coordinates break automation
- Report exactly what you see; do not hallucinate UI elements
"""
