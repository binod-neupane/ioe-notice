from pathlib import Path
import os
from datetime import datetime, time
from zoneinfo import ZoneInfo
from core.fetcher import fetch_all_pages
from core.parser import parse_notices, extract_next_page_url
from core.normalizer import normalize_date
from core.state import StateManager
from core.attachments import download_attachment
from notifier.discord import send_notifications
from config.settings import BASE_NOTICES_URL, STATE_FILE, MAX_PAGES
NEPAL_TZ = ZoneInfo('Asia/Kathmandu')
ALLOWED_START = time(9, 0)
ALLOWED_END = time(19, 0)
def within_allowed_time() -> bool:
    now = datetime.now(NEPAL_TZ).time()
    return ALLOWED_START <= now <= ALLOWED_END
def main():
    if os.getenv('ENABLE_TIME_GUARD') == '1':
        if not within_allowed_time():
            print('Outside allowed Nepal time window. Exiting safely.')
            return
    state = StateManager(Path(STATE_FILE))
    all_new_notices = []
    pages_processed = 0
    next_url = BASE_NOTICES_URL
    for html, page_url in fetch_all_pages(start_url=next_url):
        notices = parse_notices(html)
        for notice in notices:
            notice['date'] = normalize_date(notice.get('raw_date', ''))
        new_notices = state.filter_new(notices)
        if new_notices:
            for notice in new_notices:
                attachment = download_attachment(notice)
                if attachment:
                    notice['attachment'] = attachment
            all_new_notices.extend(new_notices)
        else:
            break
        pages_processed += 1
        if pages_processed >= MAX_PAGES:
            break
        next_url = extract_next_page_url(html)
        if not next_url:
            break
    if not all_new_notices:
        return
    webhook = os.getenv('DISCORD_WEBHOOK_URL', '')
    role_id = os.getenv('ROLE_ID')
    send_notifications(webhook, all_new_notices, role_id=role_id)
    state.mark_seen(all_new_notices)
    state.save()
if __name__ == '__main__':
    main()