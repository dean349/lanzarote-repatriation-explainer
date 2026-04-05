"""
fetch_ch_curl.py
================
Downloads every available PDF filing from Companies House for
Los Romeros Limited (Company No. 06993349) using curl.exe subprocess calls.

ROOT CAUSE OF PREVIOUS HANG:
  Python subprocess.run(capture_output=True) pipes stdout/stderr via OS pipes.
  Windows pipe buffers are ~64KB. curl.exe tries to write ~100KB of JSON for
  the full filing history, fills the buffer, and blocks waiting for Python to
  read -- but Python is inside communicate() waiting for curl to exit first.
  DEADLOCK. Fix: write curl output directly to a temp file, not through a pipe.

All output uses plain ASCII only (no emoji) to avoid Windows cp1252 encoding errors.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
COMPANY_NUMBER = "06993349"
API_KEY        = "ac0ca454-9fea-4bf6-ae9e-c0446e1b3f55"
BASE_URL       = "https://api.company-information.service.gov.uk"
DOC_URL        = "https://document-api.company-information.service.gov.uk"

ACCOUNTS_DIR   = Path(r"C:\DAD\UK_Lanzarote_Repatriation\Annual accounts")

SUBFOLDERS = {
    "01_Financial_Statements":     ACCOUNTS_DIR / "01_Financial_Statements",
    "02_Company_Formation":        ACCOUNTS_DIR / "02_Company_Formation",
    "03_Confirmation_Statements":  ACCOUNTS_DIR / "03_Confirmation_Statements",
    "04_Share_Capital":            ACCOUNTS_DIR / "04_Share_Capital",
    "05_PSC_Register":             ACCOUNTS_DIR / "05_PSC_Register",
    "06_Officers_and_Secretaries": ACCOUNTS_DIR / "06_Officers_and_Secretaries",
    "07_CH_Downloads_Unsorted":    ACCOUNTS_DIR / "07_CH_Downloads_Unsorted",
    "08_Resolutions_and_Charges":  ACCOUNTS_DIR / "08_Resolutions_and_Charges",
}

# ── HELPERS: CURL VIA TEMP FILE (NO PIPE BUFFER DEADLOCK) ────────────────────

def curl_get_json(url, retries=3):
    """
    Fetch JSON from CH API using curl.exe.
    Writes response body to a temp FILE (not a pipe) to avoid the Windows
    64KB pipe-buffer deadlock that causes capture_output=True to hang.
    """
    for attempt in range(1, retries + 1):
        tf = Path(tempfile.mktemp(suffix=".json"))
        cmd = [
            "curl.exe",
            "-u", "{}:".format(API_KEY),
            "-H", "Accept: application/json",
            "--connect-timeout", "30",
            "--max-time",        "90",
            "-s",
            "-o", str(tf),       # <-- body goes to FILE, not to the pipe
            url,
        ]
        try:
            # stdout/stderr discarded -- only small exit-code matters
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=100
            )
            if tf.exists() and tf.stat().st_size > 0:
                raw = tf.read_text(encoding="utf-8", errors="replace")
                tf.unlink(missing_ok=True)
                try:
                    return json.loads(raw)
                except json.JSONDecodeError as e:
                    print("    [!!] Bad JSON (attempt {}/{}): {}".format(attempt, retries, e))
                    print("    [!!] First 200 chars: {}".format(raw[:200]))
            else:
                code = result.returncode
                print("    [!!] Empty/missing output (attempt {}/{}) curl exit={}".format(
                    attempt, retries, code))
        except subprocess.TimeoutExpired:
            print("    [!!] Subprocess timeout (attempt {}/{})".format(attempt, retries))
        finally:
            tf.unlink(missing_ok=True)

        wait = 15 * attempt
        print("    [..] Backing off {}s before retry...".format(wait))
        time.sleep(wait)

    return None


def curl_download_pdf(url, dest_path):
    """
    Download a PDF from CH Document API using curl.exe.
    Writes body directly to dest_path (already a file, no pipe issue).
    Captures only the tiny -w status string through the pipe (safe).
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "curl.exe",
        "-u", "{}:".format(API_KEY),
        "-H", "Accept: application/pdf",
        "-L",
        "--connect-timeout", "30",
        "--max-time",        "120",
        "-s",
        "-o", str(dest_path),
        "-w", "%{http_code}|%{size_download}",   # tiny string through pipe -- safe
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=130)
        parts = result.stdout.strip().split("|")
        http_code = parts[0] if parts else "000"
        size_bytes = int(parts[1]) if len(parts) > 1 else 0

        if http_code == "200" and size_bytes > 500:
            return True

        print("    [!!] HTTP {} | {} bytes".format(http_code, size_bytes))
        if dest_path.exists():
            dest_path.unlink()
        return False

    except subprocess.TimeoutExpired:
        print("    [!!] PDF download timed out")
        if dest_path.exists():
            dest_path.unlink()
        return False


# ── CLASSIFICATION ────────────────────────────────────────────────────────────

