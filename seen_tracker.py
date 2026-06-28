import json
import os
import hashlib
from datetime import datetime, timedelta

SEEN_FILE = "seen_articles.json"


def _load() -> dict:
    if not os.path.exists(SEEN_FILE):
        return {}
    try:
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def has_seen(url: str) -> bool:
    return _hash(url) in _load()


def mark_seen(url: str):
    data = _load()
    data[_hash(url)] = datetime.utcnow().isoformat()
    cutoff = (datetime.utcnow() - timedelta(hours=48)).isoformat()
    data = {k: v for k, v in data.items() if v > cutoff}
    _save(data)
