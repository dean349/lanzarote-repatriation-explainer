"""
fetch_and_organise_ch.py
========================
1. Downloads every available PDF filing from Companies House for
   Los Romeros Limited (Company No. 06993349) that is not already
   on disk.
2. Organises ALL files in Annual accounts\ into clean subfolders.
3. Updates dump_sec.py to point at the new Officers subfolder.

Companies House API key: ac0ca454-9fea-4bf6-ae9e-c0446e1b3f55
"""

import os
import re
import shutil
import time
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────
COMPANY_NUMBER = "06993349"
API_KEY        = "ac0ca454-9fea-4bf6-ae9e-c0446e1b3f55"
BASE_URL       = "https://api.company-information.service.gov.uk"
DOC_URL        = "https://document-api.company-information.service.gov.uk"
AUTH           = HTTPBasicAuth(API_KEY, "")

ACCOUNTS_DIR   = Path(r"C:\DAD\UK_Lanzarote_Repatriation\Annual accounts")

SUBFOLDERS = {
    "01_Financial_Statements":      ACCOUNTS_DIR / "01_Financial_Statements",
    "02_Company_Formation":         ACCOUNTS_DIR / "02_Company_Formation",
    "03_Confirmation_Statements":   ACCOUNTS_DIR / "03_Confirmation_Statements",
    "04_Share_Capital":             ACCOUNTS_DIR / "04_Share_Capital",
    "05_PSC_Register":              ACCOUNTS_DIR / "05_PSC_Register",
    "06_Officers_and_Secretaries":  ACCOUNTS_DIR / "06_Officers_and_Secretaries",
    "07_Company_Overview":          ACCOUNTS_DIR / "07_Company_Overview",
    "08_CH_Downloads_Unsorted":     ACCOUNTS_DIR / "08_CH_Downloads_Unsorted",
}

# ── CLASSIFICATION RULES ─────────────────────────────────────────────────────
def classify_file(filename: str) -> str:
    f = filename.lower()
    if any(x in f for x in ["certificate of incorporation", "certificate_of_incorporation"]):
        return "02_Company_Formation"
    if any(x in f for x in ["confirmation statement", "cs01", "annual return"]):
        return "03_Confirmation_Statements"
    if any(x in f for x in ["sh02", "sh01", "shares", "share capital", "consolidation of shares",
                              "reconversion of stock"]):
        return "04_Share_Capital"
    if any(x in f for x in ["psc", "psc_ownership", "significant control", "person with significant"]):
        return "05_PSC_Register"
    if any(x in f for x in ["secretary", "director", "ap01", "tm01", "ch01", "ch04",
                              "officer", "adrem accounting", "appointment", "termination"]):
        return "06_Officers_and_Secretaries"
    if "company overview" in f:
        return "07_Company_Overview"
    if re.match(r"companies_house_document", f):
        return "08_CH_Downloads_Unsorted"
    if any(x in f for x in ["accounts", "financial statement", "unaudited"]):
        return "01_Financial_Statements"
    return "08_CH_Downloads_Unsorted"


def classify_filing_category(category: str, description: str) -> str:
    c, d = category.lower(), description.lower()
    if c == "accounts" or "accounts" in d:
        return "01_Financial_Statements"
    if c in ("incorporation",):
        return "02_Company_Formation"
    if c in ("annual-return", "confirmation-statement") or "confirmation" in d or "annual return" in d:
        return "03_Confirmation_Statements"
    if c == "capital" or "capital" in d or "shares" in d or "sh0" in d:
        return "04_Share_Capital"
    if c == "persons-with-significant-control" or "significant control" in d:
        return "05_PSC_Register"
    if c == "officers" or any(x in d for x in ["director", "secretary", "officer"]):
        return "06_Officers_and_Secretaries"
    return "08_CH_Downloads_Unsorted"


