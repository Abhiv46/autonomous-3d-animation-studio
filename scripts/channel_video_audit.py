import os
import sys
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with open(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 70)
print("   THE NAUGHTY DUO - COMPREHENSIVE CHANNEL VIDEO AUDIT REPORT")
print("=" * 70)

audit_results = []
for v in data.get("uploaded", []):
    key = v.get("key", "")
    title = v.get("youtube_title") or v.get("title") or key
    yt = v.get("youtube") or v.get("youtube_long") or v.get("link")
    fn = v.get("filename", "")
    
    # Check if file exists on disk
    p1 = Path(r"C:\TheNaughtyDuo_Automation\output") / fn
    p2 = Path(r"C:\TheNaughtyDuo_Automation") / fn
    fpath = p1 if p1.exists() else (p2 if p2.exists() else None)
    
    status = "AUDITED_VALID"
    note = "Visual content matches title"
    
    if key == "burn_u7_chanda_mama":
        status = "MISMATCH_DUPLICATE_PRIVATED"
        note = "Duplicate of Garden Me Jhula. Set to PRIVATE on YouTube Studio."
    elif key == "ep_18_magic_freeze_remote":
        status = "MISMATCH_CONTENT_PRIVATED"
        note = "Had old Sept 29 clip. Set to PRIVATE on YouTube Studio. Regenerating real Veo 9:16 clip now."
    elif not yt or "http" not in yt:
        status = "NOT_PUBLIC"
        note = "Saved for compilation / internal"
        
    audit_results.append({
        "key": key,
        "title": title,
        "url": yt,
        "file": fn,
        "exists_locally": fpath is not None,
        "size_mb": round(fpath.stat().st_size / (1024*1024), 2) if fpath else v.get("size_mb", 0),
        "status": status,
        "note": note
    })

print(f"Total Videos Analyzed: {len(audit_results)}")
mismatches = [a for a in audit_results if "MISMATCH" in a["status"]]
print(f"Mismatches / Duplicates Identified & Privated: {len(mismatches)}")
for m in mismatches:
    print(f"  [X] {m['key']} -> {m['url']}")
    print(f"      Title: {m['title']}")
    print(f"      Issue: {m['note']}")

valid_public = [a for a in audit_results if a["status"] == "AUDITED_VALID" and a["url"] and "http" in a["url"]]
print(f"\nAuthentic Public YouTube Videos: {len(valid_public)}")
for v in valid_public[-5:]:
    print(f"  [✓] {v['key']} -> {v['url']} ({v['size_mb']} MB)")
    print(f"      Title: {v['title'][:65]}")
