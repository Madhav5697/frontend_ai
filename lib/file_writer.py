"""
file_writer.py
---------------
Handles creation and writing of the generated website files:
- index.html
- styles.css
- app.js

This module builds the basic HTML structure linking the CSS and JS files,
and writes them into the ./out/ directory.
"""

import os
from pathlib import Path

# Path to the output folder
OUT_DIR = Path.cwd() / "out"


def ensure_out_dir():
    """
    Ensure that the ./out directory exists.
    Creates it if it doesn't.
    """
    OUT_DIR.mkdir(exist_ok=True)


def write_files(html: str, css: str, js: str):
    """
    Write the generated HTML, CSS, and JS files into ./out directory.
    Wraps HTML with a minimal base template linking the stylesheet and script.

    Args:
        html (str): HTML markup from LLM output
        css (str): CSS styles from LLM output
        js (str): JavaScript code from LLM output
    """
    ensure_out_dir()

    # Construct the index.html file content
    index_content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LLM-generated site</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
{html}

<script src="./app.js" defer></script>
</body>
</html>"""

    # Write index.html
    with open(OUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_content)

    # Write styles.css
    with open(OUT_DIR / "styles.css", "w", encoding="utf-8") as f:
        f.write(css or "/* empty */")

    # Write app.js
    with open(OUT_DIR / "app.js", "w", encoding="utf-8") as f:
        f.write(js or "// empty")

    print(f"[+] Files written successfully in: {OUT_DIR}")


def clear_out_dir():
    """
    Optional helper: clears old files from the ./out directory
    before writing new ones.
    """
    if OUT_DIR.exists():
        for file in OUT_DIR.iterdir():
            try:
                file.unlink()
            except Exception:
                pass