# ── HELPERS ───────────────────────────────────────────────────────────────────
def sanitise(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


def already_downloaded(stem: str, folder: Path) -> bool:
    """True if a file whose name contains the stem exists anywhere in ACCOUNTS_DIR."""
    for f in ACCOUNTS_DIR.rglob("*.pdf"):
        if stem[:30].lower() in f.name.lower():
            return True
    return False


def get_filing_history() -> list:
    """Fetch all filings with pagination."""
    filings = []
    start = 0
    batch = 100
    while True:
        r = requests.get(
            f"{BASE_URL}/company/{COMPANY_NUMBER}/filing-history",
            auth=AUTH,
            params={"items_per_page": batch, "start_index": start},
            timeout=30
        )
        if r.status_code != 200:
            print(f"  ⚠️  Filing history error {r.status_code}: {r.text[:200]}")
            break
        data = r.json()
        items = data.get("items", [])
        filings.extend(items)
        total = data.get("total_count", 0)
        start += batch
        print(f"  Fetched {len(filings)}/{total} filings...")
        if len(filings) >= total:
            break
        time.sleep(0.3)
    return filings


def get_document_url(doc_metadata_url: str) -> str | None:
    """Resolve document metadata URL to an actual download URL."""
    r = requests.get(doc_metadata_url, auth=AUTH, timeout=20)
    if r.status_code != 200:
        return None
    data = r.json()
    # Links object has the document content URL
    resources = data.get("resources", {})
    for mime, info in resources.items():
        if "pdf" in mime.lower():
            return data.get("links", {}).get("document", None)
    # Fallback — try direct links
    return data.get("links", {}).get("document", None)


def download_pdf(doc_url: str, dest_path: Path) -> bool:
    """Download a PDF from the Companies House Document API."""
    headers = {"Accept": "application/pdf"}
    r = requests.get(doc_url, auth=AUTH, headers=headers, timeout=60, stream=True)
    if r.status_code == 200 and "pdf" in r.headers.get("Content-Type", ""):
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    print(f"    ⚠️  Download failed: HTTP {r.status_code} | Content-Type: {r.headers.get('Content-Type','?')}")
    return False


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("Los Romeros Limited — Companies House PDF Downloader & Organiser")
    print(f"Company: {COMPANY_NUMBER} | Target: {ACCOUNTS_DIR}")
    print("=" * 70)

    # 1. Create subfolders
    print("\n[1/4] Creating subfolder structure...")
    for name, path in SUBFOLDERS.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅  {path.name}/")

    # 2. Organise existing files
    print("\n[2/4] Organising existing files into subfolders...")
    moved = []
    skipped_scripts = []
    for f in sorted(ACCOUNTS_DIR.iterdir()):
        if f.is_dir():
            continue
        if f.suffix.lower() == ".py":
            skipped_scripts.append(f.name)
            print(f"  📌 Keeping script at root: {f.name}")
            continue
        if f.suffix.lower() != ".pdf":
            print(f"  ⏭️  Skipping non-PDF: {f.name}")
            continue
        target_subfolder = classify_file(f.name)
        dest = SUBFOLDERS[target_subfolder] / f.name
        if dest.exists():
            print(f"  ⏭️  Already in place: {f.name}")
            continue
        shutil.move(str(f), str(dest))
        moved.append((f.name, target_subfolder))
        print(f"  📁 {f.name}\n     → {target_subfolder}/")

    print(f"\n  Moved {len(moved)} files into subfolders.")

    # 3. Download missing filings from Companies House
    print("\n[3/4] Fetching Companies House filing history...")
    filings = get_filing_history()
    print(f"  Total filings found: {len(filings)}")

    downloaded = 0
    skipped = 0
    failed = 0

    for filing in filings:
        date        = filing.get("date", "unknown")
        description = filing.get("description", "unknown")
        category    = filing.get("category", "other")
        links       = filing.get("links", {})
        doc_meta    = links.get("document_metadata")

        if not doc_meta:
            skipped += 1
            continue

        # Build a clean filename from date + description
        clean_desc  = sanitise(description[:80])
        filename    = f"{date}_{clean_desc}.pdf"
        subfolder   = classify_filing_category(category, description)
        dest_path   = SUBFOLDERS[subfolder] / filename

        # Skip if already exists (exact or near-match)
        if dest_path.exists():
            skipped += 1
            continue

        # Check if similar file already present in that subfolder
        year_match = re.search(r"\d{4}", date)
        if year_match:
            year = year_match.group()
            existing = list(SUBFOLDERS[subfolder].glob(f"*{year}*.pdf"))
            # Rough heuristic: skip accounts if year folder already has an accounts file
            if existing and category == "accounts":
                skipped += 1
                continue

        print(f"  ⬇️  {date} | {category:30s} | {description[:50]}...")
        doc_url = get_document_url(doc_meta)
        if not doc_url:
            print(f"    ⚠️  Could not resolve document URL")
            failed += 1
            continue

        success = download_pdf(doc_url, dest_path)
        if success:
            size_kb = dest_path.stat().st_size // 1024
            print(f"    ✅ Saved: {filename} ({size_kb} KB)")
            downloaded += 1
        else:
            failed += 1
        time.sleep(0.4)  # Be polite to the API

    print(f"\n  Downloaded: {downloaded} | Skipped (already present): {skipped} | Failed: {failed}")

    # 4. Update dump_sec.py to use new subfolder path
    print("\n[4/4] Updating dump_sec.py paths...")
    dump_sec = ACCOUNTS_DIR / "dump_sec.py"
    if dump_sec.exists():
        content = dump_sec.read_text()
        old = r'C:\DAD\UK_Lanzarote_Repatriation\Annual accounts\Secretary*'
        new = r'C:\DAD\UK_Lanzarote_Repatriation\Annual accounts\06_Officers_and_Secretaries\Secretary*'
        updated = content.replace(old, new)
        if updated != content:
            dump_sec.write_text(updated)
            print(f"  ✅  dump_sec.py updated: Secretary* path → 06_Officers_and_Secretaries/")
        else:
            print(f"  ℹ️  dump_sec.py already up to date (or pattern not found — check manually)")

    # 5. Print final structure
    print("\n" + "=" * 70)
    print("FINAL FOLDER STRUCTURE")
    print("=" * 70)
    for name, path in SUBFOLDERS.items():
        pdfs = list(path.glob("*.pdf"))
        print(f"\n  📂 {path.name}/ ({len(pdfs)} PDFs)")
        for p in sorted(pdfs):
            size_kb = p.stat().st_size // 1024
            print(f"      {p.name:<70s} {size_kb:>4} KB")

    print("\n✅ All done.")


if __name__ == "__main__":
    main()
