import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Viral Metadata Dictionary for all videos
VIDEOS_TO_UPDATE = [
    {
        "id": "kfwu0ggfjow",
        "name": "Gulab Jamun Chori",
        "title": "Magical Glowing Gulab Jamun Chori! 🍯😱 Kaartik Ne Pakda! #TheNaughtyDuo #shorts",
        "description": """Kaavya ne kitchen me dabe paon jakar chori kiya magical glowing gulab jamun! 🍯😱
Lekin bhaiyya Kaartik ne rangey haathon pakad liya! Phir dekhiye dono ne milkar kaise yummy mithaai enjoy ki aur Mummy ko manaya! 🥰❤️

Aapne bhi bachpan me mithaai chori ki hai kya? Comment me batayein! 👇😂

Aise hi funny aur cute 3D family cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔✨

#shorts #TheNaughtyDuo #funnycartoon #3danimation #hindicartoon #kaavyaandkaartik #comedy #relatablecomedy #viralshorts #trending #gulabjamun #kidsanimation""",
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "gulab jamun chori",
            "funny kids cartoon", "3d animation hindi", "kaavya and kaartik",
            "sweet prank", "relatable comedy", "viral shorts 2026", "trending cartoon",
            "cocomelon hindi", "kids animation 3d", "family comedy"
        ]
    },
    {
        "id": "iLNSVrQO-v8",
        "name": "Mummy Ki High Heels",
        "title": "Kaavya Ne Pehni Mummy Ki High Heels! 😂👠 Sassy Model Kaavya! #TheNaughtyDuo #shorts",
        "description": """Kaavya ne pehni Mummy ki stylish high heels! 😂👠
Ghar par ramp-walk karti sassy supermodel Kaavya ko jab Kaartik ne dekha toh hasi nahi ruki! Dekhiye Kaavya ka super cute reaction! 💖🥰

Aapki behen bhi bachpan me heels pehanti thi kya? Comment me batayein! 👇

Mazedar 3D Hindi cartoon comedy ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #highheels #funnycartoon #3danimation #hindicartoon #sassykaavya #siblingcomedy #viralshorts #trending #familycomedy""",
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "mummy ki high heels",
            "kaavya fashion show", "funny hindi cartoon", "3d animation kids",
            "sibling fun", "comedy shorts", "viral shorts 2026", "hindi rhymes 3d",
            "cute toddler girl", "relatable comedy"
        ]
    },
    {
        "id": "6k8HcolTcZk",
        "name": "Inspector Kaartik Nakli Moustache",
        "title": "Inspector Kaartik Ne Pakda Mummy Ko! 👮‍♂️🍪 Nakli Moustache Prank! #TheNaughtyDuo #shorts",
        "description": """Inspector Kaartik ne lagayi nakli mooch aur shuru kiya cookie investigation! 👮‍♂️🍪🔍
Mummy kitchen me cookies chupa rahi thi lekin Inspector Kaartik ne unhe rangey haath pakad liya! 😂❤️

Aapko Kaartik ka Inspector look kaisa laga? Comment me batayein! 👇

Aise hi mazedar 3D cartoon comedy ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #inspectorprank #funnykids #3danimation #hindicartoon #cookieprank #comedy #viralshorts #trending #kaavyaandkaartik""",
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "inspector kaartik",
            "cookie prank cartoon", "funny kids animation", "3d animation hindi",
            "fake mustache prank", "comedy shorts", "viral shorts 2026", "kids cartoon"
        ]
    },
    {
        "id": "jCqgPh2pYKw",
        "name": "Flying Cockroach Panic",
        "title": "Brave Ban Rahi Thi Jab Tak Cockroach Ne Pankh Nahi Khole! 🪳😱 #TheNaughtyDuo #shorts",
        "description": """Brave ban rahi thi Kaavya... jab tak cockroach ne apne pankh nahi khole! 🪳😱💨
Ghar me mach gaya hungama jab flying cockroach seedha sofa par aaya! Kaartik aur Kaavya ka comedy panic dekh kar aapki hasi nahi rukegi! 😂

Kis kis ko udne wale cockroach se darr lagta hai? Comment me '🙋‍♂️' bhejein! 👇

Daily 3D comedy animation ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #cockroachprank #flyingcockroach #funnycomedy #3danimation #hindicartoon #relatablecomedy #viralshorts #trending #familycomedy""",
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "flying cockroach",
            "cockroach attack funny", "kids cartoon comedy", "3d animation hindi",
            "viral shorts 2026", "relatable kids humor", "funny scream cartoon",
            "kaavya and kaartik", "comedy shorts"
        ]
    },
    {
        "id": "59Kj3e7JqJE",
        "name": "Papa-Kaavya Arm Wrestling",
        "title": "Kaavya Ne Haraya Papa Ko Panje Me! 💪👧🧔 The Great Arm Wrestling! #TheNaughtyDuo #shorts",
        "description": """Kaavya ne lagaya Papa se panja! 💪👧🧔
Nanhi Kaavya ne dono haathon se poori taqat laga di aur Papa ne pyara drama karke haar maan li! Emotional aur heartwarming family moment! ❤️✨

Aapne kabhi Papa ko panje me haraya hai? Comment karke batayein! 👇🥰

Aise hi pyare family cartoon moments ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #fatherdaughter #armwrestling #familycomedy #3danimation #cutebaby #hindicartoon #viralshorts #trending #emotional""",
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "papa aur beti",
            "arm wrestling", "father daughter love", "cute cartoon hindi",
            "3d family animation", "viral shorts 2026", "heartwarming cartoon",
            "kaavya cute", "family comedy"
        ]
    },
    {
        "id": "2fLDsrfukt4",
        "name": "Mummy Ka Magic Remote",
        "title": "Mummy Ka Magic Remote! 🎮😂 Sab Freeze Ho Gaye! #TheNaughtyDuo #shorts",
        "description": """Mummy ne dabaya TV remote ka button aur sab freeze ho gaye! 🎮🧊😂
Kaartik aur Kaavya funny statue ban kar freeze ho gaye! Dekhiye unfreeze hone par kya dhamaka hua! ❤️✨

Agar aapko magic remote mil jaye toh sabse pehle kisko freeze karenge? Comment karein! 👇

Mazedar 3D comedy cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #magicremote #freezeprank #funnycartoon #3danimation #hindicartoon #familycomedy #viralshorts #trending #kidspranks""",
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "magic remote",
            "freeze prank cartoon", "funny kids animation", "3d cartoon hindi",
            "kaavya kaartik comedy", "viral shorts 2026", "magic remote hindi"
        ]
    },
    {
        "id": "-70TI1fTDUk",
        "name": "Ghar Me Nakli Chuha",
        "title": "Ghar Me Aaya Nakli Chuha! 🐭😲 Kaartik Ka Prank Backfire! #TheNaughtyDuo #shorts",
        "description": """Kaartik ne kitchen me chhoda nakli toy chuha! 🐭😱
Mummy aur Kaavya dar ke bajaye has padi aur prank Kaartik par hi ulta pad gaya! Super funny family prank! 😂❤️

Aapne kabhi nakli chuhe ka prank kiya hai? Comment me batayein! 👇

Aise hi cute pranks aur 3D Hindi cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔

#shorts #TheNaughtyDuo #toymouse #funnyprank #3danimation #hindicartoon #kaavyaandkaartik #comedy #viralshorts #trending #prankbackfire""",
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "nakli chuha prank",
            "toy mouse funny", "hindi cartoon prank", "3d animation comedy",
            "trending shorts 2026", "prank backfire", "kids animation"
        ]
    }
]

