import os
import re
import time
import requests
import urllib3
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
REQUEST_TIMEOUT = 30
POLITE_DELAY = 1
PDF_DIR = 'data/pdf'
IMAGE_DIR = 'data/image'
def download_attachment(notice):
    notice_url = notice.get('url')
    if not notice_url:
        return None
    try:
        resp = requests.get(notice_url, timeout=REQUEST_TIMEOUT, verify=False)
        resp.raise_for_status()
    except Exception:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    pdf_link = _find_pdf_link(soup)
    if pdf_link:
        os.makedirs(PDF_DIR, exist_ok=True)
        filename = _safe_filename(notice.get('title', 'notice')) + '.pdf'
        dest_path = os.path.join(PDF_DIR, filename)
        if _download_pdf(pdf_link, dest_path):
            time.sleep(POLITE_DELAY)
            return {'type': 'pdf', 'path': dest_path, 'source_url': pdf_link}
    image_link = _find_image_link(soup)
    if image_link:
        os.makedirs(IMAGE_DIR, exist_ok=True)
        ext = os.path.splitext(urlparse(image_link).path)[1] or '.jpg'
        filename = _safe_filename(notice.get('title', 'notice')) + ext
        dest_path = os.path.join(IMAGE_DIR, filename)
        if _download_binary(image_link, dest_path):
            time.sleep(POLITE_DELAY)
            return {'type': 'image', 'path': dest_path, 'source_url': image_link}
    return None
def _download_pdf(url, dest_path):
    if 'drive.google.com' in url:
        return _download_google_drive_pdf(url, dest_path)
    return _download_binary(url, dest_path)
def _download_google_drive_pdf(url, dest_path):
    file_id = _extract_drive_file_id(url)
    if not file_id:
        return False
    session = requests.Session()
    base_url = 'https://drive.google.com/uc?export=download'
    params = {'id': file_id}
    try:
        response = session.get(base_url, params=params, stream=True, timeout=REQUEST_TIMEOUT, verify=False)
    except Exception:
        return False
    confirm_token = _get_drive_confirm_token(response.cookies)
    if confirm_token:
        params['confirm'] = confirm_token
        try:
            response = session.get(base_url, params=params, stream=True, timeout=REQUEST_TIMEOUT, verify=False)
        except Exception:
            return False
    return _save_stream_to_file(response, dest_path)
def _extract_drive_file_id(url):
    parsed = urlparse(url)
    if '/file/d/' in parsed.path:
        parts = parsed.path.split('/file/d/')
        if len(parts) > 1:
            return parts[1].split('/')[0]
    qs = parse_qs(parsed.query)
    if 'id' in qs:
        return qs['id'][0]
    return None
def _get_drive_confirm_token(cookies):
    for key, value in cookies.items():
        if key.startswith('download_warning'):
            return value
    return None
def _find_image_link(soup):
    ck = soup.select_one('div.ck-table')
    if not ck:
        return None
    for img in ck.find_all('img'):
        src = img.get('src', '').strip()
        if not src:
            continue
        if src.startswith('data:'):
            continue
        if img.parent and img.parent.name == 'a':
            continue
        if src.startswith('https://portal.tu.edu.np/medias/'):
            return src
    return None
def _find_pdf_link(soup):
    ck = soup.select_one('div.ck-table')
    if not ck:
        return None
    for a in ck.find_all('a', href=True):
        href = a['href'].strip()
        if not href:
            continue
        href_lower = href.lower()
        if href_lower.endswith('.pdf'):
            return href
        if 'drive.google.com' in href_lower:
            return href
        if '/downloads/' in href_lower:
            return href
    return None
def _download_binary(url, dest_path):
    try:
        response = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT, verify=False)
        response.raise_for_status()
        return _save_stream_to_file(response, dest_path)
    except Exception:
        return False
def _save_stream_to_file(response, dest_path):
    try:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception:
        return False
def _safe_filename(text):
    text = text.strip()
    text = re.sub('[\\\\/?:*\\"<>|]', '_', text)
    text = re.sub('\\s+', ' ', text)
    return text[:150]