def classify_filing(category, description, filing_type):
    c = (category or "").lower()
    d = (description or "").lower()
    t = (filing_type or "").lower()

    if c == "accounts" or "account" in d:
        return "01_Financial_Statements"
    if c == "incorporation" or t in ("model-articles", "memorandum-articles", "in01"):
        return "02_Company_Formation"
    if c in ("annual-return", "confirmation-statement") or "confirmation" in d or "annual return" in d:
        return "03_Confirmation_Statements"
    if c == "capital" or any(x in d for x in ["share capital", "sh01", "sh02", "shares allotted"]):
        return "04_Share_Capital"
    if c == "persons-with-significant-control" or "significant control" in d:
        return "05_PSC_Register"
    if c == "officers" or any(x in d for x in ["director", "secretary", "officer"]):
        return "06_Officers_and_Secretaries"
    if any(x in d for x in ["resolution", "articles of association", "charge", "gazette"]):
        return "08_Resolutions_and_Charges"
    return "07_CH_Downloads_Unsorted"


def sanitise(text):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', str(text)).strip()


def file_already_exists_for_date_and_type(date, filing_type):
    """Quick check: do we already have a file matching this date + type combo?"""
    pattern = "{}_{}".format(date, (filing_type or "").upper())
    for pdf in ACCOUNTS_DIR.rglob("*.pdf"):
        if pdf.name.startswith(date) and (filing_type or "").upper() in pdf.name.upper():
            return True
    return False


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Los Romeros Limited -- Companies House PDF Downloader")
    print("Key: {}... | Company: {}".format(API_KEY[:8], COMPANY_NUMBER))
    print("=" * 70)
    sys.stdout.flush()

    # 1. Subfolders
    print("\n[1/3] Ensuring subfolder structure...")
    for name, path in SUBFOLDERS.items():
        path.mkdir(parents=True, exist_ok=True)
    print("  [OK] {} subfolders ready".format(len(SUBFOLDERS)))
    sys.stdout.flush()

    # 2. Filing history (paginated)
    print("\n[2/3] Fetching filing history from Companies House...")
    sys.stdout.flush()

    all_filings = []
    start       = 0
    total       = None

    while True:
        url = ("{}/company/{}/filing-history"
               "?items_per_page=100&start_index={}").format(
            BASE_URL, COMPANY_NUMBER, start)
        print("  GET {}".format(url[-75:]))
        sys.stdout.flush()

        data = curl_get_json(url)
        if not data:
            print("  [XX] Failed to fetch filing history after all retries.")
            sys.exit(1)

        items = data.get("items", [])
        if total is None:
            total = data.get("total_count", len(items))

        all_filings.extend(items)
        print("  Fetched {}/{} filings".format(len(all_filings), total))
        sys.stdout.flush()

        if len(all_filings) >= total or not items:
            break
        start += 100
        time.sleep(1)

    print("  [OK] {} filings total".format(len(all_filings)))
    sys.stdout.flush()

    # 3. Download
    print("\n[3/3] Downloading missing filings...")
    sys.stdout.flush()

    downloaded = skipped = no_pdf = failed = 0

    for i, filing in enumerate(all_filings, 1):
        date        = filing.get("date", "unknown")
        description = filing.get("description", "")
        category    = filing.get("category", "other")
        ftype       = filing.get("type", "")
        links       = filing.get("links", {})
        doc_meta    = links.get("document_metadata")

        label = "{}  {:8s}  {}".format(date, ftype, description[:50])
        print("\n  [{:02d}/{}] {}".format(i, len(all_filings), label))
        sys.stdout.flush()

        if not doc_meta:
            print("    [--] No document link -- skipping")
            no_pdf += 1
            continue

        if file_already_exists_for_date_and_type(date, ftype):
            print("    [OK] Already downloaded -- skipping")
            skipped += 1
            continue

        # Resolve doc metadata to get actual download URL
        meta_url = doc_meta if doc_meta.startswith("http") else "{}{}".format(DOC_URL, doc_meta)
        meta     = curl_get_json(meta_url)

        if not meta:
            print("    [!!] Could not fetch metadata")
            failed += 1
            continue

        doc_href = (meta.get("links") or {}).get("document", "")
        if not doc_href:
            print("    [!!] No document href in metadata")
            failed += 1
            continue

        if doc_href.startswith("/"):
            full_url = "{}{}".format(DOC_URL, doc_href)
        else:
            full_url = doc_href

        # Build destination path
        subfolder  = classify_filing(category, description, ftype)
        t_safe     = sanitise(ftype).upper()[:12]
        d_safe     = sanitise(description[:55]).replace(" ", "_")
        filename   = "{}_{}_{}".format(date, t_safe, d_safe) + ".pdf"
        dest_path  = SUBFOLDERS[subfolder] / filename

        print("    [DL] -> {}/{}".format(subfolder, filename[:60]))
        sys.stdout.flush()

        ok = curl_download_pdf(full_url, dest_path)
        if ok:
            size_kb = dest_path.stat().st_size // 1024
            print("    [OK] Saved {} KB".format(size_kb))
            downloaded += 1
        else:
            failed += 1

        sys.stdout.flush()
        time.sleep(0.6)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("  Downloaded : {}".format(downloaded))
    print("  Skipped    : {}".format(skipped))
    print("  No PDF     : {}".format(no_pdf))
    print("  Failed     : {}".format(failed))

    print("\nFOLDER CONTENTS:")
    for name, path in SUBFOLDERS.items():
        pdfs = sorted(path.glob("*.pdf"))
        if pdfs:
            print("\n  [{}]  ({} PDFs)".format(path.name, len(pdfs)))
            for p in pdfs:
                print("    {}".format(p.name[:80]))

    print("\nDone.")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
