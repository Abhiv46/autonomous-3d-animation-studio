import sys
import time
import json
from playwright.sync_api import sync_playwright

IMAGE_PROMPT = (
    "Vertical 9:16 aspect ratio, ultra-colorful 3D Pixar animated cartoon comedy style. "
    "Bright cheerful sunny morning living room. Exactly ONE toddler Kaavya (3.5 years old, "
    "bright pastel pink frock, twin high pigtail buns with pink ribbons, huge glossy brown cartoon eyes, "
    "blushing chubby rosy cheeks) jumping high in the air with joyful toddler laughter, mouth wide open, "
    "tiny chubby hands reaching up to pop colorful floating soap bubbles. Beside her, Exactly ONE 5-year-old Kaartik "
    "(yellow cartoon tee, denim shorts, smiling cartoon face) dynamically waving a bubble wand with lots of "
    "iridescent shiny bubbles filling the room. Expressive cute cartoon faces, high saturation, dynamic bouncy cartoon energy, "
    "Cocomelon Disney Pixar 3D aesthetic, zero photorealism, ultra-vibrant candy colors."
)

def run():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        flow_page = next(pg for pg in browser.contexts[0].pages if "flow.google.com" in pg.url)
        
        # 1. Click 'Image' button in the open menu
        print("[1] Clicking 'Image' tab in mode menu...", flush=True)
        img_tab = flow_page.locator("button:has-text('Image'), div:has-text('Image')").first
        # Find exact button with text 'Image'
        for b in flow_page.locator("button").all():
            if b.inner_text().strip() == "Image":
                img_tab = b
                break
        img_tab.click()
        time.sleep(1)
        
        # 2. Ensure 9:16 is selected
        v916 = flow_page.locator("button:has-text('9:16')").first
        if v916.count() > 0:
            v916.click()
            time.sleep(0.5)
            
        # 3. Dismiss menu by pressing Escape or clicking outside
        flow_page.keyboard.press("Escape")
        time.sleep(1)
        
        # 4. Clear prompt box and type new IMAGE_PROMPT
        print("[2] Clearing prompt box and typing Image Prompt...", flush=True)
        pm = flow_page.locator("div.ProseMirror, [contenteditable='true']").first
        pm.click()
        flow_page.keyboard.press("Control+A")
        flow_page.keyboard.press("Backspace")
        time.sleep(0.5)
        
        # Type prompt
        pm.fill(IMAGE_PROMPT)
        time.sleep(1)
        
        # 5. Click Generate (arrow_forward)
        print("[3] Clicking Generate button...", flush=True)
        arrow = flow_page.locator("button:has-text('arrow_forward'), button.generate-icon-button, [aria-label='Start generation']").first
        arrow.click()
        time.sleep(2)
        
        # Check if spend confirmation pops up
        for _ in range(3):
            agree = flow_page.locator("button:has-text('Continue'), button:has-text('Agree')").first
            if agree.count() > 0 and agree.is_visible():
                print("[+] Confirming spend dialog...")
                agree.click()
                time.sleep(1)
                
        flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\ep23_image_gen_submitted.png")
        print("[SUCCESS] Image generation submitted! Screenshot saved.")

if __name__ == "__main__":
    run()
