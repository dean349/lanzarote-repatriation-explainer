"""
Full-Scheme SIC Code Audit — Wincham (CW12 4TR) + Adrem (CW12 4AA)
====================================================================
Uses urllib (no requests library) to avoid SSL hanging issues.
Clears any stale cache at startup automatically.

Correct SIC for Spanish property holding vehicle: 68100 / 68209
Wrong code applied by Wincham/Adrem batch:        70229
"""

import csv, json, os, time, ssl, base64, urllib.request, urllib.error

# ── Config ────────────────────────────────────────────────────────────────────
BASE       = r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action"
API_KEY    = "37e01bb5-04e8-4d0d-9895-9037e31e2e36"
BASE_URL   = "https://api.company-information.service.gov.uk"
RATE_PAUSE = 0.6    # ~100 req/min — well inside 600/5-min free-tier

WINCHAM_CSV  = os.path.join(BASE, "wincham_only_companies.csv")
EXISTING_SIC = os.path.join(BASE, "hmrc_sic_misclassification.csv")
CACHE_FILE   = os.path.join(BASE, "wincham_sic_cache.json")
OUT_CSV      = os.path.join(BASE, "FULL_SCHEME_sic_misclassification.csv")
REPORT_TXT   = os.path.join(BASE, "FULL_SCHEME_sic_audit_report.txt")

PROPERTY_SICS    = {"68100","68209","68310","68201","68202","68203","68320"}
MANAGEMENT_CONSULT = "70229"

# ── Always clear stale cache ──────────────────────────────────────────────────
if os.path.exists(CACHE_FILE):
    os.remove(CACHE_FILE)
    print("Stale cache cleared.")

# ── SSL context (same as fetch_ch.py) ────────────────────────────────────────
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE

class NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req and "Authorization" in new_req.headers:
            del new_req.headers["Authorization"]
        if new_req and "authorization" in new_req.unredirected_hdrs:
            del new_req.unredirected_hdrs["authorization"]
        return new_req

opener = urllib.request.build_opener(
    NoAuthRedirectHandler(),
    urllib.request.HTTPSHandler(context=ctx)
)
urllib.request.install_opener(opener)

def _auth_header():
    return "Basic " + base64.b64encode(f"{API_KEY}:".encode()).decode()

def get_company_profile(company_number):
    """Fetch company profile (including sic_codes) from CH API."""
    cn = str(company_number).strip().zfill(8)
    url = f"{BASE_URL}/company/{cn}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", _auth_header())
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 429:
            print("    ⚠ Rate limited — waiting 20s...")
            time.sleep(20)
            try:
                with urllib.request.urlopen(req, timeout=12) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except Exception:
                return None
        print(f"    HTTP {e.code} for {cn}")
        return None
    except Exception as e:
        print(f"    Error {cn}: {e}")
        return None

# ── Quick API key test ────────────────────────────────────────────────────────
print("Testing API key...")
test = get_company_profile("06993349")
if not test:
    print("ERROR: API key rejected or no response. Exiting.")
    exit(1)
print(f"  OK — {test.get('company_name')}  SIC: {test.get('sic_codes')}")

