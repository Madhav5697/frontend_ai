"""
llm_gemini.py
--------------
Handles all communication with the Gemini API.

This version fixes the "Please use a valid role: user, model." error by
sending a single 'user' part containing both the instruction and the prompt.
"""

import os
import requests
from typing import Optional

# Base Gemini REST endpoint (v1beta)
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Call the Gemini REST API and return the model's text output.

    Args:
        prompt (str): The user's natural-language instruction.
        model (str): Model name (default 'gemini-2.5-flash').

    Returns:
        str: The text response from Gemini (ideally JSON).
    """
    # Load API key
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("❌ Missing GEMINI_API_KEY. Add it in your .env file.")

    url = BASE_URL.format(model=model)

    # System-like instruction (we will send it inside a single user message)
    system_instruction = (
        "You are a code generator. Respond ONLY with valid JSON in this exact format:\n"
        '{"html":"...","css":"...","js":"..."}\n'
        "No explanations, markdown, or extra text. Do not use external <script src> or <link> tags."
    )

    # Combine instruction + user prompt into a single 'user' part (allowed by this API)
    full_user_text = system_instruction + "\n\nUser prompt:\n" + prompt

    body = {
        "contents": [
            {"role": "user", "parts": [{"text": full_user_text}]}
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2000,
            # request application/json to encourage structured output
            "responseMimeType": "application/json"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": key
    }

    resp = requests.post(url, json=body, headers=headers, timeout=60)
    if not resp.ok:
        # Raise detailed error so caller can see server reply
        raise RuntimeError(f"Gemini API Error {resp.status_code}: {resp.text}")

    # Parse JSON safely
    try:
        data = resp.json()
    except Exception:
        # If response is not JSON, return raw text
        return resp.text

    # --- Extract text field from Gemini response ---
    # Responses vary; try a few common paths then fallback to the first string found.
    possible_paths = [
        # candidate -> content -> text
        (lambda d: d.get("candidates", [{}])[0].get("content", [{}])[0].get("text") if d.get("candidates") else None),
        # outputs -> content -> text
        (lambda d: d.get("outputs", [{}])[0].get("content", [{}])[0].get("text") if d.get("outputs") else None),
        # output -> content -> text
        (lambda d: d.get("output", [{}])[0].get("content", [{}])[0].get("text") if d.get("output") else None),
        # sometimes content is nested differently
        (lambda d: (d.get("candidates") or [{}])[0].get("content") if isinstance((d.get("candidates") or [{}])[0].get("content"), str) else None),
    ]

    for fn in possible_paths:
        try:
            p = fn(data)
            if p:
                return p
        except Exception:
            continue

    # Fallback: find first text-like string in JSON recursively
    def find_text(obj) -> Optional[str]:
        if obj is None:
            return None
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):
            for i in obj:
                t = find_text(i)
                if t:
                    return t
        if isinstance(obj, dict):
            # prefer keys likely to contain text
            for k in ("text", "content", "message", "output", "parts"):
                if k in obj:
                    t = find_text(obj[k])
                    if t:
                        return t
            for v in obj.values():
                t = find_text(v)
                if t:
                    return t
        return None

    text = find_text(data)
    if text:
        return text

    # Final fallback: raw response text
    return resp.text
