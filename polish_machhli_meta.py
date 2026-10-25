import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r"C:\TheNaughtyDuo_Automation\output"
thumb_path = os.path.join(OUT_DIR, "machhli_rani_thumbnail.jpg")

subprocess.run(['taskkill', '/F', '/IM', 'brave.exe'], capture_output=True)
time.sleep(2)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=r'C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data',
        executable_path=r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
        headless=True,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        viewport={'width': 1600, 'height': 1000}
    )
    page = browser.new_page()
    page.goto('https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short', timeout=60000)
    time.sleep(6)

    try:
        skip = page.get_by_text('SKIP TO YOUTUBE STUDIO')
        if skip.count() > 0:
            skip.first.click(force=True)
            time.sleep(3)
    except Exception:
        pass

    # Row 1 is Machhli
    row1 = page.locator('ytcp-video-row').first
    print("[*] Opening details for Row 1...", flush=True)
    row1.locator('a#video-title').first.click(force=True)
    time.sleep(6)

    # Title
    t_box = page.locator("#title-textarea #textbox, div#textbox[aria-label*='title' i]").first
    t_box.scroll_into_view_if_needed()
    t_box.click(force=True)
    time.sleep(0.3)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    time.sleep(0.3)
    page.keyboard.insert_text("मछली जल की रानी है 🐟 Machhli Jal Ki Rani Hai | The Naughty Duo #Shorts")
    time.sleep(1)
    print("  [OK] Bilingual Title set.", flush=True)

    # Description
    d_box = page.locator("#description-textarea #textbox, div#textbox[aria-label*='Tell viewers' i]").first
    if d_box.count() > 0:
        d_box.scroll_into_view_if_needed()
        d_box.click(force=True)
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        page.keyboard.insert_text("""मछली जल की रानी है! 🐟🌊 Jeevan uska paani hai! Kaartik aur Kaavya ne dekhi talab me pyaari glowing son pari machhli! Dekhiye yeh super popular evergreen Hindi nursery rhyme 3D animation me! 🥰✨

🗣️ Dialogue & Rhyme:
Kaartik: "Machhli jal ki rani hai, jeevan uska paani hai!" 🐟🌊
Kaavya: "Arey bhaiya dekho! Kitni pyaari golden fish hai!" ✨
Kaartik: "Haath lagao toh darr jayegi, bahar nikalo toh marr jayegi!" 🤲❤️
Together: "Agar aapko hamari masti pasand aayi, toh video ko LIKE karein aur channel ko SUBSCRIBE karein! Bye-bye!" 👋❤️

🔔 Subscribe to The Naughty Duo for daily 3D Hindi nursery rhymes & animated cartoons!

#TheNaughtyDuo #Shorts #MachhliJalKiRaniHai #HindiRhymes #KidsCartoon #3DAnimation #CuteBabies #TrendingShorts #WaterFish""")
        time.sleep(1)
        print("  [OK] Description set.", flush=True)

    # Thumbnail
    if os.path.exists(thumb_path):
        thumb_input = page.locator("input#file-loader, input[type='file'][accept*='image']").first
        if thumb_input.count() > 0:
            thumb_input.set_input_files(thumb_path)
            time.sleep(3)
            print("  [OK] 3D Thumbnail uploaded.", flush=True)

    # Save
    save_btn = page.locator("#save, button:has-text('Save'), ytcp-button:has-text('Save')").first
    if save_btn.is_enabled():
        save_btn.click(force=True)
        time.sleep(4)
        print("  [OK] Changes saved successfully!", flush=True)

    browser.close()
    print("[ALL DONE] Machhli Jal Ki Rani fully polished and scheduled! 🚀🎉", flush=True)
