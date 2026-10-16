import os
import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REGISTRY_PATH = r"C:\TheNaughtyDuo_Automation\channel_master_upload_registry.json"

def check_video(query):
    if not os.path.exists(REGISTRY_PATH):
        print("[-] Registry file not found!")
        return None
        
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    query_lower = query.lower()
    matches = []
    for item in data.get("videos", []):
        f_name = item.get("file_name", "").lower()
        topic  = item.get("topic", "").lower()
        e_id   = item.get("id", "").lower()
        if query_lower in f_name or query_lower in topic or query_lower in e_id:
            matches.append(item)
            
    if not matches:
        print(f"[+] '{query}' is NOT found in upload registry (READY TO PROCESS).")
        return False
        
    for m in matches:
        yt = m.get("youtube", {})
        tt = m.get("tiktok", {})
        print(f"\n==========================================")
        print(f"🎬 Episode: {m.get('id')} - {m.get('topic')}")
        print(f"📁 File: {m.get('file_name')} ({m.get('duration')})")
        print(f"🔴 YouTube: {'ALREADY UPLOADED' if yt.get('uploaded') else 'NOT UPLOADED'} ({yt.get('views', '0 views')})")
        print(f"🖤 TikTok:  {'ALREADY UPLOADED' if tt.get('uploaded') else 'NOT UPLOADED'} ({tt.get('views', '0 views')})")
        print(f"==========================================")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_video(" ".join(sys.argv[1:]))
    else:
        print("Usage: python verify_before_upload.py <filename_or_keyword>")