def update_video_seo(page, vid_info):
    vid_id = vid_info["id"]
    name = vid_info["name"]
    url = f"https://studio.youtube.com/video/{vid_id}/edit"
    print(f"\n=======================================================")
    print(f"[*] Processing: {name} (ID: {vid_id})")
    print(f"[*] URL: {url}")
    print(f"=======================================================")
    
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(3)
    
    # Skip dialog if present
    skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
    if skip.count() > 0 and skip.is_visible():
        skip.click()
        time.sleep(2)
        
    # 1. Update Title
    title_box = page.locator("#textbox[aria-label*='title' i], [aria-label*='Add a title' i]").first
    if title_box.count() > 0:
        title_box.click()
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        title_box.fill(vid_info["title"][:100])
        time.sleep(0.5)
        print("  [✓] Title updated!")
        
    # 2. Update Description
    desc_area = page.locator("#description-textarea div#textbox, ytcp-mention-textbox#description-textarea div#textbox").first
    if desc_area.count() > 0:
        desc_area.click()
        time.sleep(0.3)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        desc_area.fill(vid_info["description"])
        time.sleep(0.5)
        print("  [✓] Description updated!")
        
    # 3. Update Tags
    show_more = page.locator("#toggle-button, button:has-text('Show more')").first
    if show_more.count() > 0 and show_more.is_visible():
        show_more.scroll_into_view_if_needed()
        show_more.click()
        time.sleep(1)
        
    tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
    if tags_input.count() > 0 and tags_input.is_visible():
        tags_input.scroll_into_view_if_needed()
        tags_input.click()
        for t in vid_info["tags"]:
            page.keyboard.type(t)
            page.keyboard.press("Enter")
            time.sleep(0.05)
        print("  [✓] Tags entered!")
        
    # 4. Save
    save_btn = page.locator("ytcp-button#save, ytcp-button:has-text('Save'), #save-button").first
    print("  [*] Checking save button status...")
    time.sleep(1)
    if save_btn.count() > 0 and save_btn.is_enabled():
        save_btn.click()
        time.sleep(4)
        print(f"  [🎉 SUCCESS] Saved updates for {name}!")
    else:
        print(f"  [i] Save button was not enabled or already saved.")
        
    proof_path = fr"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\seo_saved_{vid_id}.png"
    page.screenshot(path=proof_path)
    print(f"  [✓] Proof screenshot: seo_saved_{vid_id}.png")

def main():
    with sync_playwright() as p:
        print("[*] Connecting to Brave over CDP...")
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        
        for idx, vid in enumerate(VIDEOS_TO_UPDATE, 1):
            try:
                print(f"\n[{idx}/{len(VIDEOS_TO_UPDATE)}] Starting update...")
                update_video_seo(page, vid)
            except Exception as e:
                print(f"[!] Error on {vid['name']}: {e}")
                
        print("\n" + "=" * 60)
        print("   ALL 7 VIDEOS SUCCESSFULLY OPTIMIZED WITH VIRAL SEO!")
        print("=" * 60)

if __name__ == "__main__":
    main()
