import os
import sys
import json
import re
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOTS = [
    (0, "techwire9999@gmail.com", "1876f0f7-bc42-4764-86c9-35d76cb3a615"),
    (1, "abhiv46@gmail.com", "1fc9b4e8-54eb-4141-907d-77002b691fc7"),
    (2, "rkumar.pub@gmail.com", "0fa549b9-b73f-4dac-8061-365fd0498eb2"),
    (3, "pinku.pub@gmail.com", "a1c6f19b-b046-41f3-9b33-fbc756646163"),
    (4, "infolillylooks@gmail.com", "c30fd23d-5a03-4081-baeb-fad9cbcc6a99"),
    (5, "elegantdriveways4u@gmail.com", "3782c658-cb27-4a0a-b80b-db721a4ba00e"),
    (6, "abhiv446@gmail.com", "11330d30-604f-4829-bb72-9d4f49e64a40"),
    (7, "rkumar.ukb@gmail.com", "642a9812-732d-411c-8bbe-380269736158"),
]

def check_slots():
    detailed_summary = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        for slot, email, pid in SLOTS:
            print(f"\n=================== SLOT {slot} ({email}) ===================")
            entry = {"slot": slot, "email": email, "tier": "FREE", "status": "UNKNOWN", "credits": "Unknown", "banner": ""}
            try:
                page.goto(f"https://flow.google.com/u/{slot}/project/{pid}", wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3500)

                body_text = page.inner_text("body")

                # Check membership / tier badge
                if "plus" in body_text.lower() and ("plus member" in body_text.lower() or page.locator("text='PLUS'").count() > 0):
                    entry["tier"] = "PLUS"
                elif page.locator("text='PRO'").count() > 0:
                    entry["tier"] = "PRO"

                # Check banners
                banners = page.locator("[role='alert'], [class*='banner'], [class*='notification'], [class*='alert']").all_inner_texts()
                banners_clean = [b.strip() for b in banners if len(b.strip()) < 250 and "cookie" not in b.lower() and "workshop" not in b.lower()]
                entry["banner"] = " | ".join(list(set(banners_clean)))

                # Find any credit occurrences
                credit_matches = re.findall(r"(\d+[\s\w]*credit[s]?)", body_text, re.IGNORECASE)
                entry["credits"] = list(set(credit_matches))

                # Check if out of credits or low
                if "out of google flow credits" in body_text.lower():
                    entry["status"] = "EXHAUSTED (0 credits)"
                elif "running low on google flow credits" in body_text.lower():
                    entry["status"] = "LOW CREDITS"
                elif "reached your generation limit" in body_text.lower():
                    entry["status"] = "DAILY LIMIT REACHED"
                else:
                    entry["status"] = "READY / ACTIVE"

                # Check prosemirror editor
                editor = page.locator(".ProseMirror").first
                entry["editor_ready"] = editor.is_enabled() if editor.count() > 0 else False

                print(f"Status: {entry['status']}")
                print(f"Credits text: {entry['credits']}")
                print(f"Banner: {entry['banner']}")
                print(f"Editor Ready: {entry['editor_ready']}")

            except Exception as e:
                print(f"Error checking slot {slot}: {e}")
                entry["status"] = f"ERROR: {e}"

            detailed_summary.append(entry)

        ctx.close()

    with open("data/slot_controls_summary.json", "w", encoding="utf-8") as f:
        json.dump(detailed_summary, f, indent=2)

if __name__ == "__main__":
    check_slots()
