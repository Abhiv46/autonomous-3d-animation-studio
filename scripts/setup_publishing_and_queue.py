import sys
import sqlite3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

conn = sqlite3.connect("data/content_engine.db")
c = conn.cursor()

# Set fresh unreleased episodes ep_18 to ep_27 as QUEUED
fresh_ids = [
    'ep_18_magic_freeze_remote', 'ep_19_giant_soap_bubble', 'ep_20_pillow_fort_castle',
    'ep_21_kaavya_doctor_injection', 'ep_22_chhota_chef_pancake', 'ep_23_water_pichkari_ambush',
    'ep_24_tricycle_grand_prix', 'ep_25_toy_robot_dinosaur', 'ep_26_chocolate_treasure_hunt',
    'ep_27_mummy_saree_superhero'
]

placeholders = ",".join("?" for _ in fresh_ids)
c.execute(f"UPDATE stories SET state = 'QUEUED', priority = 1 WHERE id IN ({placeholders})", fresh_ids)
c.execute(f"UPDATE story_parts SET status = 'PENDING', assigned_account_id = NULL WHERE story_id IN ({placeholders})", fresh_ids)
conn.commit()

queued = c.execute(f"SELECT id, title FROM stories WHERE id IN ({placeholders})", fresh_ids).fetchall()
print(f"[OK] Reset {len(queued)} fresh episodes to QUEUED status.")

for r in queued:
    c.execute("""
        INSERT OR REPLACE INTO publishing_jobs (id, story_id, platform, target_channel_id, status, title, compliance_classification)
        VALUES (?, ?, 'YOUTUBE', 'UCULzzCCm0Y-ZHiYF480ioLg', 'PENDING', ?, 'MADE_FOR_KIDS')
    """, (f"pub_yt_{r[0]}", r[0], r[1]))
    c.execute("""
        INSERT OR REPLACE INTO publishing_jobs (id, story_id, platform, target_channel_id, status, title, compliance_classification)
        VALUES (?, ?, 'TIKTOK', '@TheNaughtyDuoOfficial', 'PENDING', ?, 'FAMILY_COMEDY_60S')
    """, (f"pub_tt_{r[0]}", r[0], r[1]))

conn.commit()
pub_count = c.execute("SELECT COUNT(*) FROM publishing_jobs").fetchone()[0]
print(f"[✓] Successfully populated {pub_count} platform publishing jobs (YouTube & TikTok)!")
