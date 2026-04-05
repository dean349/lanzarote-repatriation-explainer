"""
find_latest_appointments.py
============================
Uses the Companies House API to find the most recently appointed companies
where ADREM ACCOUNTING LTD (company secretary) or WINCHAM ACCOUNTANTS LIMITED
are listed as officers/secretaries.

This gives us the definitive answer to: "When did Wincham last sign up a client?"

Key officer companies found:
  ADREM ACCOUNTING LTD:        461 appointments (company number from search)
  WINCHAM ACCOUNTANTS LIMITED: 782 appointments (company number from search)
"""

import ssl, base64, json, time, urllib.request, urllib.error, urllib.parse, csv, os

API_KEY  = "37e01bb5-04e8-4d0d-9895-9037e31e2e36"
BASE_URL = "https://api.company-information.service.gov.uk"
BASE_DIR = r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action"

# ── SSL ───────────────────────────────────────────────────────────────────────
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

def auth():
    return "Basic " + base64.b64encode(f"{API_KEY}:".encode()).decode()

def get_json(url, retries=3):
    req = urllib.request.Request(url)
    req.add_header("Authorization", auth())
    req.add_header("Accept", "application/json")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"    Rate limited (429), waiting 30s...")
                time.sleep(30)
            else:
                print(f"    HTTP {e.code}")
                return {}
        except Exception as e:
            print(f"    Error attempt {attempt+1}: {e}")
            time.sleep(2)
    return {}

def get_company_profile(company_number):
    """Get full company profile including registered office."""
    cn = str(company_number).strip().zfill(8)
    return get_json(f"{BASE_URL}/company/{cn}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: Get company numbers for Adrem Accounting and Wincham Accountants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*70)
print("  STEP 1: VERIFYING OFFICER COMPANY NUMBERS")
print("="*70)

# Known from previous searches and our research
OFFICER_COMPANIES = {
    "ADREM ACCOUNTING LTD":        None,  # Will look up
    "WINCHAM ACCOUNTANTS LIMITED": "05607266",  # From previous search
    "WINCHAM ACCOUNTANTS":         None,  # unincorporated / trading name
}

# Search for Adrem Accounting to get company number
print("\n  Looking up ADREM ACCOUNTING LTD...")
data = get_json(f"{BASE_URL}/search/companies?q={urllib.parse.quote('Adrem Accounting')}&items_per_page=10")
for item in data.get("items", []):
    print(f"    {item.get('date_of_creation','?'):<12}  {item.get('title',''):<50}  {item.get('company_number','')}")
    if "ADREM ACCOUNTING" in item.get("title","").upper():
        OFFICER_COMPANIES["ADREM ACCOUNTING LTD"] = item.get("company_number","")
        print(f"    ✓ Found: {item.get('company_number','')}")
        break
time.sleep(0.6)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: Get all appointments for each officer company
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*70)
print("  STEP 2: FETCHING ALL APPOINTMENTS (companies where they are secretary)")
print("="*70)

def fetch_all_appointments(company_number, company_name):
    """
    Fetch all companies where this company acts as an officer.
    Uses /company/{cn}/appointments  — paginated.
    """
    cn = str(company_number).strip().zfill(8)
    all_items = []
    start = 0
    page_size = 50
    
    while True:
        url = f"{BASE_URL}/company/{cn}/officers?items_per_page={page_size}&start_index={start}"
        # Actually - we need the APPOINTMENTS endpoint (companies THEY are appointed to)
        # The correct endpoint is: GET /company/{company_number}/officers gives THIS company's officers
        # To find WHERE they are an officer, we need: GET /officers/{officer_id}/appointments
        # But we don't have officer IDs...
        
        # Alternative: search the officer search API
        url = f"{BASE_URL}/search/officers?q={urllib.parse.quote(company_name)}&items_per_page={page_size}&start_index={start}"
        data = get_json(url)
        items = data.get("items", [])
        
        if not items:
            break
        
        # Find the exact match
        for item in items:
            if item.get("title","").upper().strip() == company_name.upper().strip():
                # Found the officer record - get their appointments link
                links = item.get("links", {})
                appt_link = links.get("self", "")
                if appt_link:
                    print(f"    Officer link: {appt_link}")
                    # Get appointments
                    appt_url = BASE_URL + appt_link + "/appointments?items_per_page=50"
                    return appt_link, item
        
        if len(items) < page_size:
            break
        start += page_size
        time.sleep(0.3)
    
    return None, None

