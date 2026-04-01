import requests
import time
import csv
import sys
import os

print("\n--- Wincham Lead Generator: Companies House ---")

# This script uses the Companies House REST API
# Sign up at: https://developer.company-information.service.gov.uk/
API_KEY = os.environ.get("COMPANIES_HOUSE_API_KEY", "")

if not API_KEY:
    print("ERROR: Missing API Key.")
    print("Please get a free API key and set it as an environment variable:")
    print("  $env:COMPANIES_HOUSE_API_KEY='your-key-here'")
    print("Or add it to this script directly before running.")
    sys.exit(1)

# Base URLs
BASE_URL = "https://api.company-information.service.gov.uk"
WINCHAM_POSTCODE = "CW12 4TR"

def fetch_companies_by_postcode(postcode, max_results=100):
    print(f"Searching for companies registered to postcode: {postcode}...")
    headers = {"Authorization": API_KEY}
    
    # We use Congleton, filtering specifically for companies registered at Adrem's Postcode
    params = {
        'q': 'property', 
        'location': 'CW12 4AA', 
        'items_per_page': 600
    }
    
    # Using Advanced Search API (requires authorization)
    # Advanced search allows searching by location (which matches registered office address)
    search_url = f"{BASE_URL}/advanced-search/companies?location={postcode.replace(' ', '+')}&size=50"
    
    companies = []
    start_index = 0
    
    while len(companies) < max_results:
        url = f"{search_url}&start_index={start_index}"
        response = requests.get(url, auth=(API_KEY, ''))
        
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            break
            
        data = response.json()
        items = data.get('items', [])
        
        if not items:
            break
            
        for item in items:
            companies.append({
                'company_name': item.get('company_name'),
                'company_number': item.get('company_number'),
                'company_status': item.get('company_status'),
                'date_of_creation': item.get('date_of_creation')
            })
            
        print(f"Loaded {len(companies)} companies...")
        start_index += 50
        time.sleep(0.6) # Respect rate limits (600 requests per 5 minutes)
        
    return companies[:max_results]

def fetch_company_officers(company_number):
    url = f"{BASE_URL}/company/{company_number}/officers"
    response = requests.get(url, auth=(API_KEY, ''))
    
    if response.status_code != 200:
        return []
        
    data = response.json()
    officers = []
    
    for item in data.get('items', []):
        # We want the directors (the property owners), not Wincham as secretary
        if item.get('officer_role') == 'director':
            address = item.get('address', {})
            officers.append({
                'name': item.get('name'),
                'role': item.get('officer_role'),
                'address': f"{address.get('address_line_1', '')}, {address.get('locality', '')}, {address.get('postal_code', '')}"
            })
            
    return officers

def main():
    print("Step 1: Fetching core Wincham companies...")
    companies = fetch_companies_by_postcode(WINCHAM_POSTCODE, max_results=600) # Fetch all 589 hits
    
    if not companies:
        print("No companies found or API key invalid.")
        return
        
    print(f"\nStep 2: Fetching residential addresses of Directors for {len(companies)} companies...")
    
    with open('adrem_leads.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company Name', 'Company Number', 'Status', 'Date of Creation', 'Director Name', 'Director Address (LEAD)'])
        
        for i, company in enumerate(companies):
            sys.stdout.write(f"\rProcessing {i+1}/{len(companies)}...")
            sys.stdout.flush()
            
            officers = fetch_company_officers(company['company_number'])
            
            for officer in officers:
                writer.writerow([
                    company['company_name'],
                    company['company_number'],
                    company['company_status'],
                    company['date_of_creation'],
                    officer['name'],
                    officer['address']
                ])
                
            time.sleep(0.6) # Rate limit
            
    print("\n\nSuccess! Your targeted lead list has been saved to 'wincham_leads.csv'")
    print("You now have names and mailing addresses for direct marketing.")

if __name__ == "__main__":
    main()
