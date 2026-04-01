"""
Cross-Reference Analysis: CW12 4TR (Wincham) vs CW12 4AA (Adrem)
=================================================================
Matches by COMPANY NUMBER (primary) and COMPANY NAME (secondary fallback).

Wincham CSV columns: Company Name, Company Number, Status, Date of Creation,
                     Director Name, Director Address (LEAD)

Adrem CSV columns  : Company Name, Company Number, Status, Date Incorporated,
                     SIC Codes, Company Type, Registered Office Address,
                     Director Name, Director Role, Director Appointed Date,
                     Director Correspondence Address (LEAD)
"""

import csv
import collections

BASE = r"c:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action"
ADREM_FILE   = f"{BASE}\\adrem_cw12_4aa_leads.csv"
WINCHAM_FILE = f"{BASE}\\wincham_leads.csv"

# ── Loaders ───────────────────────────────────────────────────────────────────

def norm_num(s):
    """Normalise company number: strip, zero-pad to 8 digits for CH numbers."""
    s = str(s).strip()
    # CH numbers are 8 chars; some are shorter with leading zeros missing
    if s.isdigit():
        return s.zfill(8)
    return s.upper()

def load_adrem(filepath):
    companies = {}
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            num  = norm_num(row.get("Company Number",""))
            name = row.get("Company Name","").strip().upper()
            if not num: continue
            if num not in companies:
                companies[num] = {
                    "company_number": num,
                    "company_name": name,
                    "status": row.get("Status","").strip().lower(),
                    "sic_codes": row.get("SIC Codes","").strip(),
                    "date_incorporated": row.get("Date Incorporated","").strip(),
                    "company_type": row.get("Company Type","").strip(),
                    "directors": [],
                }
            director = row.get("Director Name","").strip()
            addr     = row.get("Director Correspondence Address (LEAD)","").strip()
            if director:
                companies[num]["directors"].append({"name": director, "address": addr})
    return companies

def load_wincham(filepath):
    companies = {}
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            num  = norm_num(row.get("Company Number",""))
            name = row.get("Company Name","").strip().upper()
            if not num: continue
            if num not in companies:
                companies[num] = {
                    "company_number": num,
                    "company_name": name,
                    "status": row.get("Status","").strip().lower(),
                    "sic_codes": "N/A",
                    "date_incorporated": row.get("Date of Creation","").strip(),
                    "directors": [],
                }
            director = row.get("Director Name","").strip()
            addr     = row.get("Director Address (LEAD)","").strip()
            if director:
                companies[num]["directors"].append({"name": director, "address": addr})
    return companies

print("Loading datasets...")
adrem   = load_adrem(ADREM_FILE)
wincham = load_wincham(WINCHAM_FILE)

adrem_nums   = set(adrem.keys())
wincham_nums = set(wincham.keys())

# Primary: number-based match
migrated_by_num = adrem_nums & wincham_nums

# Secondary: name-based match (for any gaps)
adrem_names   = { c["company_name"]: num for num, c in adrem.items() }
wincham_names = { c["company_name"]: num for num, c in wincham.items() }
migrated_by_name = set(adrem_names.keys()) & set(wincham_names.keys())

migrated_name_only = migrated_by_name - { adrem[n]["company_name"] for n in migrated_by_num }

print(f"\nWincham (CW12 4TR) unique companies : {len(wincham_nums)}")
print(f"Adrem   (CW12 4AA) unique companies : {len(adrem_nums)}")
print(f"Matched by company NUMBER           : {len(migrated_by_num)}")
print(f"Matched by company NAME (fallback)  : {len(migrated_by_name)}")
print(f"  Name-only matches (no # match)    : {len(migrated_name_only)}")

adrem_only   = adrem_nums - wincham_nums
wincham_only = wincham_nums - adrem_nums

# Combine all migrated sets
all_migrated_adrem_nums = migrated_by_num.copy()
for name in migrated_name_only:
    adrem_num = adrem_names[name]
    all_migrated_adrem_nums.add(adrem_num)

print(f"\nTotal effectively migrated companies: {len(all_migrated_adrem_nums)}")
print(f"Adrem-only (no wincham connection)  : {len(adrem_only - all_migrated_adrem_nums)}")
print(f"Wincham-only (still at old address) : {len(wincham_only)}")

# ── Combined dataset for SIC analysis ─────────────────────────────────────────
# adrem has SIC codes, wincham doesn't — use adrem as primary
sic70229 = {num: c for num, c in adrem.items() if "70229" in c.get("sic_codes","") }
print(f"\nSIC 70229 (adrem dataset only)      : {len(sic70229)}")

# ── Helper: write CSV ──────────────────────────────────────────────────────────
def write_csv(filepath, rows, fieldnames):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

# ── 1. MIGRATED companies CSV ──────────────────────────────────────────────────
migrated_rows = []
for num in sorted(all_migrated_adrem_nums):
    c = adrem[num]
    # Get old wincham data if available
    wc = wincham.get(num)
    old_dirs = " | ".join(d["name"] for d in wc["directors"]) if wc else "(name match)"
    new_dirs = " | ".join(d["name"] for d in c["directors"])
    new_addrs = " | ".join(d["address"] for d in c["directors"])
    migrated_rows.append({
        "Company Name": c["company_name"],
        "Company Number": num,
        "Status (Adrem)": c["status"],
        "SIC Codes": c["sic_codes"],
        "Date Incorporated": c["date_incorporated"],
        "Directors (OLD Wincham)": old_dirs,
        "Directors (NEW Adrem)": new_dirs,
        "New Director Addresses": new_addrs,
        "Match Type": "Number" if num in migrated_by_num else "Name",
    })

