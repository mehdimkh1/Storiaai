import json
import os
import sys
from fastapi.testclient import TestClient

# Ensure backend/app package is importable
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Reset local SQLite DB for a clean smoke run (safe for local only)
db_path = os.path.join(PROJECT_ROOT, "storiaai.db")
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("Reset local DB:", db_path)
    except Exception as e:
        print("Warning: could not reset local DB:", e)

from app.main import app
from app.database import init_db

# Ensure tables exist for the smoke test
init_db()

client = TestClient(app)

# Healthcheck
res = client.get("/health")
print("HEALTH:", res.status_code, res.json())

# Generate story payload
payload = {
    "parent_email": "parent@example.com",
    "child": {
        "name": "Luca",
        "age": 6,
        "mood": "curioso",
        "interests": ["draghi", "calcio"],
    },
    "controls": {
        "no_scary": True,
        "kindness_lesson": True,
        "italian_focus": True,
        "educational": False,
    },
    "language": "it",
    "target_duration_minutes": 7,
    "sequel": False,
    "voice": None,
    "style": "fiaba classica",
    "tone": "calmo",
    "educational_topic": "stelle",
    "generate_panels": True,
}

res2 = client.post("/generate_story", json=payload)
print("GENERATE:", res2.status_code)
data = res2.json()
print("keys:", list(data.keys()))
print("story keys:", list(data.get("story", {}).keys()))
print("panel_prompts count:", len(data.get("story", {}).get("panel_prompts", [])))
print("memory_snapshot:", data.get("memory_snapshot"))
print(json.dumps(data, ensure_ascii=False)[:600])
