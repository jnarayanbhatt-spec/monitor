from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from collections import deque
import pandas as pd
def fetch_urls_from_sitemap(domain):
    sitemap_url = f"https://{domain}/sitemap.xml"
    urls = set()

    resp = requests.get(sitemap_url, timeout=10)
    if resp.status_code != 200:
        return urls

    soup = BeautifulSoup(resp.text, "xml")
    for loc in soup.find_all("loc"):
        urls.add(loc.text.strip())

    return urls


import requests
import ssl
import socket
import time
from urllib.parse import urlparse
import datetime
from tqdm import tqdm
    

def assess_availability(url, allow_redirect_as_success=True):
    try:
        start_time = time.time()
        resp = requests.get(url, timeout=10, allow_redirects=False)
        response_time = time.time() - start_time
        return {
            'status_code': resp.status_code,
            'response_time': response_time,
            'is_available': resp.status_code in [200, 301, 302] if allow_redirect_as_success else resp.status_code == 200
        }
    except requests.RequestException as e:
        return {
            'status_code': None,
            'response_time': None,
            'is_available': False,
            'error': str(e)
        }

def assess_security(url):
    parsed = urlparse(url)
    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    # Check SSL/TLS
    ssl_info = {}
    if parsed.scheme == 'https':
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    ssl_info = {
                        'has_ssl': True,
                        'cert_expires': cert['notAfter'],
                        'issuer': cert['issuer'][0][0][1] if cert['issuer'] else None,
                        'days_until_expiry': (datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z') - datetime.datetime.now()).days,
                        'current_date': datetime.datetime.now().isoformat()
                    }
        except Exception as e:
            ssl_info = {'has_ssl': False, 'error': str(e)}
    else:
        ssl_info = {'has_ssl': False}
    
    try:
        resp = requests.get(url, timeout=10)
        headers = resp.headers
        security_headers = {
            'content_security_policy': 'Content-Security-Policy' in headers,
            'x_frame_options': 'X-Frame-Options' in headers,
            'strict_transport_security': 'Strict-Transport-Security' in headers
        }
    except:
        security_headers = {}
    
    return {
        'ssl_info': ssl_info,
        'security_headers': security_headers
    }

def assess_performance(url):
    try:
        start_time = time.time()
        resp = requests.get(url, timeout=10)
        total_time = time.time() - start_time
        page_size = len(resp.content)
        return {
            'total_load_time': total_time,
            'page_size_bytes': page_size,
            'status_code': resp.status_code
        }
    except requests.RequestException as e:
        return {'error': str(e)}

def assess_accessibility(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        has_alt = any(img.get('alt') for img in soup.find_all('img'))
        has_headings = bool(soup.find_all(['h1', 'h2', 'h3']))
        return {
            'has_alt_text': has_alt,
            'has_headings': has_headings,
        }
    except Exception as e:
        return {'error': str(e)}


def assess_urls(urls):
    results = {}
    for url in tqdm(urls, desc=f"Assessing URL from domain {urlparse(urls[0]).hostname}"):
        results[url] = {
            'availability': assess_availability(url),
            'security': assess_security(url),
            'performance': assess_performance(url),
            'accessibility': assess_accessibility(url)
        }
    return results

def get_tables(data):
    tables = {}
    key_fields = list(data.values())[0].keys()
    for key in tqdm(key_fields):  # Get the first subdictionary's keys
        # Create a DataFrame for each key
        if key is None:
            break
        tables[key] = pd.DataFrame.from_dict(
            {url: data[url][key] for url in tqdm(data)},
            orient='index'
        )
        if 'security' in key:
            ssl_df = tables[key]
            ssl_df_expanded = pd.DataFrame()
            for col in ssl_df.columns:
                col_data = ssl_df[col].apply(lambda x:pd.Series(x) if isinstance(x, dict) else pd.Series())
                col_data.index = ssl_df.index
                ssl_df_expanded = pd.concat([ssl_df_expanded, col_data], axis=1)
            tables[key] = ssl_df_expanded
    return tables
