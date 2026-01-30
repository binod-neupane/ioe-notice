from datetime import datetime
from typing import Optional, Dict
def normalize_date(raw_date: str) -> Dict[str, Optional[str]]:
    raw = (raw_date or '').strip()
    if not raw:
        return {'raw': raw, 'iso': None}
    known_formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d', '%b %d, %Y', '%B %d, %Y']
    for fmt in known_formats:
        try:
            parsed = datetime.strptime(raw, fmt)
            return {'raw': raw, 'iso': parsed.date().isoformat()}
        except ValueError:
            continue
    return {'raw': raw, 'iso': None}