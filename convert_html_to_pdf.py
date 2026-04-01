"""
Convert all HTML files in the Wincham Legal Case folder to PDF
using Microsoft Edge (or Chrome) headless renderer.
"""
import os
import subprocess
import time

FOLDER = r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action"

# ── Find a Chromium-based browser ────────────────────────────────────────────
BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

browser = next((b for b in BROWSER_CANDIDATES if os.path.exists(b)), None)

if not browser:
    print("ERROR: Neither Microsoft Edge nor Google Chrome was found.")
    print("Checked paths:")
    for b in BROWSER_CANDIDATES:
        print(f"  {b}")
    exit(1)

browser_name = "Edge" if "edge" in browser.lower() else "Chrome"
print(f"Browser : {browser_name}")
print(f"Path    : {browser}")
print()

# ── Find HTML files ───────────────────────────────────────────────────────────
html_files = sorted(f for f in os.listdir(FOLDER) if f.lower().endswith(".html"))
print(f"Found {len(html_files)} HTML file(s):\n")

# ── Convert each file ─────────────────────────────────────────────────────────
success = 0
failed  = 0

for fname in html_files:
    src  = os.path.join(FOLDER, fname)
    stem = os.path.splitext(fname)[0]
    dst  = os.path.join(FOLDER, stem + ".pdf")

    # Build file:// URL (Windows-safe)
    file_url = "file:///" + src.replace("\\", "/").replace(" ", "%20")

    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={dst}",
        "--no-pdf-header-footer",
        file_url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        time.sleep(2)  # let Edge fully release before spawning next instance

        if os.path.exists(dst) and os.path.getsize(dst) > 1024:
            size_kb = round(os.path.getsize(dst) / 1024, 1)
            print(f"  ✓  {stem}.pdf  ({size_kb} KB)")
            success += 1
        else:
            print(f"  ✗  {fname}  FAILED (empty or missing output)")
            if result.stderr:
                print(f"     {result.stderr[:300]}")
            failed += 1

    except subprocess.TimeoutExpired:
        print(f"  ✗  {fname}  TIMED OUT")
        failed += 1
    except Exception as e:
        print(f"  ✗  {fname}  ERROR: {e}")
        failed += 1

print(f"\n{'─'*50}")
print(f"  Done.  {success} succeeded  |  {failed} failed")
print(f"{'─'*50}")
