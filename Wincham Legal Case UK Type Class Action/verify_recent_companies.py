"""
verify_recent_companies.py
===========================
Takes the most recently incorporated companies at CW12 4TR/CW12 4AA
and verifies whether they are Spanish property holding vehicles
(part of the Wincham scheme) or just regular local businesses.

Key signals of a Wincham SCHEME company:
  - SIC code 70229 (Management Consultancy) — wrong for property
  - SIC code 68100/68209 (Property) — correct but listed by secretary
  - Company name is a random word + "Limited" (not a real business name)
  - Directors have addresses outside Congleton (foreign/UK-wide)
  - Registered office IS CW12 4TR or CW12 4AA
  - Often dissolved or still active but dormant

Regular Wincham ACCOUNTANCY clients (not scheme):
  - SIC codes for real businesses (trades, services, etc.)
  - Company name matches a real business
  - Directors live near Congleton

We'll check the top 30 most recent and score them.
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

def get_json(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", auth())
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("    ⏳ Rate limited, waiting 30s...")
            time.sleep(30)
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    return json.loads(r.read().decode())
            except:
                return {}
        return {}
    except Exception as e:
        return {}

SCHEME_SICS = {"70229", "68100", "68209", "68310", "68201", "68202", "68320"}
PROPERTY_SIC = {"68100", "68209", "68310", "68201", "68320"}

# ── Known recent companies from our data ────────────────────────────────────
# Taken from the sorted output - top 30 most recent
RECENT = [
    ("2026-03-27", "LTW PROPERTY LTD",                       "17121923", "Wincham CW12 4TR"),
    ("2026-03-24", "NB LANDSCAPES LTD",                      "17113179", "Wincham CW12 4TR"),
    ("2026-03-16", "BEARINGS & DRIVES HOLDINGS LIMITED",      "17092065", "Wincham CW12 4TR"),
    ("2026-03-11", "D4S HOLDCO LTD",                         "17085114", "Wincham CW12 4TR"),
    ("2026-02-26", "JAROCA JOINERY LTD",                     "17057644", "Wincham CW12 4TR"),
    ("2026-02-12", "N A B METALS LIMITED",                   "17029239", "Wincham CW12 4TR"),
    ("2026-02-04", "CARECONCEPTS (MAYFIELD) LTD",            "17012132", "Wincham CW12 4TR"),
    ("2025-11-10", "C & N MECHANICAL LTD",                   "16843738", "Wincham CW12 4TR"),
    ("2025-10-17", "J AMBROSE SERVICES LTD",                 "16792265", "Wincham CW12 4TR"),
    ("2025-10-14", "TURNAROUND CREATIVE LIMITED",            "16782897", "Wincham CW12 4TR"),
    ("2025-09-22", "2125 TM LTD",                            "16733538", "Wincham CW12 4TR"),
    ("2025-09-17", "AIM INSTALLATIONS LTD",                  "16725518", "Wincham CW12 4TR"),
    ("2025-08-28", "JPEG PROPERTIES LTD",                    "16679568", "Wincham CW12 4TR"),
    ("2025-07-14", "ROOFS R US (CONGLETON) LTD",             "16579764", "Wincham CW12 4TR"),
    ("2025-06-20", "CLIFFE EARTHMOVING LTD",                 "16531731", "Wincham CW12 4TR"),
    ("2025-04-25", "L P LANDSCAPES (NW) LTD",                "16409766", "Wincham CW12 4TR"),
    ("2025-04-22", "TWA DEVELOPMENTS LTD",                   "16397957", "Wincham CW12 4TR"),
    ("2025-03-20", "STARBOYCLUB LTD",                        "16329840", "Wincham CW12 4TR"),
    ("2025-03-18", "CLOUDVIEW ACCOUNTANTS LTD",              "16323046", "Wincham CW12 4TR"),
    ("2025-03-03", "ROYLES BEDS LTD",                        "16289276", "Wincham CW12 4TR"),
    ("2025-02-21", "B & R CONTRACTING LTD",                  "16268953", "Wincham CW12 4TR"),
    ("2025-02-05", "HUDSON AND BOWMAN LTD",                  "16230691", "Adrem CW12 4AA"),
    ("2025-01-24", "INTERVENTION FIRST LTD",                  "16206748", "Adrem CW12 4AA"),
    ("2024-11-12", "TURNAROUND PRINT SERVICES LTD",          "16076567", "Wincham CW12 4TR"),
    ("2024-11-04", "CARECONCEPTS (NORTH STAFFORDSHIRE) LTD", "16060255", "Wincham CW12 4TR"),
    ("2024-09-24", "WREXHAM CITY FC LIMITED",                 "15980000", "Wincham CW12 4TR"),  # placeholder
]

print("\n" + "="*70)
print("  VERIFYING MOST RECENT COMPANIES — SCHEME vs REGULAR CLIENTS")
print("  Checking SIC codes, director locations, and company characteristics")
print("="*70)

results = []

for date_inc, name, number, source in RECENT:
    cn = number.zfill(8)
    print(f"\n  Checking: {name} ({cn}) — {date_inc}")
    
    profile = get_json(f"{BASE_URL}/company/{cn}")
    time.sleep(0.6)
    
    if not profile:
        print(f"    ⚠ No data returned")
        continue
    
    sic_codes    = profile.get("sic_codes", [])
    company_type = profile.get("type", "")
    reg_office   = profile.get("registered_office_address", {})
    reg_postcode = reg_office.get("postal_code", "")
    company_name = profile.get("company_name", name)
    status       = profile.get("company_status", "")
    
    # Get officers
    officers_data = get_json(f"{BASE_URL}/company/{cn}/officers")
    time.sleep(0.6)
    
    directors = []
    secretaries = []
    has_wincham_secretary = False
    director_postcodes = []
    
    for officer in officers_data.get("items", []):
        role = officer.get("officer_role","").lower()
        nm   = officer.get("name","")
        addr = officer.get("address", {})
        pc   = addr.get("postal_code","")
        
        if "director" in role and not officer.get("resigned_on"):
            directors.append(f"{nm} [{pc}]")
            director_postcodes.append(pc)
        elif "secretary" in role and not officer.get("resigned_on"):
            secretaries.append(nm)
            if "WINCHAM" in nm.upper() or "ADREM" in nm.upper():
                has_wincham_secretary = True
    
    # Score: is this a scheme company?
    is_scheme = False
    scheme_signals = []
    
    if "70229" in sic_codes:
        is_scheme = True
        scheme_signals.append("SIC 70229 (Mgmt Consultancy - wrong for property)")
    if any(s in PROPERTY_SIC for s in sic_codes):
        is_scheme = True
        scheme_signals.append(f"Property SIC {sic_codes}")
    if has_wincham_secretary:
        is_scheme = True
        scheme_signals.append("Wincham/Adrem named as secretary")
    if reg_postcode in ("CW12 4TR", "CW12 4AA"):
        scheme_signals.append(f"Registered at {reg_postcode}")
    
    # Check if directors are NOT from Congleton area (scheme signal)
    local_directors = [pc for pc in director_postcodes if "CW12" in pc or "CW11" in pc]
    if director_postcodes and not local_directors:
        scheme_signals.append(f"Directors from outside Congleton: {director_postcodes[:3]}")
    
    verdict = "⚠ POSSIBLE SCHEME" if is_scheme else "✓ Regular Client"
    if not scheme_signals:
        verdict = "✓ Regular Wincham accountancy client (not scheme)"
    if is_scheme:
        verdict = "🚨 LIKELY SCHEME COMPANY"
    
    results.append({
        "date_incorporated": date_inc,
        "company_name":      company_name,
        "company_number":    cn,
        "status":            status,
        "sic_codes":         " | ".join(sic_codes),
        "reg_postcode":      reg_postcode,
        "directors":         "; ".join(directors[:3]),
        "secretaries":       "; ".join(secretaries[:2]),
        "has_wincham_sec":   "YES" if has_wincham_secretary else "No",
        "scheme_signals":    "; ".join(scheme_signals),
        "verdict":           verdict,
        "source":            source,
    })
    
    print(f"    SIC:       {sic_codes}")
    print(f"    Secretary: {secretaries}")
    print(f"    Directors: {directors[:3]}")
    print(f"    Signals:   {scheme_signals}")
    print(f"    VERDICT:   {verdict}")

# ── Save and summarise ────────────────────────────────────────────────────────
print("\n" + "="*70)
print("  SUMMARY: VERIFICATION RESULTS")
print("="*70)

scheme_companies = [r for r in results if "SCHEME" in r["verdict"]]
regular_companies = [r for r in results if "SCHEME" not in r["verdict"]]

print(f"\n  Total checked:      {len(results)}")
print(f"  🚨 Scheme companies: {len(scheme_companies)}")
print(f"  ✓ Regular clients:  {len(regular_companies)}")

if scheme_companies:
    print(f"\n  SCHEME COMPANIES (most recent last known sign-ups):")
    print(f"  {'Date':<12}  {'Company Name':<45}  {'Number':<10}  Signals")
    print(f"  {'-'*100}")
    for r in sorted(scheme_companies, key=lambda x: x["date_incorporated"], reverse=True):
        print(f"  {r['date_incorporated']:<12}  {r['company_name'][:44]:<45}  {r['company_number']:<10}  {r['scheme_signals'][:60]}")
    
    latest_scheme = max(scheme_companies, key=lambda x: x["date_incorporated"])
    print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  📌 MOST RECENTLY INCORPORATED SCHEME COMPANY:")
    print(f"     Date:     {latest_scheme['date_incorporated']}")
    print(f"     Company:  {latest_scheme['company_name']}")
    print(f"     Number:   {latest_scheme['company_number']}")
    print(f"     Status:   {latest_scheme['status']}")
    print(f"     Signals:  {latest_scheme['scheme_signals']}")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Save full results
out = os.path.join(BASE_DIR, "recent_companies_verified.csv")
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=results[0].keys() if results else [])
    w.writeheader()
    w.writerows(results)
print(f"\n  ✓ Saved: {out}")
