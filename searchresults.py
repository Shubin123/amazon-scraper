from selectorlib import Extractor
import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

ENABLE_GSHEETS = True  # Set this to False to disable Google Sheets writing

# Google Sheets setup
def init_gsheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('clientsecret.json', scope) #stored apikey
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def scrape(url, extractor):  


    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.ca/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading %s"%url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create 
    return extractor.extract(r.text)

# Sample run call, replace 'num' with your desired number

def run():
    # Create an Extractor by reading from the YAML file
    e = Extractor.from_yaml_file('search_results.yml')
    
    product_data = []
    gsheet = None

    if ENABLE_GSHEETS:
        gsheet = init_gsheet('sales-list')  # Replace with your Google Sheet name

    with open("search_results_urls.txt", 'r') as urllist, open('search_results_output.jsonl', 'w') as outfile:
        for url in urllist.read().splitlines():
            data = scrape(url, e)
            if data:
                for product in data['products']:
                    product['search_url'] = url
                    print("Saving Product: %s" % product['title'])
                    product_data.append(product)

                    # Write to JSONL file
                    json.dump(product, outfile)
                    outfile.write("\n")

                    # Write to Google Sheets
                    if ENABLE_GSHEETS and gsheet:
                        gsheet.append_row(list(product.values()))
# run()
                        
run()