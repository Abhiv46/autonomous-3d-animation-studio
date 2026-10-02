import json

path = r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for v in data.get("uploaded", []):
    if v.get("key") == "burn_u7_chanda_mama":
        v["youtube_status"] = "PRIVATED (Duplicate of Garden Swing)"
    elif v.get("key") == "ep_18_magic_freeze_remote":
        v["youtube_status"] = "PRIVATED (Old Clip Mismatch - Regenerating Real Veo 9:16)"

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("[✓] uploaded_videos_log.json updated with privated statuses!")
