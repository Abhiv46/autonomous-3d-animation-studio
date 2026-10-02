import json

transcript_path = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            obj = json.loads(line)
            if obj.get("source") == "USER_EXPLICIT":
                c = obj.get("content", "")
                if any(k in c.lower() for k in ["upload", "youtube", "tiktok", "browser", "post"]):
                    print(f"--- Step {obj.get('step_index')} ---")
                    print(c)
        except Exception:
            pass
