# lib/parser.py
"""
parser.py
---------
Parse and normalize model output into a dict with keys:
  {"html": "...", "css": "...", "js": "..."}

Strategy:
1. Try to parse the whole text as JSON.
2. If that fails, try to extract the first {...} JSON block and parse it.
3. If still failing, use HTML heuristics to extract:
   - content inside <body>...</body> as html
   - content inside first <style>...</style> as css
   - content inside first <script>...</script> as js
4. If none of the above yields useful output, raise ValueError.
"""

from typing import Dict, Optional
import json
import re


def _extract_first_json_block(text: str) -> Optional[str]:
    """
    Return the first {...} substring found in text (best-effort).
    Strips surrounding markdown fences if present.
    """
    if not text:
        return None
    # Remove common markdown fences (```json ... ```)
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)

    # Find first balanced-looking JSON object using a regex (best-effort)
    m = re.search(r"\{[\s\S]*\}", text)
    return m.group(0) if m else None


def _extract_html_parts(text: str) -> Dict[str, str]:
    """
    Heuristically extract html, css, js from text containing HTML.
    Returns dict with keys 'html','css','js' (empty strings when not found).
    """
    html = ""
    css = ""
    js = ""

    # Extract <style> contents
    style_m = re.search(r"<style[^>]*>([\s\S]*?)</style>", text, flags=re.IGNORECASE)
    if style_m:
        css = style_m.group(1).strip()

    # Extract first <script> contents that is not a src include
    script_m = re.search(r"<script\b(?:(?!src)[\s\S])*?>([\s\S]*?)</script>", text, flags=re.IGNORECASE)
    if script_m:
        js = script_m.group(1).strip()
    else:
        # fallback: any <script> content
        script_m2 = re.search(r"<script[^>]*>([\s\S]*?)</script>", text, flags=re.IGNORECASE)
        if script_m2:
            js = script_m2.group(1).strip()

    # Extract <body> inner HTML (preferred)
    body_m = re.search(r"<body[^>]*>([\s\S]*?)</body>", text, flags=re.IGNORECASE)
    if body_m:
        html = body_m.group(1).strip()
    else:
        # If whole text looks like full HTML, return it as html
        if "<html" in text.lower():
            # remove any <head> (we keep body-like content)
            # simple approach: remove <head>...</head>
            no_head = re.sub(r"<head[\s\S]*?>[\s\S]*?</head>", "", text, flags=re.IGNORECASE)
            html = no_head.strip()
        else:
            # Try to extract the first large block-level element like <div>...</div>
            div_m = re.search(r"<(div|main|section|article)[\s\S]*?>[\s\S]*?</\1>", text, flags=re.IGNORECASE)
            if div_m:
                html = div_m.group(0).strip()

    return {"html": html or "", "css": css or "", "js": js or ""}


def parse_model_output(text: str) -> Dict[str, str]:
    """
    Parse model output into {"html":..., "css":..., "js":...}.
    Raises ValueError if parsing fails.
    """
    if not text or not isinstance(text, str):
        raise ValueError("Empty model output")

    # 1) Try direct JSON parse
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and any(k in obj for k in ("html", "css", "js")):
            return {
                "html": obj.get("html", "") or "",
                "css": obj.get("css", "") or "",
                "js": obj.get("js", "") or ""
            }
    except Exception:
        pass

    # 2) Try extracting JSON block and parsing
    block = _extract_first_json_block(text)
    if block:
        try:
            obj = json.loads(block)
            if isinstance(obj, dict) and any(k in obj for k in ("html", "css", "js")):
                return {
                    "html": obj.get("html", "") or "",
                    "css": obj.get("css", "") or "",
                    "js": obj.get("js", "") or ""
                }
        except Exception:
            # If parsing failed, continue to HTML heuristics
            pass

    # 3) HTML heuristics
    parts = _extract_html_parts(text)
    if any(parts[k].strip() for k in ("html", "css", "js")):
        return parts

    # 4) If we reach here, nothing useful was found
    raise ValueError("Unable to parse model output into html/css/js")
