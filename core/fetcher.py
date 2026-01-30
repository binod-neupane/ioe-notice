import time
import warnings
from typing import Generator, Tuple, Optional
import requests
from urllib3.exceptions import InsecureRequestWarning
from config.settings import BASE_NOTICES_URL, REQUEST_TIMEOUT, REQUEST_DELAY_SECONDS, MAX_PAGES
warnings.simplefilter('ignore', InsecureRequestWarning)
def fetch_page(url: str) -> Optional[str]:
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False, headers={'User-Agent': 'exam-notice-bot/1.0 (+https://github.com/PadhVaiiPadh/exam-bot)'})
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        print(f'[fetcher] Failed to fetch {url}: {exc}')
        return None
def fetch_all_pages(start_url: str=BASE_NOTICES_URL) -> Generator[Tuple[str, str], None, None]:
    current_url = start_url
    page_count = 0
    while current_url and page_count < MAX_PAGES:
        html = fetch_page(current_url)
        if html is None:
            break
        yield (html, current_url)
        page_count += 1
        time.sleep(REQUEST_DELAY_SECONDS)
        current_url = None