import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

path = "C:/Users/user/.gemini/antigravity/brain/6d8e842c-e3cd-412c-b189-0e40ce6ac7f9/.system_generated/logs/transcript.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        idx = obj.get("step_index", 0)
        if 335 <= idx <= 450:
            if obj.get("source") in ["USER_EXPLICIT", "MODEL"]:
                t = obj.get("type")
                if t in ["USER_INPUT", "PLANNER_RESPONSE"]:
                    print(f"[{idx}] {obj.get('source')}: {str(obj.get('content'))[:160]}")
                    if obj.get("tool_calls"):
                        for tc in obj.get("tool_calls"):
                            print(f"   Tool: {tc.get('name')} | Args: {str(tc.get('args'))[:140]}")
