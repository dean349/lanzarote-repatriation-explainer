"""
download_ch_public.py
=====================
Downloads all Los Romeros Limited filings using PUBLIC Companies House
website URLs. No API key needed. No document-api dependency.
All 70 transaction IDs are hardcoded from browser extraction.

URL format:
  https://find-and-update.company-information.service.gov.uk
  /company/06993349/filing-history/{txId}/document?format=pdf&download=1
"""

import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ── ARCHIVE ROOT ──────────────────────────────────────────────────────────────
ACCOUNTS_DIR = Path(r"C:\DAD\UK_Lanzarote_Repatriation\Annual accounts")

SUBFOLDERS = {
    "01_Financial_Statements":     ACCOUNTS_DIR / "01_Financial_Statements",
    "02_Company_Formation":        ACCOUNTS_DIR / "02_Company_Formation",
    "03_Confirmation_Statements":  ACCOUNTS_DIR / "03_Confirmation_Statements",
    "04_Share_Capital":            ACCOUNTS_DIR / "04_Share_Capital",
    "05_PSC_Register":             ACCOUNTS_DIR / "05_PSC_Register",
    "06_Officers_and_Secretaries": ACCOUNTS_DIR / "06_Officers_and_Secretaries",
    "07_Registered_Office":        ACCOUNTS_DIR / "07_Registered_Office",
    "08_CH_Downloads_Unsorted":    ACCOUNTS_DIR / "08_CH_Downloads_Unsorted",
}

CH_BASE = "https://find-and-update.company-information.service.gov.uk"
COMPANY = "06993349"

