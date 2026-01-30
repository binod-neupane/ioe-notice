import json
from pathlib import Path
from typing import List, Dict, Set
class StateManager:
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.seen_urls: Set[str] = set()
        self._load()
    def _load(self) -> None:
        if not self.state_file.exists():
            self.seen_urls = set()
            return
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                urls = data.get('seen_urls', [])
                self.seen_urls = {u.strip() for u in urls if isinstance(u, str)}
        except Exception:
            self.seen_urls = set()
    def save(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({'seen_urls': sorted(self.seen_urls)}, f, indent=2, ensure_ascii=False)
    def filter_new(self, notices: List[Dict]) -> List[Dict]:
        new_items = []
        for notice in notices:
            url = notice.get('url')
            if not isinstance(url, str):
                continue
            url = url.strip()
            if url in self.seen_urls:
                continue
            new_items.append(notice)
        return new_items
    def mark_seen(self, notices: List[Dict]) -> None:
        for notice in notices:
            url = notice.get('url')
            if isinstance(url, str):
                self.seen_urls.add(url.strip())