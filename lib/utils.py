# lib/utils.py
"""
Utility helpers used across the project.

Functions:
- load_env(): loads .env file if present (uses python-dotenv).
- env_loaded(): returns True if GEMINI_API_KEY or GOOGLE_API_KEY is present.
- escape_html(s): HTML-escape a string for safe display inside <pre>.
- trunc(s, n): truncate a string with a clear marker.
- pretty_json(obj): return pretty-printed JSON string.
- now_ts(): return a simple timestamp string for logging.
"""

import os
import json
from datetime import datetime

try:
    # python-dotenv is optional; if installed, use it to load .env
    from dotenv import load_dotenv as _load_dotenv
except Exception:
    _load_dotenv = None


def load_env(dotenv_path: str = ".env"):
    """
    Load environment variables from a .env file if python-dotenv is installed.
    This is safe to call repeatedly.
    """
    if _load_dotenv:
        _load_dotenv(dotenv_path)


def env_loaded() -> bool:
    """
    Return True if a Gemini/Google API key is available in the environment.
    """
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))


def escape_html(s: str) -> str:
    """
    HTML-escape a string for safe insertion into an HTML page.
    """
    if s is None:
        return ""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))


def trunc(s: str, n: int = 1000) -> str:
    """
    Truncate string s to length n and append a '(truncated)' marker.
    """
    if s is None:
        return ""
    s = str(s)
    if len(s) <= n:
        return s
    return s[:n] + "...(truncated)"


def pretty_json(obj) -> str:
    """
    Return a pretty-printed JSON string for objects (dict/list).
    Falls back to str(obj) for non-serializable objects.
    """
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return str(obj)


def now_ts(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Return current timestamp string for logging.
    """
    return datetime.now().strftime(fmt)


# auto-load .env when module is imported (convenience)
load_env()