# ── ALL 70 FILINGS (hardcoded from browser extraction 2 Apr 2026) ─────────────
# (date_iso, filing_type, description, txId)
FILINGS = [
    ("2026-02-10", "TM01", "Termination of appointment of Beryl Harrison as a director",          "MzUwNDA3OTM3M2FkaXF6a2N4"),
    ("2025-12-19", "AA",   "Total exemption full accounts made up to 31 August 2025",             "MzQ5NTM0Mzg5OWFkaXF6a2N4"),
    ("2025-10-27", "CH04", "Secretary's details changed for Adrem Accounting Ltd",                "MzQ4NjQwNzMxN2FkaXF6a2N4"),
    ("2025-09-25", "AD01", "Registered office address changed from Wincham House to 4 Market St", "MzQ4MjY3ODc3MGFkaXF6a2N4"),
    ("2025-08-27", "CS01", "Confirmation statement made on 18 August 2025 with no updates",       "MzQ3ODgwMjk5M2FkaXF6a2N4"),
    ("2024-12-19", "AA",   "Total exemption full accounts made up to 31 August 2024",             "MzQ0ODM0NTM2NWFkaXF6a2N4"),
    ("2024-08-20", "CS01", "Confirmation statement made on 18 August 2024 with no updates",       "MzQzMjczMjgxNWFkaXF6a2N4"),
    ("2024-06-25", "CH04", "Secretary's details changed for Wincham Accountancy Limited",         "MzQyNjUxNDQwNWFkaXF6a2N4"),
    ("2024-03-14", "AA",   "Total exemption full accounts made up to 31 August 2023",             "MzQxNDU0MzYzMmFkaXF6a2N4"),
    ("2023-08-21", "CS01", "Confirmation statement made on 18 August 2023 with no updates",       "MzM5MDE4ODE2M2FkaXF6a2N4"),
    ("2023-05-26", "AA",   "Total exemption full accounts made up to 31 August 2022",             "MzM4MDk3MzAzOGFkaXF6a2N4"),
    ("2022-08-19", "CS01", "Confirmation statement made on 18 August 2022 with no updates",       "MzM0OTE1NTIwNGFkaXF6a2N4"),
    ("2022-05-20", "AA",   "Total exemption full accounts made up to 31 August 2021",             "MzMzOTk4ODA0OGFkaXF6a2N4"),
    ("2021-08-18", "CS01", "Confirmation statement made on 18 August 2021 with updates",          "MzMxMDk5NTgzMmFkaXF6a2N4"),
    ("2021-08-18", "AP04", "Appointment of Wincham Accountancy Limited as a secretary",           "MzMxMDk5NTMzNGFkaXF6a2N4"),
    ("2021-08-18", "TM02", "Termination of appointment of Wincham Accountants Limited as secretary","MzMxMDk5NTI0OWFkaXF6a2N4"),
    ("2021-08-18", "CH04", "Secretary's details changed for Adrem Accounting Ltd",                "MzMxMDk5NDk2NmFkaXF6a2N4"),
    ("2021-08-18", "CH01", "Director's details changed for Mrs Mary Ann Stockwell",               "MzMxMDk5NDkwNWFkaXF6a2N4"),
    ("2021-08-18", "CH01", "Director's details changed for Mr Bryan Frederick Stockwell",         "MzMxMDk5NDgxMWFkaXF6a2N4"),
    ("2021-07-05", "AA",   "Total exemption full accounts made up to 31 August 2020",             "MzMwNzIxMzc4NGFkaXF6a2N4"),
    ("2020-09-02", "CS01", "Confirmation statement made on 18 August 2020 with updates",          "MzI3Njc1Mzk0M2FkaXF6a2N4"),
    ("2020-09-02", "AD01", "Registered office address changed from 4 Market Street to Wincham House","MzI3Njc1MzkzMmFkaXF6a2N4"),
    ("2020-09-02", "CH01", "Director's details changed for Mrs Mary Ann Stockwell",               "MzI3Njc1MzkxM1FkaXF6a2N4"),
    ("2020-09-02", "CH01", "Director's details changed for Mr Bryan Frederick Stockwell",         "MzI3Njc1MzkwMGFkaXF6a2N4"),
    ("2020-04-17", "AA",   "Total exemption full accounts made up to 31 August 2019",             "MzI2MzEyMTgzNmFkaXF6a2N4"),
    ("2020-01-06", "SH02", "Statement of capital on 23 December 2019 GBP 159636",                 "MzI1MzY2ODg3NGFkaXF6a2N4"),
    ("2019-12-30", "TM01", "Termination of appointment of Kevin John Stockwell as a director",    "MzI1MzMxOTY0MWFkaXF6a2N4"),
    ("2019-12-27", "TM01", "Termination of appointment of Mrs Mary Ann Stockwell as a director",  "MzI1MzMxOTUxOWFkaXF6a2N4"),
    ("2019-12-27", "SH01", "Statement of capital following allotment of shares 23 December 2019", "MzI1MzIyNDAzOGFkaXF6a2N4"),
    ("2019-12-23", "AP04", "Appointment of Adrem Accounting Limited as a secretary",              "MzI1MzE1Mjk3MmFkaXF6a2N4"),
    ("2019-12-23", "AP01", "Appointment of Mr Bryan Frederick Stockwell as a director",           "MzI1MzE1Mjc5OWFkaXF6a2N4"),
    ("2019-12-04", "AA",   "Total exemption full accounts made up to 31 August 2019 (original)",  "MzI1MTE3MDkxMWFkaXF6a2N4"),
    ("2019-10-08", "AP01", "Appointment of Mr Mark Damion Roach as a director",                   "MzI0NjI2NTYwMmFkaXF6a2N4"),
    ("2019-10-07", "AP01", "Appointment of Mr Kevin John Stockwell as a director",                "MzI0NjE5MjI5MmFkaXF6a2N4"),
    ("2019-10-07", "TM01", "Termination of appointment of Mark Damion Roach as a director",       "MzI0NjE5MTkyM2FkaXF6a2N4"),
    ("2019-08-21", "CS01", "Confirmation statement made on 18 August 2019 with no updates",       "MzI0MjI0MDY4NmFkaXF6a2N4"),
    ("2019-04-15", "AA",   "Total exemption full accounts made up to 31 August 2018",             "MzIzMjA3ODU1OGFkaXF6a2N4"),
    ("2019-01-25", "AP01", "Appointment of Mr Mark Damion Roach as a director",                   "MzIyNTQxMjQ1NGFkaXF6a2N4"),
    ("2019-01-25", "TM01", "Termination of appointment of Bryan Frederick Stockwell as a director","MzIyNTQxMjM4NmFkaXF6a2N4"),
    ("2019-01-25", "PSC04","Change of details for Mrs Mary Ann Stockwell on 23 January 2019",     "MzIyNTQxMjI5M2FkaXF6a2N4"),
    ("2019-01-25", "PSC07","Cessation of Bryan Frederick Stockwell as a person with significant control","MzIyNTQxMjI4MmFkaXF6a2N4"),
    ("2018-08-24", "CS01", "Confirmation statement made on 18 August 2018 with no updates",       "MzIxMjg3NTE4OGFkaXF6a2N4"),
    ("2018-04-17", "AA",   "Total exemption full accounts made up to 31 August 2017",             "MzIwMjc2OTI4MGFkaXF6a2N4"),
    ("2017-08-18", "CS01", "Confirmation statement made on 18 August 2017 with no updates",       "MzE4MzUwNDY1MWFkaXF6a2N4"),
    ("2017-08-18", "CH01", "Director's details changed for Mrs Mary Ann Stockwell",               "MzE4MzUwNDUwNmFkaXF6a2N4"),
    ("2017-08-11", "AD01", "Registered office address changed from Wincham House to 4 Market Street","MzE4MzAwMDkyOWFkaXF6a2N4"),
    ("2017-04-19", "AA",   "Total exemption full accounts made up to 31 August 2016",             "MzE3Mzg4NzMxNGFkaXF6a2N4"),
    ("2017-01-18", "PSC01","Notification of Mrs Mary Ann Stockwell as a person with significant control","MzE2Njc5MTU4MmFkaXF6a2N4"),
    ("2017-01-18", "PSC01","Notification of Mr Bryan Frederick Stockwell as a person with significant control","MzE2Njc5MTU3OWFkaXF6a2N4"),
    ("2016-08-30", "CS01", "Confirmation statement made on 18 August 2016 with no updates",       "MzE1NTczNzI4OWFkaXF6a2N4"),
    ("2016-05-24", "AA",   "Total exemption full accounts made up to 31 August 2015",             "MzE0OTYwMjIxM2FkaXF6a2N4"),
    ("2015-08-24", "AR01", "Annual return made up to 18 August 2015 with full list of shareholders","MzEzMDM5OTY3N2FkaXF6a2N4"),
    ("2015-05-20", "AA",   "Total exemption full accounts made up to 31 August 2014",             "MzEyMzUyOTc3MmFkaXF6a2N4"),
    ("2014-04-28", "AA",   "Total exemption small company accounts made up to 31 August 2013",    "MzA5ODk2NTEyNWFkaXF6a2N4"),
    ("2013-08-19", "AR01", "Annual return made up to 18 August 2013 with full list of shareholders","MzA4Mjc2ODgwNWFkaXF6a2N4"),
    ("2013-04-24", "AA",   "Total exemption small company accounts made up to 31 August 2012",    "MzA3NTQzMjA3N2FkaXF6a2N4"),
    ("2012-09-01", "AR01", "Annual return made up to 18 August 2012 with full list of shareholders","MzA2Mjc0NzExMWFkaXF6a2N4"),
    ("2012-08-31", "TM02", "Termination of appointment of Companies 4 U Secretaries as a secretary","MzA2MjcwNTU0OWFkaXF6a2N4"),
    ("2012-08-31", "AP04", "Appointment of Wincham Legal Limited as a secretary",                 "MzA2MjcwNTQ5OWFkaXF6a2N4"),
    ("2012-05-28", "AA",   "Total exemption small company accounts made up to 31 August 2011",    "MzA1NjQwMjIwNmFkaXF6a2N4"),
    ("2011-08-18", "AR01", "Annual return made up to 18 August 2011 with full list of shareholders","MzA0MTQyNTAyNmFkaXF6a2N4"),
    ("2011-07-21", "AA",   "Total exemption small company accounts made up to 31 August 2010",    "MzAzOTg3Mzk0M2FkaXF6a2N4"),
    ("2011-06-10", "TM01", "Termination of appointment of Frederick Purvs as a director",         "MzAzODA5MzAzOGFkaXF6a2N4"),
    ("2011-06-10", "TM01", "Termination of appointment of Margaret Purvis as a director",         "MzAzODA5Mjk4OWFkaXF6a2N4"),
    ("2011-06-10", "AP01", "Appointment of Mr Bryan Frederick Stockwell as a director",           "MzAzODA5MjkyMGFkaXF6a2N4"),
    ("2011-05-17", "AD01", "Registered office address changed from 4 Market Street to Wincham House","MzAzNjAzMDI0NWFkaXF6a2N4"),
    ("2010-08-23", "CH04", "Secretary's details changed for Companies 4 U Secretaries Ltd",       "MzAxOTUxNDkyMWFkaXF6a2N4"),
    ("2010-08-23", "AR01", "Annual return made up to 18 August 2010 with full list of shareholders","MzAxOTUxNDgxMWFkaXF6a2N4"),
    ("2010-07-28", "SH01", "Statement of capital following allotment of shares on 23 July 2010",  "MzAxNzk0NTk0MWFkaXF6a2N4"),
    ("2010-07-27", "TM01", "Termination of appointment of Malcolm Roach as a director",           "MzAxNzg5OTI0NGFkaXF6a2N4"),
    ("2010-07-27", "AP01", "Appointment of Margaret Ellen Purvis as a director",                  "MzAxNzg5OTIyOWFkaXF6a2N4"),
    ("2010-07-27", "AP01", "Appointment of Frederick Purvs as a director",                        "MzAxNzg5OTE0MWFkaXF6a2N4"),
    ("2009-08-18", "NEWINC","Incorporation of Los Romeros Limited",                               "MzAwMDQxNTAzMWFkaXF6a2N4"),
]

