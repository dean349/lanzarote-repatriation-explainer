import ssl
import json
import base64
import urllib.request
import os

api_key = '445f486c-a61d-49ec-be74-3e16e0fa8c83'
company_no = '06993349'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

class NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Remove the Authorization header when following redirects (AWS S3 rejects it)
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req and 'Authorization' in new_req.headers:
            del new_req.headers['Authorization']
        if new_req and 'authorization' in new_req.unredirected_hdrs:
            del new_req.unredirected_hdrs['authorization']
        return new_req

opener = urllib.request.build_opener(NoAuthRedirectHandler(), urllib.request.HTTPSHandler(context=ctx))
urllib.request.install_opener(opener)

def make_ch_request(url):
    req = urllib.request.Request(url)
    base64string = base64.b64encode(f"{api_key}:".encode('utf-8')).decode('utf-8')
    req.add_header('Authorization', f'Basic {base64string}')
    req.add_header('Accept', 'application/json')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching metadata {url}: {e}")
        return None

def download_pdf(document_id, filename):
    url = f"https://document-api.company-information.service.gov.uk/document/{document_id}/content"
    req = urllib.request.Request(url)
    base64string = base64.b64encode(f"{api_key}:".encode('utf-8')).decode('utf-8')
    req.add_header('Authorization', f'Basic {base64string}')
    req.add_header('Accept', 'application/pdf')
    print(f"Downloading {filename}...")
    try:
        with urllib.request.urlopen(req) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
        print(f"Success! Saved {filename}")
    except urllib.error.HTTPError as e:
        print(f"Error downloading {filename}: {e.code} {e.reason}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")


out_dir = r"c:\DAD\UK_Lanzarote_Repatriation\Files and Information for Phil Harrison"

print("Fetching filing history...")
history = make_ch_request(f'https://api.company-information.service.gov.uk/company/{company_no}/filing-history?items_per_page=100')

downloaded = 0
if history and 'items' in history:
    for item in history['items']:
        date = item.get('date', '')
        if date.startswith('2019'):
            desc = item.get('description', '')
            doc_meta = item.get('links', {}).get('document_metadata', '')
            
            if not doc_meta: continue
            doc_id = doc_meta.split('/')[-1]
            
            form_type = item.get('type', '')
            
            # Looking for the PSC statement
            if form_type in ['PSC01', 'PSC02'] or 'person-with-significant-control' in item.get('category',''):
                filepath = os.path.join(out_dir, "2019_Philip_Harrison_PSC_Ownership.pdf")
                print(f"Found 2019 PSC: {date} - {desc}")
                download_pdf(doc_id, filepath)
                downloaded += 1
                
            # Looking for the Confirmation statement
            elif form_type == 'CS01' and '2019' in date:
                filepath = os.path.join(out_dir, "2019_Los_Romeros_Confirmation_Statement_CS01.pdf")
                print(f"Found 2019 Confirmation Statement: {date} - {desc}")
                download_pdf(doc_id, filepath)
                downloaded += 1

print(f"Done. Downloaded {downloaded} documents.")
