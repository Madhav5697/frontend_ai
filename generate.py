import os
import re
import time
from dotenv import load_dotenv
import google.generativeai as genai
import http.server
import socketserver
import webbrowser

# -----------------------------
# 1. Load API key
# -----------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env or environment variables.")
    exit()

genai.configure(api_key=api_key)
model_name = "gemini-2.0-flash"

# -----------------------------
# 2. User prompt
# -----------------------------
user_prompt = input("💡 Enter your prompt (e.g. 'make a to-do list website'): ")

# -----------------------------
# 3. Meta prompt (forces correct filenames and syntax)
# -----------------------------
meta_prompt = f"""
You are an expert web developer AI.

The user asked: "{user_prompt}"

Automatically break the request into parts and produce full valid code.

Follow this structure exactly:

[HTML]
Full valid HTML5 code.
It must reference:
  <link rel="stylesheet" href="styles.css">
  <script src="app.js"></script>

[CSS]
Full valid CSS3 code for styles.css

[JS]
Full valid vanilla JavaScript code for app.js

Use these filenames only:
  HTML → index.html
  CSS  → styles.css
  JS   → app.js

Return only runnable code, no explanations or commented text.
"""

# -----------------------------
# 4. Generate content
# -----------------------------
print("\n🌐 Gemini Local Web Generator\n--------------------------------")

start_time = time.time()

try:
    print("⏳ Generating website files...\n")
    model = genai.GenerativeModel(model_name)

    for attempt in range(3):
        try:
            response = model.generate_content(meta_prompt)
            break
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                print("🔁 Retrying in 5 seconds...\n")
                time.sleep(5)
            else:
                raise e

    text = response.text or ""

    # -----------------------------
    # 5. Clean and save files in 'out/' folder
    # -----------------------------
    output_dir = os.path.join(os.path.dirname(__file__), "out")
    os.makedirs(output_dir, exist_ok=True)

    def clean_code(code: str) -> str:
        """Cleans markdown fences and removes comment lines."""
        code = re.sub(r"^```[a-zA-Z]*", "", code, flags=re.MULTILINE)  # remove ```javascript, ```html
        code = re.sub(r"```", "", code)                                # remove closing ```
        code = re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)        # remove HTML comments
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)         # remove JS/CSS block comments
        code = re.sub(r"^\s*//.*$", "", code, flags=re.MULTILINE)      # remove single-line JS comments
        return code.strip()

    if "[HTML]" in text:
        html = text.split("[HTML]")[1].split("[CSS]")[0].strip() if "[CSS]" in text else text.split("[HTML]")[1].strip()
        html = clean_code(html)
        with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("💾 Saved: out/index.html")

    if "[CSS]" in text:
        css = text.split("[CSS]")[1].split("[JS]")[0].strip() if "[JS]" in text else text.split("[CSS]")[1].strip()
        css = clean_code(css)
        with open(os.path.join(output_dir, "styles.css"), "w", encoding="utf-8") as f:
            f.write(css)
        print("💾 Saved: out/styles.css")

    if "[JS]" in text:
        js = text.split("[JS]")[1].strip()
        js = clean_code(js)
        with open(os.path.join(output_dir, "app.js"), "w", encoding="utf-8") as f:
            f.write(js)
        print("💾 Saved: out/app.js")

    elapsed = round(time.time() - start_time, 2)
    print(f"\n✅ Generation complete in {elapsed} seconds! Files saved in 'out/' folder.\n")

except Exception as e:
    print("❌ Gemini API Error:", e)
    exit()

# -----------------------------
# 6. Serve files locally
# -----------------------------
index_path = os.path.join(output_dir, "index.html")
if not os.path.exists(index_path) or os.path.getsize(index_path) == 0:
    print("⚠️ No valid index.html found in 'out' folder. Generation might have failed.")
else:
    os.chdir(output_dir)
    PORT = 8000
    print(f"\n🚀 Serving website from 'out/' folder at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}/index.html")

    with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        print("🌍 Website running! Press Ctrl + C to stop.")
        httpd.serve_forever()
