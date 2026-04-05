"""
latest_signup_from_existing_data.py
====================================
Reads the existing CSVs we've already pulled from Companies House
and finds the most recently incorporated companies across all Wincham cohorts.

Also queries the CH API directly with the correct search approach to find
any companies more recent than what we have.
"""

import ssl, base64, json, time, urllib.request, urllib.error, csv, os

API_KEY  = "37e01bb5-04e8-4d0d-9895-9037e31e2e36"
BASE_URL = "https://api.company-information.service.gov.uk"
BASE_DIR = r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action"

# ── SSL setup ─────────────────────────────────────────────────────────────────
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE

class NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req:
            new_req.headers.pop("Authorization", None)
            new_req.unredirected_hdrs.pop("authorization", None)
        return new_req

opener = urllib.request.build_opener(NoAuthRedirectHandler(), urllib.request.HTTPSHandler(context=ctx))
urllib.request.install_opener(opener)

def auth_header():
    return "Basic " + base64.b64encode(f"{API_KEY}:".encode()).decode()

def get_json(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", auth_header())
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 1: Analyse existing CSVs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*70)
print("  PART 1: EXISTING DATA — MOST RECENT INCORPORATIONS")
print("="*70)

csv_files = [
    ("wincham_only_companies.csv",  "Wincham (CW12 4TR)"),
    ("adrem_only_companies.csv",    "Adrem (CW12 4AA)"),
    ("adrem_leads.csv",             "Adrem Leads (full)"),
    ("wincham_leads.csv",           "Wincham Leads (full)"),
    ("FULL_SCHEME_sic_misclassification.csv", "Full Scheme Combined"),
]

all_companies = []

for filename, label in csv_files:
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  ⚠ Not found: {filename}")
        continue
    
    try:
        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Find date column
        date_col = None
        name_col = None
        num_col  = None
        status_col = None
        
        for k in (rows[0].keys() if rows else []):
            kl = k.lower()
            if "date" in kl and ("inc" in kl or "creat" in kl or "incorporat" in kl):
                date_col = k
            elif "company name" in kl or kl == "name":
                name_col = k
            elif "company number" in kl or kl == "number":
                num_col = k
            elif "status" in kl:
                status_col = k
        
        if not date_col:
            # Try any date field
            for k in (rows[0].keys() if rows else []):
                if "date" in k.lower():
                    date_col = k
                    break
        
        if not date_col:
            print(f"  ⚠ {filename}: no date column found. Columns: {list(rows[0].keys()) if rows else []}")
            continue
        
        company_dates = []
        seen = set()
        for r in rows:
            dt  = r.get(date_col, "").strip()
            nm  = r.get(name_col or "Company Name", r.get("company_name", "")).strip()
            num = r.get(num_col or "Company Number", r.get("company_number", "")).strip()
            st  = r.get(status_col or "Status", r.get("company_status", "")).strip()
            if dt and num and num not in seen:
                seen.add(num)
                company_dates.append((dt, nm, num, st, label))
                all_companies.append((dt, nm, num, st, label + f" [{filename}]"))
        
        company_dates.sort(reverse=True)
        print(f"\n  📁 {label}  ({filename})  — {len(company_dates)} unique companies")
        print(f"     Date column used: '{date_col}'")
        print(f"     {'Date':<12}  {'Company Name':<45}  {'Number':<10}  Status")
        print(f"     {'-'*90}")
        for dt, nm, num, st, _ in company_dates[:10]:
            print(f"     {dt:<12}  {nm[:44]:<45}  {num:<10}  {st}")
        if len(company_dates) > 10:
            print(f"     ... and {len(company_dates)-10} more")
            
    except Exception as e:
        print(f"  ⚠ Error reading {filename}: {e}")

# ── Deduplicate all_companies and find overall most recent ─────────────────────
seen_global = set()
unique_all = []
for item in all_companies:
    if item[2] not in seen_global:
        seen_global.add(item[2])
        unique_all.append(item)

unique_all.sort(reverse=True)

print("\n" + "="*70)
print(f"  OVERALL: TOP 20 MOST RECENTLY INCORPORATED — ALL COHORTS COMBINED")
print(f"  (Deduplicated: {len(unique_all)} unique companies across all files)")
print("="*70)
print(f"  {'Date':<12}  {'Company Name':<45}  {'Number':<10}  {'Status':<15}  Source")
print(f"  {'-'*110}")
for dt, nm, num, st, src in unique_all[:20]:
    print(f"  {dt:<12}  {nm[:44]:<45}  {num:<10}  {st:<15}  {src}")

if unique_all:
    latest = unique_all[0]
    print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  📌 LAST KNOWN SIGN-UP IN EXISTING DATA:")
    print(f"     Date:    {latest[0]}")
    print(f"     Company: {latest[1]}")
    print(f"     Number:  {latest[2]}")
    print(f"     Status:  {latest[3]}")
    print(f"     Source:  {latest[4]}")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 2: Live CH API — search by OFFICER NAME (most reliable method)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*70)
print("  PART 2: LIVE API — SEARCH BY KNOWN WINCHAM OFFICER/SECRETARY NAMES")
print("  (Most reliable way to find recently-formed companies in the scheme)")
print("="*70)

# Key Wincham-linked officer/secretary names to search
WINCHAM_OFFICERS = [
    "ADREM GROUP LIMITED",
    "Adrem Group",
    "Wincham International",
    "WINCHAM INTERNATIONAL LIMITED",
]

for officer_name in WINCHAM_OFFICERS:
    encoded = urllib.parse.quote(officer_name) if hasattr(urllib, 'parse') else officer_name.replace(' ', '+')
    url = f"{BASE_URL}/search/officers?q={encoded}&items_per_page=10"
    try:
        import urllib.parse
        encoded = urllib.parse.quote(officer_name)
        url = f"{BASE_URL}/search/officers?q={encoded}&items_per_page=20"
        data = get_json(url)
        items = data.get("items", [])
        print(f"\n  Searching officer: '{officer_name}' → {len(items)} result(s)")
        for item in items[:5]:
            print(f"    {item.get('title','')}: {item.get('description','')[:80]}")
    except Exception as e:
        print(f"  ⚠ Error searching '{officer_name}': {e}")
    time.sleep(0.5)

# ── Direct company search for Wincham-named entities ─────────────────────────
print("\n  Searching for Wincham-named companies …")
for search_term in ["Wincham", "Adrem Group"]:
    try:
        import urllib.parse
        url = f"{BASE_URL}/search/companies?q={urllib.parse.quote(search_term)}&items_per_page=20"
        data = get_json(url)
        items = data.get("items", [])
        print(f"\n  '{search_term}': {len(items)} results")
        for item in items[:10]:
            print(f"    {item.get('date_of_creation','?'):<12}  {item.get('title',''):<45}  {item.get('company_number',''):<10}  {item.get('company_status','')}")
    except Exception as e:
        print(f"  ⚠ Error: {e}")
    time.sleep(0.5)
