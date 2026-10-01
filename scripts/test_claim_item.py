import sys
import json
import os
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.worker_pool.parallel_engine import MultiAccountParallelEngine
from backend.db.database import DatabaseManager

with open('config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

engine = MultiAccountParallelEngine(config=config, max_concurrent=1)
acc = config['google_flow']['accounts'][0]
print(f"Testing worker item claim on slot {acc['slot_index']}: {acc['email']}")

item = engine.claim_next_work_item(acc['slot_index'])
if item:
    print(f"Successfully claimed item: {item['id']} - {item['title'][:40]} (Part {item['part_number']})")
    # Release it back to PENDING so runner can take it
    db = DatabaseManager()
    with db.get_connection() as conn:
        conn.execute("UPDATE story_parts SET status = 'PENDING', assigned_account_id = NULL WHERE id = ?", (item['id'],))
        conn.commit()
    print("Released item back to PENDING.")
else:
    print("No pending item claimed! Checking DB...")
    db = DatabaseManager()
    with db.get_connection() as conn:
        rows = conn.execute("SELECT id, status, assigned_account_id FROM story_parts LIMIT 5").fetchall()
        for r in rows:
            print(dict(r))
