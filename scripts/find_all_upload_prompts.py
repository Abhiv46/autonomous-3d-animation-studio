import os
import json

convs = [
    '2ebe07f2-7a70-428f-ab41-dc22d7b904d2',
    'b4d81050-dfde-4524-a716-544f534d0b40',
    '6d8e842c-e3cd-412c-b189-0e40ce6ac7f9',
    '759570ea-a8ec-459d-9096-0e4d4eb178d4'
]

for conv in convs:
    path = f"C:/Users/user/.gemini/antigravity/brain/{conv}/.system_generated/logs/transcript.jsonl"
    if not os.path.exists(path):
        continue
    print(f"=== Conversation: {conv} ===")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("source") == "USER_EXPLICIT":
                    c = obj.get("content", "")
                    if any(w in c.lower() for w in ["upload", "youtube", "post", "link", "browser", "shorts"]):
                        print(f"  [{obj.get('step_index')}] {c.strip()[:140]}")
            except Exception:
                pass
