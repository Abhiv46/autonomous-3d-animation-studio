import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from backend.db.database import DatabaseManager

db = DatabaseManager()
with db.get_connection() as conn:
    conn.execute("UPDATE accounts SET available_credits = 0, status = 'COOLDOWN' WHERE slot_index = 3")
    conn.commit()
    print("Updated Slot 3 to COOLDOWN (0 credits)")
    rows = conn.execute("SELECT slot_index, email, tier, available_credits, status, project_id FROM accounts WHERE available_credits > 0 ORDER BY available_credits DESC").fetchall()
    print("Available slots:")
    for r in rows:
        print(dict(r))
