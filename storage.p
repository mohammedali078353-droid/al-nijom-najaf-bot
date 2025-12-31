import json
import os
from datetime import datetime

DATA_FILE = "scheduled_posts.json"

def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, default=str)

def load_posts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for p in data:
            p["post_time"] = datetime.fromisoformat(p["post_time"])
        return data