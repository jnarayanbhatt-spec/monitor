from functions_requests import fetch_urls_from_sitemap, assess_security, get_tables
from functions_selenium import get_webdriver, assess_availability, assess_performance, assess_accessibility
import os
import pandas as pd
from typing import Union
from tqdm import tqdm
from urllib.parse import urlparse
# import json

DOMAIN = "./domains.txt"
DATA_DIR = "data"


def read_json_file(file_path: str) -> Union[dict, None]:
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        import json
        return json.loads(f.read())
    
def write_json_file(file_path: str, data: dict):
    with open(file_path, "w") as f:
        import json
        json.dump(data, f, indent=4)
        
def assess_urls(urls):
    
    results = {}
    for url in tqdm(urls, desc=f"Assessing URL from domain {urlparse(urls[0]).hostname}"):
        results[url] = {
            'availability': assess_availability(url),
            # 'security': assess_security(url),
            # 'performance': assess_performance(url),
            'accessibility': assess_accessibility(url)
        }
    return results



def load_url_from_domain(domain):
    urls = fetch_urls_from_sitemap(domain)
    return urls


def main():
    
    def update_assessments(existing, new):
        for url, data in new.items():
            if url not in existing:
                existing[url] = data
            else:
                existing[url].update(data)
        return existing
    
    domains = []
    with open(DOMAIN, "r") as f:
        domains = [line.strip() for line in f.readlines() if line.strip()]

    for domain in domains:
        try:
            urls = fetch_urls_from_sitemap(domain)
        except:
            continue
        urls_path = f"{DATA_DIR}/txt/{domain}_urls.txt"
        with open(urls_path, "w") as f:
            for url in urls:
                f.write(f"{url}\n")
    
    all_url_files = os.listdir(f"{DATA_DIR}/txt/")
    for file_name in all_url_files:
        if not file_name.endswith("_urls.txt"):
            continue
        domain = file_name.replace("_urls.txt", "")
        urls_path = f"{DATA_DIR}/txt/{domain}_urls.txt"
        # if not os.path.exists(urls_path):
        #     continue
        with open(urls_path, "r") as f:
            urls = [line.strip() for line in f.readlines() if line.strip()]
        all_urls = urls
        if len(all_urls) == 0:
            continue
        assessments_path = f"{DATA_DIR}/json/assessments/{domain}.json"
        existing_assessments = read_json_file(assessments_path) or {}
        assessments = assess_urls(all_urls)        
        update_assessments(existing_assessments, assessments)
        write_json_file(assessments_path, existing_assessments)

    json_files = os.listdir(f"{DATA_DIR}/json/assessments/")
    for file_name in json_files:
        domain = file_name.replace(".json", "").replace(".gov.in", "")
        json_path = f"{DATA_DIR}/json/assessments/{file_name}"
        assessments = read_json_file(json_path)

        tables = get_tables(assessments)
        
        for asmt_criteria, table in tables.items():
            table.to_csv(f"{DATA_DIR}/csv/{asmt_criteria}/{domain}.csv")
        with pd.ExcelWriter(f"{DATA_DIR}/excel/{domain}.xlsx", engine='xlsxwriter') as writer:
            for asmt_criteria, table in tables.items():
                table.to_excel(writer, sheet_name=asmt_criteria)  # Sheet names max length is 31

if __name__ == "__main__":
    main()