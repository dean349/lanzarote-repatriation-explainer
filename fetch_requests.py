import os
import json
import requests

api_key = '445f486c-a61d-49ec-be74-3e16e0fa8c83'
company_no = '06993349'
out_dir = r"c:\DAD\UK_Lanzarote_Repatriation\Files and Information for Phil Harrison"

session = requests.Session()
session.auth = (api_key, '')

history_url = f'https://api.company-information.service.gov.uk/company/{company_no}/filing-history?items_per_page=100'

try:
    print("Fetching filing history...")
    history = session.get(history_url).json()

    for item in history.get('items', []):
        date = item.get('date', '')
        if date.startswith('2019'):
            desc = item.get('description', '')
            doc_meta = item.get('links', {}).get('document_metadata', '')
            if not doc_meta: continue
            
            form_type = item.get('type', '')
            filename = None
            
            # Looking for the PSC statement
            if form_type in ['PSC01', 'PSC02'] or 'person-with-significant-control' in item.get('category',''):
                filename = "2019_Philip_Harrison_PSC_Ownership.pdf"
                
            # Looking for the Confirmation statement
            elif form_type == 'CS01' and '2019' in date:
                filename = "2019_Los_Romeros_Confirmation_Statement_CS01.pdf"
                
            if filename:
                doc_id = doc_meta.split('/')[-1]
                download_url = f"https://document-api.company-information.service.gov.uk/document/{doc_id}/content"
                print(f"Resolving redirect for {filename}...")
                
                # Turn off automatic redirects to grab the actual AWS S3 URL
                headers = {'Accept': 'application/pdf'}
                r = session.get(download_url, headers=headers, allow_redirects=False)
                
                if r.status_code in (301, 302, 303, 307, 308):
                    s3_url = r.headers['Location']
                    print(f"Downloading from S3...")
                    # Fetch from S3 without the Basic Auth header
                    pdf_r = requests.get(s3_url)
                    
                    filepath = os.path.join(out_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(pdf_r.content)
                    print(f"SUCCESS: Saved {filename}")
                else:
                    print(f"Failed to get redirect: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")

print("Done.")
