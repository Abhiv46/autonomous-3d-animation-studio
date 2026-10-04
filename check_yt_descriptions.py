import urllib.request
import re
import json

video_ids = [
    ("ep_18", "2fLDsrfukt4"),
    ("ep_06", "-70TI1fTDUk"),
    ("ep_07", "2wePkYa9lqw"),
    ("ep_14", "sa218mcIeiU"),
    ("ep_17", "HBmHJVsL0Ok"),
    ("ep_19", "jCqgPh2pYKw"),
    ("ep_20", "59Kj3e7JqJE"),
    ("ep_21", "3w4RHWr09TQ"),
    ("ep_21_alt", "vmY1l6qEuSo"),
    ("ep_22", "kfwu0ggfjow")
]

print("Checking video descriptions on YouTube...")
for ep, vid in video_ids:
    url = f"https://www.youtube.com/watch?v={vid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # Look for shortDescription
            m = re.search(r'"shortDescription":"(.*?)"', html)
            desc = m.group(1).encode().decode('unicode-escape') if m else ""
            desc_clean = desc.replace('\\n', ' ').strip()
            print(f"[{ep} | {vid}]: Description Length = {len(desc_clean)}")
            if len(desc_clean) < 50:
                print(f"   --> MISSING/SHORT: '{desc_clean}'")
            else:
                print(f"   --> OK: '{desc_clean[:60]}...'")
    except Exception as e:
        print(f"[{ep} | {vid}]: Error fetching: {e}")
