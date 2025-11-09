"""
lib package

This folder contains helper modules for the LLM Local Deployer project.

Modules:
- llm_gemini.py : Handles Gemini API requests.
- parser.py     : Extracts and parses JSON/HTML from model outputs.
- sanitizer.py  : Removes unsafe or network-related JS.
- file_writer.py: Writes HTML/CSS/JS files to ./out directory.
- utils.py      : Helper utilities (HTML escaping, env checks, etc.)
"""

# Optional: import key modules for convenience when doing `from lib import ...`
from . import llm_gemini, parser, sanitizer, file_writer, utils

__all__ = ["llm_gemini", "parser", "sanitizer", "file_writer", "utils"]