# ── CLASSIFICATION ────────────────────────────────────────────────────────────
def classify(ftype):
    t = ftype.upper()
    if t == "AA":                              return "01_Financial_Statements"
    if t in ("NEWINC",):                       return "02_Company_Formation"
    if t in ("CS01", "AR01"):                  return "03_Confirmation_Statements"
    if t in ("SH01", "SH02"):                  return "04_Share_Capital"
    if t in ("PSC01","PSC04","PSC07","PSC09"): return "05_PSC_Register"
    if t in ("AP01","AP04","TM01","TM02","CH01","CH04","CH02","CH03"): return "06_Officers_and_Secretaries"
    if t == "AD01":                            return "07_Registered_Office"
    return "08_CH_Downloads_Unsorted"


def sanitise(text):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', str(text)).strip()


def already_have(date, ftype):
    """Check if we already have a PDF for this exact date+type."""
    prefix = "{}_{}".format(date, ftype.upper())
    for pdf in ACCOUNTS_DIR.rglob("*.pdf"):
        if pdf.name.upper().startswith(prefix.upper()):
            return True
    return False


def curl_download(url, dest_path):
    """
    Download URL to dest_path using curl.exe (no auth, public URL).
    Returns True on success.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "curl.exe",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-H", "Accept: application/pdf,*/*",
        "-L",
        "--connect-timeout", "30",
        "--max-time",        "120",
        "-s",
        "-o", str(dest_path),
        "-w", "%{http_code}|%{size_download}|%{content_type}",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=130)
        parts  = result.stdout.strip().split("|")
        http   = parts[0] if parts else "000"
        size   = int(parts[1]) if len(parts) > 1 else 0
        ctype  = parts[2] if len(parts) > 2 else ""

        if http == "200" and size > 500:
            return True, http, size, ctype

        # Cleanup bad files
        if dest_path.exists():
            dest_path.unlink()
        return False, http, size, ctype

    except subprocess.TimeoutExpired:
        if dest_path.exists():
            dest_path.unlink()
        return False, "TIMEOUT", 0, ""


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 72)
    print("Los Romeros Limited -- CH Archive Download (Public URLs, No API Key)")
    print("Company: {} | Filings: {}".format(COMPANY, len(FILINGS)))
    print("=" * 72)
    sys.stdout.flush()

    # Ensure subfolders
    for path in SUBFOLDERS.values():
        path.mkdir(parents=True, exist_ok=True)
    print("[OK] Subfolders ready\n")
    sys.stdout.flush()

    # Quick connectivity test
    test_url = "{}/company/{}/filing-history".format(CH_BASE, COMPANY)
    tf = Path(tempfile.mktemp(suffix=".html"))
    test_cmd = ["curl.exe", "-L", "--connect-timeout", "20", "--max-time", "30",
                "-s", "-o", str(tf), "-w", "%{http_code}", test_url]
    try:
        r = subprocess.run(test_cmd, capture_output=True, text=True, timeout=35)
        code = r.stdout.strip()
        tf.unlink(missing_ok=True)
        if code == "200":
            print("[OK] Public CH website reachable (HTTP 200)\n")
        else:
            print("[!!] Public CH website returned HTTP {} -- will try anyway\n".format(code))
    except Exception as e:
        tf.unlink(missing_ok=True)
        print("[!!] Connectivity test failed: {} -- will try anyway\n".format(e))
    sys.stdout.flush()

    downloaded = skipped = failed = 0

    for i, (date, ftype, desc, txid) in enumerate(FILINGS, 1):
        label = "{}  {:6s}  {}".format(date, ftype, desc[:50])
        print("[{:02d}/{:02d}] {}".format(i, len(FILINGS), label))
        sys.stdout.flush()

        if already_have(date, ftype):
            print("  [SKIP] Already in archive")
            skipped += 1
            sys.stdout.flush()
            continue

        subfolder = classify(ftype)
        d_safe    = sanitise(desc[:55]).replace(" ", "_")
        filename  = "{}_{}_{}".format(date, ftype.upper(), d_safe) + ".pdf"
        dest      = SUBFOLDERS[subfolder] / filename

        url = "{}/company/{}/filing-history/{}/document?format=pdf&download=1".format(
            CH_BASE, COMPANY, txid)

        ok, http, size, ctype = curl_download(url, dest)

        if ok:
            print("  [OK]  Saved to {}/  ({} KB)".format(subfolder, size // 1024))
            downloaded += 1
        else:
            print("  [FAIL] HTTP={} size={} ctype={}".format(http, size, ctype[:40]))
            failed += 1

        sys.stdout.flush()
        time.sleep(0.8)

    print("\n" + "=" * 72)
    print("COMPLETE: Downloaded={} Skipped={} Failed={}".format(
        downloaded, skipped, failed))

    print("\nFOLDER SUMMARY:")
    for name, path in SUBFOLDERS.items():
        pdfs = sorted(path.glob("*.pdf"))
        if pdfs:
            print("\n  [{}]  ({} PDFs)".format(path.name, len(pdfs)))
            for p in pdfs:
                print("    {}".format(p.name[:80]))


if __name__ == "__main__":
    main()
