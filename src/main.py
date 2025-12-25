from functions import fetch_urls_from_sitemap, assess_availability, assess_security, assess_performance, assess_accessibility, assess_urls, get_tables
import os
DOMAIN = "./domains.txt"
DATA_DIR = "data"
import pandas as pd
def load_url_from_domain(domain):
    urls = fetch_urls_from_sitemap(domain)
    return urls


def main():
    
    # domains = []
    # with open(DOMAIN, "r") as f:
    #     domains = [line.strip() for line in f.readlines() if line.strip()]

    # for domain in domains:
    #     try:
    #         urls = fetch_urls_from_sitemap(domain)
    #     except:
    #         continue
    #     urls_path = f"{DATA_DIR}/txt/{domain}_urls.txt"
    #     with open(urls_path, "w") as f:
    #         for url in urls:
    #             f.write(f"{url}\n")
    
    # all_url_files = os.listdir(f"{DATA_DIR}/txt/")
    # for file_name in all_url_files:
    #     if not file_name.endswith("_urls.txt"):
    #         continue
    #     domain = file_name.replace("_urls.txt", "")
    #     urls_path = f"{DATA_DIR}/txt/{domain}_urls.txt"
    #     # if not os.path.exists(urls_path):
    #     #     continue
    #     with open(urls_path, "r") as f:
    #         urls = [line.strip() for line in f.readlines() if line.strip()]
    #     all_urls = urls
    #     if len(all_urls) == 0:
    #         continue
    #     assessments = assess_urls(all_urls)
    #     assessments_path = f"{DATA_DIR}/json/assessments/{domain}.json"
    #     with open(assessments_path, "w") as f:
    #         import json
    #         json.dump(assessments, f, indent=4)

    json_files = os.listdir(f"{DATA_DIR}/json/assessments/")
    for file_name in json_files:
        domain = file_name.replace(".json", "").replace(".gov.in", "")
        with open(f"{DATA_DIR}/json/assessments/{file_name}", "r") as f:
            import json
            assessments = json.load(f)

        tables = get_tables(assessments)
        
        # for asmt_criteria, table in tables.items():
        #     table.to_csv(f"{DATA_DIR}/csv/{asmt_criteria}/{domain}.csv")
        with pd.ExcelWriter(f"{DATA_DIR}/excel/{domain}.xlsx", engine='xlsxwriter') as writer:
            for asmt_criteria, table in tables.items():
                table.to_excel(writer, sheet_name=asmt_criteria)  # Sheet names max length is 31

if __name__ == "__main__":
    main()