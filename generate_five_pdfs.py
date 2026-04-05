# generate_five_pdfs.py
# Converts the five updated Wincham HTML documents to PDF using
# Microsoft Edge or Chrome headless renderer.
# Run from: c:\DAD\UK_Lanzarote_Repatriation

import os
import subprocess
import time

SUBFOLDER = r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham Scheme-Legal Claims-Victims"


TARGET_FILES = [
    "Wincham_Pitch_Report_For_Law_Firms",
    "Wincham_Pitch_Report_EXTERNAL",
    "Wincham_Public_Evidence_Dossier",
    "Wincham_ICAEW_Disciplinary_Referral",
    "Wincham_Nine_Task_Verification_Report",
]

# ── Find a Chromium-based browser ────────────────────────────────────────────
BROWSER_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
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

success = 0
failed  = 0

for stem in TARGET_FILES:
    src = os.path.join(SUBFOLDER, stem + ".html")
    dst = os.path.join(SUBFOLDER, stem + ".pdf")

    if not os.path.exists(src):
        print(f"  ✗  {stem}.html  NOT FOUND — skipping")
        failed += 1
        continue

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
        "--disable-extensions",
        "--disable-dev-shm-usage",
        file_url,
    ]

    print(f"  → Generating: {stem}.pdf", end="", flush=True)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        time.sleep(3)  # let browser flush before spawning next instance

        if os.path.exists(dst) and os.path.getsize(dst) > 1024:
            size_kb = round(os.path.getsize(dst) / 1024, 1)
            print(f"  ✓  ({size_kb} KB)")
            success += 1
        else:
            print(f"  ✗  FAILED (empty or missing output)")
            if result.stderr:
                print(f"     stderr: {result.stderr[:400]}")
            failed += 1

    except subprocess.TimeoutExpired:
        print(f"  ✗  TIMED OUT after 120s")
        failed += 1
    except Exception as e:
        print(f"  ✗  ERROR: {e}")
        failed += 1

print(f"\n{'─'*55}")
print(f"  Done.  {success} succeeded  |  {failed} failed")
print(f"  Output folder: {SUBFOLDER}")
print(f"{'─'*55}")