# ── Load existing Adrem mis-classification records ────────────────────────────
adrem_records = []
with open(EXISTING_SIC, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        adrem_records.append(row)
print(f"\nAdrem (CW12 4AA) confirmed SIC 70229 : {len(adrem_records)}")

# ── Load Wincham company numbers ──────────────────────────────────────────────
wincham_cos = []
with open(WINCHAM_CSV, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        num = row.get("Company Number","").strip().zfill(8)
        if num:
            wincham_cos.append({
                "company_number": num,
                "company_name":   row.get("Company Name","").strip(),
                "status":         row.get("Status","").strip(),
                "date_inc":       row.get("Date Incorporated","").strip(),
                "directors":      row.get("Directors","").strip(),
                "dir_addrs":      row.get("Director Addresses","").strip(),
            })

total = len(wincham_cos)
print(f"Wincham (CW12 4TR) companies to check: {total}")
print(f"Estimated time: ~{total * RATE_PAUSE / 60:.0f} minutes\n")

# ── Fetch SIC codes for each Wincham company ─────────────────────────────────
cache       = {}
results     = []
cnt_70229   = 0
cnt_prop    = 0
cnt_no_sic  = 0
cnt_other   = 0

for i, co in enumerate(wincham_cos):
    num = co["company_number"]
    profile = get_company_profile(num)
    time.sleep(RATE_PAUSE)

    sic_codes    = profile.get("sic_codes", []) if profile else []
    company_type = profile.get("type", "")    if profile else ""
    sic_str      = " | ".join(sic_codes)      if sic_codes else "NONE"

    has_70229   = MANAGEMENT_CONSULT in sic_codes
    has_prop    = any(s in PROPERTY_SICS for s in sic_codes)
    no_sic      = not sic_codes

    if has_70229:  cnt_70229  += 1
    elif has_prop: cnt_prop   += 1
    elif no_sic:   cnt_no_sic += 1
    else:          cnt_other  += 1

    results.append({
        "Company Name":             co["company_name"],
        "Company Number":           num,
        "Status":                   co["status"],
        "SIC Codes":                sic_str,
        "Date Incorporated":        co["date_inc"],
        "Company Type":             company_type,
        "SIC 70229?":               "YES" if has_70229 else "No",
        "Has Property SIC?":        "YES" if has_prop  else "No",
        "No SIC Filed":             "YES" if no_sic    else "No",
        "Migrated from Wincham":    "N/A",
        "Directors":                co["directors"],
        "Director Addresses":       co["dir_addrs"],
        "Cohort":                   "Wincham (CW12 4TR)",
    })

    if (i + 1) % 50 == 0 or (i + 1) == total:
        print(f"  [{i+1:3d}/{total}]  SIC 70229: {cnt_70229}  | "
              f"Property SIC: {cnt_prop}  |  No SIC: {cnt_no_sic}  |  Other: {cnt_other}")

# ── Write combined CSV ────────────────────────────────────────────────────────
FIELDS = ["Company Name","Company Number","Status","SIC Codes","Date Incorporated",
          "Company Type","SIC 70229?","Has Property SIC?","No SIC Filed",
          "Migrated from Wincham","Directors","Director Addresses","Cohort"]

with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
    w.writeheader()
    for r in results:
        w.writerow(r)
    for r in adrem_records:
        w.writerow({
            "Company Name":          r.get("Company Name",""),
            "Company Number":        r.get("Company Number","").zfill(8),
            "Status":                r.get("Status",""),
            "SIC Codes":             r.get("SIC Codes","70229"),
            "Date Incorporated":     r.get("Date Incorporated",""),
            "Company Type":          r.get("Company Type",""),
            "SIC 70229?":            "YES",
            "Has Property SIC?":     "No",
            "No SIC Filed":          "No",
            "Migrated from Wincham": r.get("Migrated from Wincham",""),
            "Directors":             r.get("Directors",""),
            "Director Addresses":    r.get("Director Addresses",""),
            "Cohort":                "Adrem (CW12 4AA)",
        })

combined_70229 = cnt_70229 + len(adrem_records)
combined_total = total + len(adrem_records)

report = f"""
================================================================================
FULL-SCHEME SIC CODE AUDIT — WINCHAM + ADREM (BOTH REGISTERED ADDRESSES)
Generated: {time.strftime('%d %B %Y %H:%M')}
================================================================================

WINCHAM COHORT (CW12 4TR — Greenfield Farm, Congleton) — {total} companies
-----------------------------------------------------------------------
  SIC 70229 — Management Consultancy (WRONG for property):  {cnt_70229:>5}  ({cnt_70229/total*100:.1f}%)
  Correct property SIC (68100/68209/68310):                 {cnt_prop:>5}  ({cnt_prop/total*100:.1f}%)
  No SIC code filed at all:                                 {cnt_no_sic:>5}  ({cnt_no_sic/total*100:.1f}%)
  Other code (not 70229, not property):                     {cnt_other:>5}  ({cnt_other/total*100:.1f}%)

ADREM COHORT (CW12 4AA — Albert Chambers, Congleton) — {len(adrem_records)} companies
--------------------------------------------------------------------
  SIC 70229 confirmed (all records):                        {len(adrem_records):>5}  (100% of cohort)
  (197 total Adrem; 167 = 84.8% were SIC 70229 — confirmed previously)

COMBINED TOTALS (Both addresses)
-----------------------------------------------
  Total companies audited:                                  {combined_total:>5}
  Total confirmed on wrong SIC 70229:                       {combined_70229:>5}  ({combined_70229/combined_total*100:.1f}%)
  Wincham-only with NO SIC filed:                           {cnt_no_sic:>5}

CORRECT SIC FOR SPANISH PROPERTY HOLDING VEHICLES
  68100 — Buying and selling of own real estate
  68209 — Other letting and operating of own / leased real estate
  68310 — Real estate agencies

WRONG CODE APPLIED
  70229 — Management consultancy activities (other than financial management)

OUTPUT: {OUT_CSV}
================================================================================
"""

with open(REPORT_TXT, "w", encoding="utf-8") as f:
    f.write(report)

print(report)
print(f"\n✓ {OUT_CSV}")
print(f"✓ {REPORT_TXT}")
