"""
rebuild_and_publish.py
──────────────────────
Run this script whenever you have finished making changes to any .md file.

It will:
  1. Rebuild all HTML files from the .md source files
  2. Rebuild all PDFs from the HTML files (using Chrome)
  3. Copy the 8 final PDFs into the distribution subfolder

Nothing is deleted. Existing files in the subfolder are simply overwritten
with the latest versions.
"""

import os
import shutil
import subprocess
import sys

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE        = r"C:\DAD\UK_Lanzarote_Repatriation"
SCRIPTS     = BASE
WINCHAM_DIR = os.path.join(BASE, "Wincham Legal Case UK Type Class Action")
PUBLISH_DIR = os.path.join(WINCHAM_DIR, "Wincham Scheme-Legal Claims-Victims")

# The 8 PDFs that go into the distribution subfolder
PUBLISH_PDFS = [
    "Wincham_Pitch_Report_EXTERNAL.pdf",
    "Wincham_Pitch_Report_For_Law_Firms.pdf",
    "Ellis_Briefing_Document.pdf",
    "Wincham_NDA_Non_Circumvention.pdf",
    "Wincham_Data_Licence_Agreement.pdf",
    "Dean_Ellis_Introduction_Fee_Agreement.pdf",
    "Wincham_Legal_Lead_Generation_Business_Plan.pdf",
    "Wincham_Public_Evidence_Dossier.pdf",
]

def banner(msg):
    print(f"\n{'─'*60}")
    print(f"  {msg}")
    print(f"{'─'*60}")

def run_script(script_name):
    path = os.path.join(SCRIPTS, script_name)
    print(f"\n▶  Running {script_name} …\n")
    result = subprocess.run([sys.executable, path], cwd=SCRIPTS)
    if result.returncode != 0:
        print(f"\n⚠  {script_name} exited with an error.")
        return False
    return True

def copy_pdfs():
    banner("Step 3 — Copying PDFs to distribution folder")
    os.makedirs(PUBLISH_DIR, exist_ok=True)
    ok, missing = [], []
    for fname in PUBLISH_PDFS:
        src = os.path.join(WINCHAM_DIR, fname)
        dst = os.path.join(PUBLISH_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            size_kb = round(os.path.getsize(dst) / 1024, 1)
            print(f"  ✓  {fname}  ({size_kb} KB)")
            ok.append(fname)
        else:
            print(f"  ✗  {fname}  NOT FOUND — was the PDF generated correctly?")
            missing.append(fname)
    return ok, missing

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    banner("Step 1 — Rebuilding HTML files from Markdown sources")
    if not run_script("convert_all_md.py"):
        print("Stopping early — fix the HTML conversion issue first.")
        sys.exit(1)

    banner("Step 2 — Rebuilding PDFs from HTML files (using Chrome)")
    if not run_script("convert_html_to_pdf.py"):
        print("Stopping early — fix the PDF conversion issue first.")
        sys.exit(1)

    ok, missing = copy_pdfs()

    banner("All done")
    print(f"  {len(ok)} PDF(s) published to:")
    print(f"  {PUBLISH_DIR}")
    if missing:
        print(f"\n  ⚠  {len(missing)} file(s) were not copied (see above).")
    print()
