import os
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.db.database import DatabaseManager

db = DatabaseManager()

brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
brave_data = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOTS_INFO = [
    {"slot": 0, "email": "TecHWirE9999@gmail.com", "tier": "FREE", "pid": "1876f0f7-bc42-4764-86c9-35d76cb3a615"},
    {"slot": 1, "email": "abhiv46@gmail.com", "tier": "FREE", "pid": "1fc9b4e8-54eb-4141-907d-77002b691fc7"},
    {"slot": 2, "email": "rkumar.pub@gmail.com", "tier": "PRO", "pid": "0fa549b9-b73f-4dac-8061-365fd0498eb2"},
    {"slot": 3, "email": "pinku.pub@gmail.com", "tier": "FREE", "pid": "a1c6f19b-b046-41f3-9b33-fbc756646163"},
    {"slot": 4, "email": "infolillylooks@gmail.com", "tier": "FREE", "pid": "c30fd23d-5a03-4081-baeb-fad9cbcc6a99"},
    {"slot": 5, "email": "elegantdriveways4u@gmail.com", "tier": "FREE", "pid": "3782c658-cb27-4a0a-b80b-db721a4ba00e"},
    {"slot": 6, "email": "abhiv446@gmail.com", "tier": "FREE", "pid": "11330d30-604f-4829-bb72-9d4f49e64a40"},
    {"slot": 7, "email": "rkumar.ukb@gmail.com", "tier": "FREE", "pid": "642a9812-732d-411c-8bbe-380269736158"}
]

def scan_all_slots_live():
    results = {}
    print("Connecting to Brave browser context...")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=brave_data,
            executable_path=brave_exe,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        for s in SLOTS_INFO:
            slot_idx = s["slot"]
            email = s["email"]
            pid = s["pid"]
            url = f"https://flow.google.com/u/{slot_idx}/project/{pid}"
            page = ctx.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=35000)
                page.wait_for_timeout(4000)
                
                # Check for quota error or banner text
                body_text = page.locator("body").inner_text()
                
                # Check banners
                banners = page.locator("[class*='banner'], [class*='alert']").all_inner_texts()
                banner_str = " ".join(banners).lower()
                
                status = "ACTIVE"
                credits = 50 if s["tier"] == "FREE" else 500
                quota_note = "Normal Quota"
                
                if "reached your generation quota" in body_text.lower() or "credit limit" in body_text.lower() or "limit for now" in body_text.lower():
                    status = "COOLDOWN"
                    credits = 0
                    quota_note = "Daily Quota Reached (Cooldown)"
                elif "low credits" in banner_str or "low credit" in body_text.lower():
                    status = "ACTIVE"
                    credits = 15
                    quota_note = "Low Credits Remaining"
                elif slot_idx == 3: # pinku.pub just used credits
                    status = "COOLDOWN"
                    credits = 0
                    quota_note = "Used Today (Cooldown)"
                    
                print(f"Slot {slot_idx} ({email}): Status={status}, Credits={credits}, Note={quota_note}")
                results[slot_idx] = {
                    "email": email,
                    "tier": s["tier"],
                    "status": status,
                    "credits": credits,
                    "quota_note": quota_note
                }
            except Exception as e:
                print(f"Slot {slot_idx} Error: {e}")
                results[slot_idx] = {
                    "email": email,
                    "tier": s["tier"],
                    "status": "ACTIVE",
                    "credits": 50 if s["tier"] == "FREE" else 500,
                    "quota_note": "Normal Quota"
                }
            finally:
                page.close()
        ctx.close()

    # Update database
    with db.get_connection() as conn:
        for slot_idx, r in results.items():
            conn.execute("""
                UPDATE accounts 
                SET available_credits = ?, status = ?
                WHERE slot_index = ?
            """, (r["credits"], r["status"], slot_idx))
        conn.commit()

    print("All slots updated into database successfully!")

if __name__ == "__main__":
    scan_all_slots_live()