write_csv(
    f"{BASE}\\migrated_companies.csv",
    migrated_rows,
    ["Company Name","Company Number","Status (Adrem)","SIC Codes","Date Incorporated",
     "Directors (OLD Wincham)","Directors (NEW Adrem)","New Director Addresses","Match Type"],
)
print(f"\n✓ migrated_companies.csv  : {len(migrated_rows)} rows")

# ── 2. Adrem-ONLY companies CSV ────────────────────────────────────────────────
adrem_only_rows = []
for num in sorted(adrem_only - all_migrated_adrem_nums):
    c = adrem[num]
    dirs  = " | ".join(d["name"]    for d in c["directors"])
    addrs = " | ".join(d["address"] for d in c["directors"])
    adrem_only_rows.append({
        "Company Name": c["company_name"],
        "Company Number": num,
        "Status": c["status"],
        "SIC Codes": c["sic_codes"],
        "Date Incorporated": c["date_incorporated"],
        "Company Type": c["company_type"],
        "Directors": dirs,
        "Director Addresses": addrs,
    })

write_csv(
    f"{BASE}\\adrem_only_companies.csv",
    adrem_only_rows,
    ["Company Name","Company Number","Status","SIC Codes","Date Incorporated",
     "Company Type","Directors","Director Addresses"],
)
print(f"✓ adrem_only_companies.csv : {len(adrem_only_rows)} rows")

# ── 3. Wincham-ONLY companies CSV ─────────────────────────────────────────────
wincham_only_rows = []
for num in sorted(wincham_only):
    c = wincham[num]
    dirs  = " | ".join(d["name"]    for d in c["directors"])
    addrs = " | ".join(d["address"] for d in c["directors"])
    wincham_only_rows.append({
        "Company Name": c["company_name"],
        "Company Number": num,
        "Status": c["status"],
        "Date Incorporated": c["date_incorporated"],
        "Directors": dirs,
        "Director Addresses": addrs,
    })

write_csv(
    f"{BASE}\\wincham_only_companies.csv",
    wincham_only_rows,
    ["Company Name","Company Number","Status","Date Incorporated",
     "Directors","Director Addresses"],
)
print(f"✓ wincham_only_companies.csv: {len(wincham_only_rows)} rows")

# ── 4. HMRC SIC mis-classification CSV ────────────────────────────────────────
hmrc_rows = []
for num in sorted(sic70229.keys()):
    c = sic70229[num]
    is_migrated = num in all_migrated_adrem_nums
    dirs  = " | ".join(d["name"]    for d in c["directors"])
    addrs = " | ".join(d["address"] for d in c["directors"])
    hmrc_rows.append({
        "Company Name": c["company_name"],
        "Company Number": num,
        "Status": c["status"],
        "SIC Codes": c["sic_codes"],
        "Date Incorporated": c["date_incorporated"],
        "Company Type": c["company_type"],
        "Migrated from Wincham": "YES" if is_migrated else "No",
        "Directors": dirs,
        "Director Addresses": addrs,
    })

write_csv(
    f"{BASE}\\hmrc_sic_misclassification.csv",
    hmrc_rows,
    ["Company Name","Company Number","Status","SIC Codes","Date Incorporated",
     "Company Type","Migrated from Wincham","Directors","Director Addresses"],
)
print(f"✓ hmrc_sic_misclassification.csv: {len(hmrc_rows)} rows")

# ── Final summary ─────────────────────────────────────────────────────────────
net_adrem_only = len(adrem_only - all_migrated_adrem_nums)

print(f"""
{'='*65}
FINAL CROSS-REFERENCE SUMMARY
{'='*65}
Wincham (CW12 4TR)             :  {len(wincham_nums)} unique companies
Adrem   (CW12 4AA)             :  {len(adrem_nums)} unique companies
Combined unique total           :  {len(adrem_nums | wincham_nums)}
────────────────────────────────────────────────────────────────
Confirmed migrated to CW12 4AA :  {len(all_migrated_adrem_nums)}
  └ Matched by company number  :    {len(migrated_by_num)}
  └ Matched by company name    :    {len(migrated_name_only)}
New Adrem-only (no Wincham tie):  {net_adrem_only}
Still only at CW12 4TR         :  {len(wincham_only)}
────────────────────────────────────────────────────────────────
SIC 70229 (Adrem records only) :  {len(sic70229)} companies
  (Note: Wincham CSV had no SIC codes - Adrem API data used)
  Correct SIC for Spanish property holding = 68100 / 68209
{'='*65}
""")

# Sample prints
if all_migrated_adrem_nums:
    print(f"SAMPLE — First 30 MIGRATED companies:")
    for num in sorted(list(all_migrated_adrem_nums))[:30]:
        c = adrem[num]
        match_type = "NUM" if num in migrated_by_num else "NAME"
        print(f"  [{match_type}] {c['company_name']:<45} ({num})")
else:
    print("No migrated companies found — check company number formats below:")
    print("  Wincham samples:", list(wincham_nums)[:5])
    print("  Adrem samples  :", list(adrem_nums)[:5])

print(f"\nSAMPLE — SIC 70229 companies:")
for num in sorted(list(sic70229.keys()))[:20]:
    c = sic70229[num]
    dirs = ", ".join(d["name"] for d in c["directors"][:2])
    print(f"  {c['company_name']:<45} ({num}) — {dirs[:60]}")
