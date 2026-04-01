"""
Parse all 10 downloaded Companies House pages for CW12 4AA
and build a clean CSV, then enrich with director data via API.
"""
import re
import csv
import os
import requests
import time
import sys

API_KEY = "445f486c-a61d-49ec-be74-3e16e0fa8c83"
BASE_API = "https://api.company-information.service.gov.uk"
OUTPUT_FILE = "adrem_cw12_4aa_leads.csv"

# Paths to the downloaded markdown files (pages 1-10)
BRAIN = r"C:\Users\Dean Harrison\.gemini\antigravity\brain\a0404328-6429-4520-a1d7-281b695738e5\.system_generated\steps"
PAGE_FILES = {
    1: os.path.join(BRAIN, "122", "content.md"),   # page 1 fetched earlier
    2: os.path.join(BRAIN, "149", "content.md"),
    3: os.path.join(BRAIN, "152", "content.md"),
    4: os.path.join(BRAIN, "153", "content.md"),
    5: os.path.join(BRAIN, "154", "content.md"),
    6: os.path.join(BRAIN, "157", "content.md"),
    7: os.path.join(BRAIN, "158", "content.md"),
    8: os.path.join(BRAIN, "159", "content.md"),
    9: os.path.join(BRAIN, "160", "content.md"),
    10: os.path.join(BRAIN, "161", "content.md"),
}


def parse_page(filepath):
    """
    Parse a markdown-converted Companies House results page.
    
    The format from read_url_content looks like:
    ## [COMPANY NAME(link opens a new window)](https://find-.../company/NNNNNNNN)
    [COMPANY NAME(link opens a new window)](https://find-.../company/NNNNNNNN)
    Active    (or Dissolved)
    - Private limited company
    - 
    - NNNNNNNN - Incorporated on DD Month YYYY
    """
    companies = []
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Cannot read {filepath}: {e}")
        return companies

    # Extract blocks: each company has the pattern:
    # company_number appears in the URL /company/NNNNNNNN
    # company name appears in the ## heading
    # status appears right after the repeated link line

    # Pattern: ## [NAME(link opens a new window)](URL/company/NUMBER)
    block_pattern = re.compile(
        r'## \[([^\]]+)\(link opens a new window\)\]\([^)]+/company/(\d{5,9})\)',
        re.IGNORECASE
    )

    # Find all company blocks
    matches = list(block_pattern.finditer(content))
    
    for idx, m in enumerate(matches):
        raw_name = m.group(1).strip()
        company_number = m.group(2)
        
        # Get the text between this match and the next (to find status)
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        block_text = content[start:end]
        
        # Find status
        status_match = re.search(r'\b(Active|Dissolved|Liquidation|Administration|Receivership)\b', block_text)
        status = status_match.group(1) if status_match else ""
        
        # Find incorporation date
        date_match = re.search(r'Incorporated on (\d+ \w+ \d{4})', block_text)
        date_inc = date_match.group(1) if date_match else ""
        
        # Find dissolution date
        diss_match = re.search(r'Dissolved on (\d+ \w+ \d{4})', block_text)
        date_dis = diss_match.group(1) if diss_match else ""
        
        # Find company type
        type_match = re.search(r'- (Private limited company|Public limited company|Limited liability partnership|Community interest company|Industrial and provident society)', block_text)
        company_type = type_match.group(1) if type_match else ""
        
        # Find SIC codes
        sic_match = re.search(r'SIC codes? - ([\d, ]+)', block_text)
        sic_codes = sic_match.group(1).strip() if sic_match else ""
        
        # Find registered address
        addr_match = re.search(r'- ([^-\n]{15,100}CW12[^-\n]+)', block_text)
        address = addr_match.group(1).strip() if addr_match else ""
        
        companies.append({
            "company_name": raw_name,
            "company_number": company_number,
            "status": status,
            "type": company_type,
            "date_incorporated": date_inc,
            "date_dissolved": date_dis,
            "sic_codes": sic_codes,
            "address": address,
        })
    
    return companies


