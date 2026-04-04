"""
gui_harness.utils — shared utilities.
"""

import json
import re


def parse_json(reply: str) -> dict:
    """Robustly extract a JSON object from an LLM reply.

    Handles:
    - Pure JSON: {"action": "click", ...}
    - Markdown fenced: ```json\n{...}\n```
    - Mixed text + JSON: "Here's my plan: {"action": ...}"
    - Multiple JSON objects: picks the first valid one
    """
    text = reply.strip()

    # 1. Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown fences
    if "```" in text:
        # Extract content between fences
        match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

    # 3. Find JSON object with regex (handles "text before {json} text after")
    # Look for outermost { ... } that forms valid JSON
    brace_depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if brace_depth == 0:
                start = i
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth == 0 and start is not None:
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    start = None  # try next { ... } block

    # 4. Nothing worked
    raise json.JSONDecodeError(f"No valid JSON found in: {text[:200]}", text, 0)
