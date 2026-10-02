import os
import sys
import json
import re
from playwright.sync_api import sync_playwright

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"

SLOTS = [0, 1, 2, 3, 4, 5, 6, 7]

def check_all_account_credits():
    results = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        for slot in SLOTS:
            slot_info = {
                "slot": slot,
                "email": "",
                "name": "",
                "credits": "Unknown",
                "tier_or_buttons": [],
                "banner_alert": "",
                "status": "UNKNOWN"
            }
            print(f"\n==========================================")
            print(f"CHECKING EXACT CREDITS FOR SLOT {slot}...")
            print(f"==========================================")

            try:
                page.goto(f"https://flow.google.com/u/{slot}/", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3500)

                # Check any alert banners on the page
                banners = page.locator("[role='alert'], [class*='banner'], [class*='notification'], [class*='alert']").all_inner_texts()
                clean_banners = [b.strip() for b in banners if len(b.strip()) < 200 and "cookie" not in b.lower() and "workshop" not in b.lower()]
                if clean_banners:
                    slot_info["banner_alert"] = " | ".join(list(set(clean_banners)))

                # Click Account details button
                user_btn = page.locator("[aria-label='Account details'], .header-user-button").first
                if user_btn.count() > 0:
                    user_btn.click()
                    page.wait_for_timeout(2000)

                    # Screenshot popover
                    screenshot_path = f"data/slot_{slot}_account_details.png"
                    page.screenshot(path=screenshot_path)

                    # Look for popover content
                    # Scan for text with credits
                    body_text = page.locator("body").inner_text()
                    credit_match = re.search(r"(\d+[\s\w]*Google Flow credits)", body_text, re.IGNORECASE)
                    if not credit_match:
                        # Try broader pattern
                        credit_match = re.search(r"(\d+[\s\w]*credits?)", body_text, re.IGNORECASE)

                    if credit_match:
                        slot_info["credits"] = credit_match.group(1).strip()
                    else:
                        # Check if out of credits
                        if "out of google flow credits" in body_text.lower():
                            slot_info["credits"] = "0 Google Flow credits (Out of credits)"
                        elif "0 credits" in body_text.lower():
                            slot_info["credits"] = "0 Google Flow credits"

                    # Check buttons inside popover
                    popover_btns = page.locator("button, a").all_inner_texts()
                    for btn_text in popover_btns:
                        bt = btn_text.strip()
                        if bt in ["Upgrade", "Manage subscription", "Add AI credits", "Sign out of all accounts"]:
                            slot_info["tier_or_buttons"].append(bt)

                    # Extract email & name
                    # In popover, email is often in a div or span
                    email_match = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", body_text)
                    if email_match:
                        slot_info["email"] = email_match.group(1)

                    print(f"Slot {slot} Found:")
                    print(f"  Email: {slot_info['email']}")
                    print(f"  Credits: {slot_info['credits']}")
                    print(f"  Actions: {slot_info['tier_or_buttons']}")
                    print(f"  Banner: {slot_info['banner_alert']}")
                else:
                    print(f"Slot {slot}: Account details button not found")

            except Exception as e:
                print(f"Error checking slot {slot}: {e}")
                slot_info["status"] = f"ERROR: {e}"

            results.append(slot_info)

        ctx.close()

    with open("data/exact_fleet_credits.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n[+] Audit of all 8 slots complete!")

if __name__ == "__main__":
    check_all_account_credits()