def fetch_directors(company_number):
    url = f"{BASE_API}/company/{company_number}/officers"
    try:
        resp = requests.get(url, auth=(API_KEY, ""), timeout=15)
        if resp.status_code != 200:
            return []
        
        directors = []
        for item in resp.json().get("items", []):
            if "director" not in item.get("officer_role", "").lower():
                continue
            if item.get("resigned_on"):
                continue
            
            addr = item.get("address", {})
            address_str = ", ".join(filter(None, [
                addr.get("care_of", ""),
                addr.get("premises", ""),
                addr.get("address_line_1", ""),
                addr.get("address_line_2", ""),
                addr.get("locality", ""),
                addr.get("region", ""),
                addr.get("postal_code", ""),
                addr.get("country", ""),
            ]))
            
            directors.append({
                "name": item.get("name", ""),
                "role": item.get("officer_role", ""),
                "address": address_str,
                "appointed_on": item.get("appointed_on", ""),
            })
        return directors
    except Exception:
        return []


def main():
    print("=" * 62)
    print("  ADREM CW12 4AA — PARSING DOWNLOADED PAGES")
    print("=" * 62)
    
    # ── Step 1: Parse all pages ─────────────────────────────────
    print("\n[1/3] Parsing 10 downloaded page files...")
    
    all_companies = {}
    for page_num, filepath in PAGE_FILES.items():
        exists = os.path.exists(filepath)
        companies = parse_page(filepath) if exists else []
        new = 0
        for c in companies:
            if c["company_number"] not in all_companies:
                all_companies[c["company_number"]] = c
                new += 1
        status_str = f"+{new} new" if exists else "FILE NOT FOUND"
        print(f"  Page {page_num:2d}: {status_str} (total: {len(all_companies)})")
    
    print(f"\n  Total unique companies: {len(all_companies)}")
    
    if not all_companies:
        print("\n  ERROR: No companies parsed. Check file paths and content.")
        return
    
    # ── Step 2: Test API ─────────────────────────────────────────
    print(f"\n[2/3] Testing API key and fetching directors...")
    test = requests.get(f"{BASE_API}/company/06993349", auth=(API_KEY, ""), timeout=15)
    print(f"  API test (Los Romeros 06993349): HTTP {test.status_code}")
    use_api = test.status_code == 200
    
    if use_api:
        data = test.json()
        print(f"  ✓ LOS ROMEROS LIMITED — Status: {data.get('company_status','?')}")
        addr = data.get("registered_office_address", {})
        print(f"  ✓ Address: {addr.get('address_line_1','')}, {addr.get('postal_code','')}")
    else:
        print(f"  ✗ API key not working — will save company list without directors")
    
    # ── Step 3: Write CSV ─────────────────────────────────────────
    companies_list = list(all_companies.values())
    rows_written = 0
    los_romeros_in_list = "06993349" in all_companies
    
    print(f"\n  Writing CSV{'+ fetching directors' if use_api else ''} for {len(companies_list)} companies...")
    
    # Sort: active first, then by name
    companies_list.sort(key=lambda c: (c["status"] != "Active", c["company_name"]))
    
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Company Name", "Company Number", "Status", "Type",
            "Date Incorporated", "Date Dissolved", "SIC Codes",
            "Registered Address",
            "Director Name", "Director Role",
            "Director Correspondence Address (LEAD)", "Director Appointed",
        ])
        
        for i, company in enumerate(companies_list):
            num = company["company_number"]
            name = company["company_name"]
            
            if use_api:
                sys.stdout.write(f"\r  [{i+1:3d}/{len(companies_list)}] {name[:50]:<50}")
                sys.stdout.flush()
            
            if num == "06993349":
                print(f"\n  *** LOS ROMEROS LIMITED ({num}) — CONFIRMED ***")
            
            directors = fetch_directors(num) if use_api else []
            
            if directors:
                for d in directors:
                    writer.writerow([
                        name, num, company["status"], company["type"],
                        company["date_incorporated"], company["date_dissolved"],
                        company["sic_codes"], company["address"],
                        d["name"], d["role"], d["address"], d["appointed_on"],
                    ])
                    rows_written += 1
            else:
                writer.writerow([
                    name, num, company["status"], company["type"],
                    company["date_incorporated"], company["date_dissolved"],
                    company["sic_codes"], company["address"],
                    "", "", "", "",
                ])
                rows_written += 1
            
            if use_api:
                time.sleep(0.6)
    
    print(f"\n\n{'=' * 62}")
    print(f"  COMPLETE")
    print(f"{'=' * 62}")
    print(f"  Companies processed : {len(companies_list)}")
    print(f"  Rows written        : {rows_written}")
    print(f"  Output              : {OUTPUT_FILE}")
    print(f"  Los Romeros in list : {'YES ✓' if los_romeros_in_list else 'No (check number 06993349)'}")
    print()


if __name__ == "__main__":
    main()
