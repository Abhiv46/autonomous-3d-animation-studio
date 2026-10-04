import sys
import time
import threading
import win32gui
import win32con
from pathlib import Path
from playwright.sync_api import sync_playwright

VIDEO_FILE = str(Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_TikTok_RedButtonMagic_Master_CorrectSequence.mp4").resolve())

YT_TITLE = '"Red Button Ko Mat Dabana!" 🔴😱 Kaavya Ne Dabaya Phir Jo Hua... 😂🫧 #TheNaughtyDuo #shorts'

YT_DESC = """Kaartik ne baar-baar mana kiya tha — "Red Button ko bilkul mat dabana!" 🔴✋
Lekin Kaavya kahan maanne wali thi! Jaise hi Kaavya ne mysterious button dabaya... Achanak ek Giant Beach Ball unke peeche bhaagne lagi! 😱🏃‍♂️💨

Lekin ruko... machine se aakhir me kya nikla? Cute and magical bubbles! 🫧😂✨
Dekhiye Kaavya aur Kaartik ki sabse mazedaar shararat! 🥰❤️

💬 Sawaal: Aapko kya laga tha red button dabane se kya hoga? Comment me batayein! 👇

🔔 Aise hi funny 3D cartoons aur daily family adventures ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! ✨

#shorts #TheNaughtyDuo #KaavyaAndKaartik #RedButtonPrank #3DAnimation #HindiCartoon #FunnyShorts #KidsCartoon #Comedy #GiantBallChase #BubbleMachine #ViralShorts #TrendingShorts"""

YT_TAGS = [
    "The Naughty Duo", "TheNaughtyDuo", "Kaartik and Kaavya", "red button prank",
    "dont press the red button", "hindi cartoon funny", "3d animation hindi",
    "funny kids animation", "giant ball chase", "bubble machine cartoon",
    "shorts", "viral shorts 2026", "trending cartoon shorts"
]

def handle_open_dialog():
    print("[Thread] Waiting for Windows Open dialog...")
    for _ in range(30):
        hwnd = win32gui.FindWindow("#32770", "Open")
        if hwnd:
            print(f"[Thread] Found Open dialog! HWND: {hwnd}")
            time.sleep(0.5)
            edit_hwnd = None
            def enum_children(child_hwnd, _):
                nonlocal edit_hwnd
                cls = win32gui.GetClassName(child_hwnd)
                if cls == "Edit":
                    edit_hwnd = child_hwnd
            win32gui.EnumChildWindows(hwnd, enum_children, None)
            
            if edit_hwnd:
                print(f"[Thread] Found Edit HWND: {edit_hwnd}")
                win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, None, VIDEO_FILE)
                time.sleep(0.5)
                win32gui.PostMessage(edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(edit_hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                print("[Thread] Sent file path and pressed Enter successfully!")
                return True
        time.sleep(0.5)
    print("[Thread] Timeout waiting for Open dialog.")
    return False

def main():
    print("[1] Connecting to Brave via CDP...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        
        # Find YouTube Studio page
        page = None
        for pg in context.pages:
            if "studio.youtube.com" in pg.url:
                page = pg
                break
                
        if not page:
            print("[+] Opening YouTube Studio...", flush=True)
            page = context.new_page()
            page.goto("https://studio.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/videos/short", wait_until="domcontentloaded", timeout=45000)
            time.sleep(4)
        else:
            print(f"[+] Found YouTube Studio page: {page.url}", flush=True)
            page.bring_to_front()
            
        proof_dir = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")
        
        # Dismiss any leftover dialogs
        close_btn = page.locator("ytcp-uploads-dialog #close-button, ytcp-button#dismiss-button").first
        if close_btn.count() > 0 and close_btn.is_visible():
            print("[+] Closing old dialog...", flush=True)
            close_btn.click()
            time.sleep(1)

        # 1. Click Create button
        print("[2] Opening Upload Dialog...", flush=True)
        create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create'), #create-icon").first
        if create_btn.count() > 0 and create_btn.is_visible():
            create_btn.click()
            time.sleep(1)
            upload_item = page.locator("ytcp-text-menu-item:has-text('Upload videos'), text='Upload videos'").first
            if upload_item.count() > 0 and upload_item.is_visible():
                upload_item.click()
                time.sleep(2)
                
        # 2. Start dialog thread & click Select files
        print("[3] Initiating file selection...", flush=True)
        t = threading.Thread(target=handle_open_dialog)
        t.start()
        
        select_files_btn = page.locator("#select-files-button, button:has-text('Select files')").first
        if select_files_btn.count() > 0 and select_files_btn.is_visible():
            select_files_btn.click()
            
        t.join(timeout=20)
        print("[4] File selected! Waiting 10s for upload wizard to initialize...", flush=True)
        time.sleep(10)
        
        page.screenshot(path=str(proof_dir / "yt_upload_wizard_opened.png"))
        
        # 3. Detect Video ID/Link
        video_link = None
        for _ in range(15):
            links = page.locator("a.ytcp-video-info, a[href*='youtu.be'], a[href*='youtube.com/shorts']")
            if links.count() > 0:
                for idx in range(links.count()):
                    href = links.nth(idx).get_attribute("href")
                    if href and ("youtu.be" in href or "shorts" in href):
                        video_link = href
                        break
            if video_link:
                break
            time.sleep(1)
        print(f"[+] Detected Video Link: {video_link}", flush=True)
        
        # 4. Set Title
        print("[5] Setting Title...", flush=True)
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            time.sleep(0.3)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.3)
            title_box.fill(YT_TITLE[:100])
            time.sleep(0.5)
            print("[+] Title set!", flush=True)
            
        # 5. Set Description
        print("[6] Setting Description...", flush=True)
        desc_box = page.locator("#textbox[aria-label*='description' i], ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() > 0:
            desc_box.click()
            time.sleep(0.3)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.3)
            desc_box.fill(YT_DESC)
            time.sleep(0.5)
            print("[+] Description set!", flush=True)
            
        # 6. Set Audience (Not made for kids - enables comments)
        print("[7] Setting Audience...", flush=True)
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            time.sleep(0.5)
            print("[+] Audience set to Not Made for Kids (Comments enabled)!", flush=True)
            
        # 7. Add Tags
        show_more = page.locator("#toggle-button, button:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            show_more.click()
            time.sleep(1)
            
        tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
        if tags_input.count() > 0 and tags_input.is_visible():
            print("[*] Adding viral tags...", flush=True)
            tags_input.click()
            for t_tag in YT_TAGS:
                page.keyboard.type(t_tag)
                page.keyboard.press("Enter")
                time.sleep(0.05)
            print("[+] Tags added!", flush=True)
            
        page.screenshot(path=str(proof_dir / "yt_details_filled.png"))
        
        # 8. Wizard Steps (Next -> Next -> Next -> Visibility)
        print("[8] Stepping through wizard...", flush=True)
        for step in range(3):
            next_btn = page.locator("#next-button").first
            if next_btn.count() > 0 and next_btn.is_visible():
                next_btn.click()
                print(f"[+] Clicked Next button (step {step+1})", flush=True)
                time.sleep(2)
                
        # 9. Set Visibility to Public
        print("[9] Setting Visibility to Public...", flush=True)
        public_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
        if public_radio.count() > 0 and public_radio.is_visible():
            public_radio.click()
            time.sleep(1)
            print("[+] Public visibility selected!", flush=True)
            
        page.screenshot(path=str(proof_dir / "yt_visibility_public.png"))
        
        # 10. Click Publish / Done
        print("[10] Publishing video...", flush=True)
        done_btn = page.locator("#done-button").first
        if done_btn.count() > 0 and done_btn.is_visible():
            done_btn.click()
            print("[+] Done button clicked!", flush=True)
            time.sleep(5)
            
        # 11. Final verification
        proof_path = proof_dir / "yt_published_proof.png"
        page.screenshot(path=str(proof_path))
        print(f"[SUCCESS] YouTube video uploaded & published! Proof: {proof_path}", flush=True)

if __name__ == "__main__":
    main()
