from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def assess_availability(url, driver, timeout=30):
    try:
        start_time = time.time()
        driver.get(url)
        
        # Wait for the page to load (wait for body element)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        response_time = time.time() - start_time
        
        # Check if page loaded successfully
        page_title = driver.title
        current_url = driver.current_url
        
        # Basic checks: title exists, no error pages
        is_available = bool(page_title) and "error" not in page_title.lower() and "404" not in page_title.lower()
        
        return {
            'status_code': 200 if is_available else None,  # Selenium doesn't give HTTP status directly
            'response_time': response_time,
            'is_available': is_available,
            'final_url': current_url,
            'page_title': page_title
        }
    except Exception as e:
        return {
            'status_code': None,
            'response_time': None,
            'is_available': False,
            'error': str(e)
        }

def assess_security(url, driver, timeout=30):
    # Selenium cannot directly check SSL certificates or response headers.
    # Omitting SSL info and security headers for now.
    # If needed, install selenium-wire for header inspection.
    parsed = urlparse(url)
    ssl_info = {'has_ssl': parsed.scheme == 'https'}  # Basic check
    security_headers = {}  # Cannot check with standard Selenium
    
    return {
        'ssl_info': ssl_info,
        'security_headers': security_headers
    }

def assess_performance(url, driver, timeout=30):
    try:
        start_time = time.time()
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        total_time = time.time() - start_time
        page_size = len(driver.page_source.encode('utf-8'))  # Approximate page size
        
        return {
            'total_load_time': total_time,
            'page_size_bytes': page_size,
            'status_code': 200  # Assume success if loaded
        }
    except Exception as e:
        return {'error': str(e)}

def assess_accessibility(url, driver, timeout=30):
    try:
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        has_alt = any(img.get('alt') for img in soup.find_all('img'))
        has_headings = bool(soup.find_all(['h1', 'h2', 'h3']))
        return {
            'has_alt_text': has_alt,
            'has_headings': has_headings,
        }
    except Exception as e:
        return {'error': str(e)}

def assess_urls(urls, driver):
    results = {}
    for url in tqdm(urls):
        results[url] = {}
        results[url]['availability'] = assess_availability(url, driver)
        results[url]['security'] = assess_security(url, driver)
        results[url]['performance'] = assess_performance(url, driver)
        results[url]['accessibility'] = assess_accessibility(url, driver)
    return results

# Then, when calling assess_urls, pass the driver:
# results = assess_urls(all_urls, driver)