from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.settings import BASE_NOTICES_URL
def parse_notices(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    container = soup.select_one('section.notices-pg div.notices-warpper')
    if not container:
        return results
    posts = container.select('div.recent-post-wrapper')
    for post in posts:
        title_tag = post.select_one('a > h5')
        link_tag = post.select_one('a[href]')
        date_tag = post.select_one('span.nep_date')
        if not title_tag or not link_tag:
            continue
        title = title_tag.get_text(strip=True)
        url = urljoin(BASE_NOTICES_URL, link_tag.get('href', '').strip())
        raw_date = date_tag.get_text(strip=True) if date_tag else ''
        results.append({'title': title, 'url': url, 'raw_date': raw_date})
    return results
def extract_next_page_url(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, 'html.parser')
    next_link = soup.select_one('a[rel="next"]')
    if not next_link:
        return None
    href = next_link.get('href')
    if not href:
        return None
    return urljoin(BASE_NOTICES_URL, href)