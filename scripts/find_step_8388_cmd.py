import sys
import json

sys.stdout.reconfigure(encoding="utf-8")
path = "C:/Users/user/.gemini/antigravity/brain/2ebe07f2-7a70-428f-ab41-dc22d7b904d2/.system_generated/logs/transcript.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        idx = obj.get("step_index", 0)
        if 8365 <= idx <= 8387:
            if obj.get("tool_calls"):
                for tc in obj.get("tool_calls"):
                    print(f"[{idx}] {tc.get('name')}: {tc.get('args')}")
