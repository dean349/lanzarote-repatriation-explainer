"""
explainer_to_pdf.py  (v2)
Converts explainer.html → document.pdf using headless Edge/Chrome.
Uses Popen + wait instead of subprocess.run to avoid pipe deadlock on Windows.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

SRC = Path(r"C:\DAD\UK_Lanzarote_Repatriation\explainer.html")
DST = Path(r"C:\DAD\UK_Lanzarote_Repatriation\document.pdf")

# ── Find a Chromium-based browser ──────────────────────────────────────────────
BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

browser = next((b for b in BROWSER_CANDIDATES if os.path.exists(b)), None)

if not browser:
    print("ERROR: Neither Microsoft Edge nor Google Chrome was found.")
    sys.exit(1)

browser_name = "Edge" if "edge" in browser.lower() else "Chrome"
print(f"Browser : {browser_name}")
print(f"Input   : {SRC}")
print(f"Output  : {DST}")

if not SRC.exists():
    print(f"ERROR: Source file not found: {SRC}")
    sys.exit(1)

file_url = SRC.as_uri()  # properly encoded file:/// URL

cmd = [
    browser,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={DST}",
    "--no-pdf-header-footer",
    file_url,
]

print("Rendering (this may take ~10-20 seconds)...")
proc = subprocess.Popen(
    cmd,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW,
)
try:
    proc.wait(timeout=120)
except subprocess.TimeoutExpired:
    proc.kill()
    print("✗  TIMED OUT after 120 seconds")
    sys.exit(1)

time.sleep(2)  # give OS time to flush the file

if DST.exists() and DST.stat().st_size > 1024:
    size_kb = round(DST.stat().st_size / 1024, 1)
    print(f"✓  document.pdf created  ({size_kb} KB)")
else:
    print("✗  FAILED — output file missing or empty")
    sys.exit(1)