all_appointments = []

for officer_name, company_number in OFFICER_COMPANIES.items():
    if not company_number:
        print(f"\n  ⚠ No company number for '{officer_name}', skipping officer appointment lookup")
        continue
    
    cn = company_number.zfill(8)
    print(f"\n  ▶ {officer_name} ({cn})")
    
    # First get the company profile to verify
    profile = get_company_profile(cn)
    print(f"    Company: {profile.get('company_name', 'N/A')}")
    print(f"    Status:  {profile.get('company_status', 'N/A')}")
    print(f"    Registered: {profile.get('registered_office_address', {})}")
    time.sleep(0.6)
    
    # Now search officer search to find appointments link
    print(f"    Searching officer records for '{officer_name}'...")
    search_data = get_json(f"{BASE_URL}/search/officers?q={urllib.parse.quote(officer_name)}&items_per_page=20")
    time.sleep(0.6)
    
    officer_link = None
    for item in search_data.get("items", []):
        title = item.get("title","").upper().strip()
        desc  = item.get("description","")
        if officer_name.upper().strip() in title:
            links = item.get("links", {})
            self_link = links.get("self", "")
            print(f"    Found: {title} → {self_link}  ({desc})")
            if ("ADREM" in title or "WINCHAM ACCOUNTANTS" in title) and self_link:
                officer_link = self_link
                # Extract total appointments
                total_appts = item.get("description","")
                print(f"    Description: {total_appts}")
    
    if officer_link:
        print(f"    Fetching appointments via: {officer_link}/appointments")
        # Paginate through all appointments
        page_start = 0
        company_appointments = []
        
        while True:
            appt_url = f"{BASE_URL}{officer_link}/appointments?items_per_page=50&start_index={page_start}"
            appt_data = get_json(appt_url)
            items_page = appt_data.get("items", [])
            
            if not items_page:
                break
            
            total_count = appt_data.get("total_results", 0)
            
            for appt in items_page:
                company_appointments.append({
                    "officer":          officer_name,
                    "appointed_to":     appt.get("appointed_to", {}).get("company_name", ""),
                    "company_number":   appt.get("appointed_to", {}).get("company_number", ""),
                    "company_status":   appt.get("appointed_to", {}).get("company_status", ""),
                    "role":             appt.get("officer_role", ""),
                    "appointed_on":     appt.get("appointed_on", ""),
                    "resigned_on":      appt.get("resigned_on", ""),
                    "is_current":       "resigned_on" not in appt or not appt.get("resigned_on"),
                })
            
            print(f"    Page {page_start//50 + 1}: {len(items_page)} items (total: {total_count})")
            
            if len(items_page) < 50 or (page_start + 50) >= total_count:
                break
            
            page_start += 50
            time.sleep(0.6)
        
        all_appointments.extend(company_appointments)
        print(f"    Total appointments fetched: {len(company_appointments)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: Sort by appointment date and show most recent
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if all_appointments:
    # Sort by appointed_on date
    all_appointments.sort(key=lambda x: x.get("appointed_on",""), reverse=True)
    
    print("\n" + "="*70)
    print(f"  STEP 3: MOST RECENT CLIENT APPOINTMENTS — TOTAL: {len(all_appointments)}")
    print("="*70)
    print(f"  {'Appointed':<12}  {'Company Name':<45}  {'Number':<10}  {'Status':<12}  {'Role':<15}  Resigned?")
    print(f"  {'-'*115}")
    for appt in all_appointments[:30]:
        resigned = appt.get("resigned_on","") or "CURRENT"
        print(f"  {appt['appointed_on']:<12}  {appt['appointed_to'][:44]:<45}  {appt['company_number']:<10}  {appt['company_status']:<12}  {appt['role']:<15}  {resigned}")
    
    # Save to CSV
    out_file = os.path.join(BASE_DIR, "wincham_latest_appointments.csv")
    with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=all_appointments[0].keys())
        w.writeheader()
        w.writerows(all_appointments)
    print(f"\n  ✓ Saved to: {out_file}")
    
    # HEADLINE
    latest = all_appointments[0]
    print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  📌 MOST RECENT CLIENT APPOINTMENT DATE:")
    print(f"     Date Appointed: {latest['appointed_on']}")
    print(f"     Company:        {latest['appointed_to']}")
    print(f"     Number:         {latest['company_number']}")
    print(f"     Status:         {latest['company_status']}")
    print(f"     Officer role:   {latest['role']}")
    print(f"     Acting for:     {latest['officer']}")
    resigned = latest.get("resigned_on","")
    if resigned:
        print(f"     ⚠ Resigned:    {resigned}")
    else:
        print(f"     ✓ STILL CURRENT/ACTIVE APPOINTMENT")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
