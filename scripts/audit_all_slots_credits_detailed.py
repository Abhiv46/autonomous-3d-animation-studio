import os
import sys
import time
import json
import re
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOTS_INFO = [
    {"slot": 0, "email": "techwire9999@gmail.com", "pid": "1876f0f7-bc42-4764-86c9-35d76cb3a615"},
    {"slot": 1, "email": "abhiv46@gmail.com", "pid": "1fc9b4e8-54eb-4141-907d-77002b691fc7"},
    {"slot": 2, "email": "rkumar.pub@gmail.com", "pid": "0fa549b9-b73f-4dac-8061-365fd0498eb2"},
    {"slot": 3, "email": "pinku.pub@gmail.com", "pid": "a1c6f19b-b046-41f3-9b33-fbc756646163"},
    {"slot": 4, "email": "infolillylooks@gmail.com", "pid": "c30fd23d-5a03-4081-baeb-fad9cbcc6a99"},
    {"slot": 5, "email": "elegantdriveways4u@gmail.com", "pid": "3782c658-cb27-4a0a-b80b-db721a4ba00e"},
    {"slot": 6, "email": "abhiv446@gmail.com", "pid": "11330d30-604f-4829-bb72-9d4f49e64a40"},
    {"slot": 7, "email": "rkumar.ukb@gmail.com", "pid": "642a9812-732d-411c-8bbe-380269736158"}
]

def audit_credits():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        for item in SLOTS_INFO:
            slot = item["slot"]
            expected_email = item["email"]
            pid = item["pid"]
            slot_res = {
                "slot": slot,
                "expected_email": expected_email,
                "detected_email": "",
                "tier": "UNKNOWN",
                "banners": [],
                "credit_text": [],
                "avatar_details": "",
                "status": "UNKNOWN",
                "notes": ""
            }
            print(f"\n==========================================")
            print(f"AUDITING SLOT {slot} ({expected_email})...")
            print(f"==========================================")

            try:
                # 1. Open home page of slot
                page.goto(f"https://flow.google.com/u/{slot}/", wait_until="domcontentloaded", timeout=35000)
                page.wait_for_timeout(3500)

                # Find any text containing 'credit', 'quota', 'limit', 'plan', 'plus', 'pro'
                body_text = page.inner_text("body")
                
                # Check for banners / alerts
                alert_elements = page.locator("[role='alert'], [class*='banner'], [class*='alert'], [class*='notification'], [class*='snackbar']").all()
                for el in alert_elements:
                    txt = el.inner_text().strip()
                    if txt and txt not in slot_res["banners"]:
                        slot_res["banners"].append(txt)

                # Check top navigation badges
                plus_badge = page.locator("text='PLUS', text='Plus', [aria-label*='Plus' i]").count()
                pro_badge = page.locator("text='PRO', text='Pro', [aria-label*='Pro' i]").count()
                if pro_badge > 0:
                    slot_res["tier"] = "PRO"
                elif plus_badge > 0:
                    slot_res["tier"] = "PLUS"
                else:
                    slot_res["tier"] = "FREE"

                # Look for credit chips/text
                credit_matches = re.findall(r"(\d+[\s\w]*credit[s]?)", body_text, re.IGNORECASE)
                if credit_matches:
                    slot_res["credit_text"].extend(credit_matches)

                # Check avatar popup
                avatar_btn = page.locator("button[aria-label*='Google Account' i], a[aria-label*='Google Account' i], img[alt*='Google Account' i]").first
                if avatar_btn.count() > 0:
                    aria = avatar_btn.get_attribute("aria-label") or ""
                    slot_res["avatar_details"] = aria
                    # Extract email from aria-label
                    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", aria)
                    if email_match:
                        slot_res["detected_email"] = email_match.group(0)

                # Screenshot slot home
                page.screenshot(path=f"data/audit_slot_{slot}_home.png")

                # 2. Also check inside the official project canvas for exact credit approval / bottom bar
                if pid:
                    project_url = f"https://flow.google.com/u/{slot}/project/{pid}"
                    page.goto(project_url, wait_until="domcontentloaded", timeout=35000)
                    page.wait_for_timeout(3500)

                    p_body = page.inner_text("body")
                    p_alerts = page.locator("[role='alert'], [class*='banner'], [class*='alert'], [class*='notification']").all()
                    for el in p_alerts:
                        txt = el.inner_text().strip()
                        if txt and txt not in slot_res["banners"]:
                            slot_res["banners"].append(txt)

                    p_credit_matches = re.findall(r"(\d+[\s\w]*credit[s]?)", p_body, re.IGNORECASE)
                    for cm in p_credit_matches:
                        if cm not in slot_res["credit_text"]:
                            slot_res["credit_text"].append(cm)

                    if "out of google flow credits" in p_body.lower():
                        slot_res["banners"].append("Out of Google Flow credits")
                    if "reached your generation limit" in p_body.lower() or "generation limit for today" in p_body.lower():
                        slot_res["banners"].append("Daily generation limit reached")
                    if "monthly limit" in p_body.lower():
                        slot_res["banners"].append("Monthly generation limit reached")

                    page.screenshot(path=f"data/audit_slot_{slot}_project.png")

                print(f"Slot {slot} Summary:")
                print(f"  Detected Email: {slot_res['detected_email'] or slot_res['avatar_details']}")
                print(f"  Tier: {slot_res['tier']}")
                print(f"  Banners: {slot_res['banners']}")
                print(f"  Credit strings: {slot_res['credit_text']}")

            except Exception as e:
                print(f"Error auditing slot {slot}: {e}")
                slot_res["notes"] = str(e)

            results.append(slot_res)

        browser.close()

    with open("data/fleet_credit_audit_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\nAudit completed and saved to data/fleet_credit_audit_results.json")

if __name__ == "__main__":
    audit_credits()
