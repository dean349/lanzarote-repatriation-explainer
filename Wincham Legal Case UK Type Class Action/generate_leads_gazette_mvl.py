import requests
from bs4 import BeautifulSoup
import csv
import time
import sys

print("\n--- Wincham Lead Generator: The London Gazette (MVLs) ---")
print("Targeting companies in Members' Voluntary Liquidation (Wincham Exit Pipeline)\n")

# Gazette search URL for Corporate Insolvency -> Members Voluntary Liquidation
# Searching for text "Wincham" or postcode "CW12 4TR"
SEARCH_URL = "https://www.thegazette.co.uk/insolvency/notice?text=Wincham+OR+CW12+4TR&categorycode=G405000000+G405010000+G405020000+G405030000&location-distance-1=1&numberOfLocationSearches=1&results-page-size=50"

def fetch_gazette_notices():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Fetching active insolvency notices...")
    try:
        response = requests.get(SEARCH_URL, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch Gazette: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    notices = []
    
    # Gazette search results list
    feed = soup.find_all('div', class_='feed-item')
    
    for item in feed:
        title_elem = item.find('h3', class_='title')
        if not title_elem:
            continue
            
        company_name = title_elem.get_text(strip=True)
        notice_date = item.find('time').get_text(strip=True) if item.find('time') else "Unknown"
        link = "https://www.thegazette.co.uk" + title_elem.find('a')['href'] if title_elem.find('a') else ""
        
        # Extract snippet details
        snippet = item.find('div', class_='content')
        snippet_text = snippet.get_text(strip=True) if snippet else ""
        
        notices.append({
            'Company Name': company_name,
            'Date Published': notice_date,
            'Snippet': snippet_text,
            'Link': link
        })
        
    return notices

def main():
    try:
        import bs4
    except ImportError:
        print("ERROR: Missing 'beautifulsoup4' library.")
        print("Please run: pip install beautifulsoup4 requests")
        sys.exit(1)
        
    leads = fetch_gazette_notices()
    
    if not leads:
        print("No MVL leads found today or rate-limited.")
        return
        
    print(f"Found {len(leads)} companies currently unwinding via MVL (High Intent!).")
    
    with open('gazette_mvl_leads.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Company Name', 'Date Published', 'Snippet', 'Link'])
        writer.writeheader()
        writer.writerows(leads)
        
    print("Saved 'gazette_mvl_leads.csv' with direct links to the liquidation notices.")
    print("These are people actively paying to escape the Wincham scheme.")
    
if __name__ == "__main__":
    main()