else:
    print("\n  ⚠ No appointments data retrieved — may need officer ID approach")
    print("    Try manual search at:")
    print("    https://find-and-update.company-information.service.gov.uk/officers/[officer_id]/appointments")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: Cross ref against existing data — find most recent in our dataset
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*70)
print("  STEP 4: EXISTING DATA — CORRECTED DATE SORT")
print("  (wincham_only_companies.csv + adrem_only_companies.csv)")
print("="*70)

combined = []
for fname, label in [
    ("wincham_only_companies.csv", "Wincham CW12 4TR"),
    ("adrem_only_companies.csv", "Adrem CW12 4AA"),
]:
    fpath = os.path.join(BASE_DIR, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            # Find date field
            dt = row.get("Date Incorporated","") or row.get("date_of_creation","") or row.get("Date of Creation","")
            dt = dt.strip()
            nm = row.get("Company Name","") or row.get("company_name","")
            nu = row.get("Company Number","") or row.get("company_number","")
            st = row.get("Status","") or row.get("company_status","")
            if dt:
                # Normalise ISO format  (YYYY-MM-DD)
                import re
                iso = re.search(r'(\d{4}-\d{2}-\d{2})', dt)
                if iso:
                    combined.append((iso.group(1), nm.strip(), nu.strip(), st.strip(), label))
                else:
                    # Try to parse "9 October 2019" style
                    from datetime import datetime
                    for fmt in ["%d %B %Y", "%d %b %Y", "%B %d, %Y"]:
                        try:
                            parsed = datetime.strptime(dt.strip(), fmt)
                            combined.append((parsed.strftime("%Y-%m-%d"), nm.strip(), nu.strip(), st.strip(), label))
                            break
                        except ValueError:
                            pass

# Deduplicate by company number
seen = set()
deduped = []
for item in combined:
    if item[2] not in seen:
        seen.add(item[2])
        deduped.append(item)

deduped.sort(reverse=True)

print(f"\n  {'Date':<12}  {'Company Name':<45}  {'Number':<10}  {'Status':<15}  Cohort")
print(f"  {'-'*105}")
for dt, nm, nu, st, lbl in deduped[:25]:
    print(f"  {dt:<12}  {nm[:44]:<45}  {nu:<10}  {st:<15}  {lbl}")

if deduped:
    latest2 = deduped[0]
    print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  📌 MOST RECENTLY INCORPORATED IN OUR EXISTING DATASET:")
    print(f"     Date:    {latest2[0]}")
    print(f"     Company: {latest2[1]}")
    print(f"     Number:  {latest2[2]}")
    print(f"     Status:  {latest2[3]}")
    print(f"     Source:  {latest2[4]}")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
