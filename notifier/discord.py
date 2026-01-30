import os
import json
import requests
from typing import List, Dict
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
REQUEST_TIMEOUT = 30
def send_notifications(webhook_url: str, notices: List[Dict], role_id: str=None) -> None:
    if not webhook_url or not notices:
        return
    notices_with_files = []
    text_only_notices = []
    for notice in notices:
        if notice.get('attachment'):
            notices_with_files.append(notice)
        else:
            text_only_notices.append(notice)
    for notice in notices_with_files:
        _send_notice_with_attachment(webhook_url, notice, role_id)
    if text_only_notices:
        _send_text_batch(webhook_url, text_only_notices, role_id)
def _send_notice_with_attachment(webhook_url: str, notice: Dict, role_id: str=None) -> None:
    attachment = notice.get('attachment')
    if not attachment:
        return
    file_path = attachment.get('path')
    if not file_path or not os.path.exists(file_path):
        return
    lines = []
    if role_id:
        lines.append(f'<@&{role_id}>')
    lines.append(f"**{notice.get('title', 'New Notice')}**")
    raw_date = notice.get('date', {}).get('raw')
    if raw_date:
        lines.append(f'📅 {raw_date}')
    if attachment.get('source_url'):
        lines.append(f"🔗 [Click here]({attachment['source_url']})")
    content = '\n'.join(lines)
    payload = {'content': content, 'allowed_mentions': {'roles': [str(role_id)] if role_id else []}}
    opened_file = open(file_path, 'rb')
    files = {'file': (os.path.basename(file_path), opened_file)}
    try:
        requests.post(webhook_url, data={'payload_json': json.dumps(payload)}, files=files, timeout=REQUEST_TIMEOUT, verify=False)
    except Exception as e:
        print(f'[discord] Failed to send notice with attachment: {e}')
    finally:
        opened_file.close()
def _send_text_batch(webhook_url: str, notices: List[Dict], role_id: str=None) -> None:
    if not notices:
        return
    lines = []
    if role_id:
        lines.append(f'<@&{role_id}>')
    lines.append('**🆕 New IOE Exam Notices**\n')
    for notice in notices:
        title = notice.get('title', 'New Notice')
        raw_date = notice.get('date', {}).get('raw', 'Unknown date')
        url = notice.get('url', '')
        lines.append(f'• **{title}**\n  📅 {raw_date}\n  🔗 {url}\n')
    content = '\n'.join(lines)
    payload = {'content': content, 'allowed_mentions': {'roles': [str(role_id)] if role_id else []}}
    try:
        requests.post(webhook_url, json=payload, timeout=REQUEST_TIMEOUT, verify=False)
    except Exception as e:
        print(f'[discord] Failed to send text batch: {e}')