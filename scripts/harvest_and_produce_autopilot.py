import os
import sys
import time
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"
RAW_CLIPS.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BRAVE_EXE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
BRAVE_DATA = r"C:\Users\user\AppData\Local\BraveSoftware\Brave-Browser\User Data"
FFMPEG_BIN = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
UPLOAD_LOG = Path(r"C:\TheNaughtyDuo_Automation\uploaded_videos_log.json")
STATUS_FILE = BASE_DIR / "data" / "live_production_status.json"

# Active Flow Accounts with available credits
ACTIVE_SLOTS = [
    {"slot": 7, "email": "rkumar.ukb@gmail.com", "tier": "FREE"},
    {"slot": 5, "email": "elegantdriveways4u@gmail.com", "tier": "FREE"},
    {"slot": 6, "email": "abhiv446@gmail.com", "tier": "FREE"},
    {"slot": 4, "email": "infolillylooks@gmail.com", "tier": "FREE"},
    {"slot": 0, "email": "TecHWirE9999@gmail.com", "tier": "FREE"}
]

# Fresh high-graphic episodes
EPISODES_TO_PRODUCE = [
    {
        "id": "ep_13_floor_is_lava",
        "title": "The Floor is Lava! 🌋🛋️ Mummy Ka Flamingo Dance! #TheNaughtyDuo #shorts",
        "desc": (
            "Kaartik aur Kaavya ne living room me announce kar diya: 'THE FLOOR IS LAVA!' 🌋😱\n"
            "Mummy garam chai le kar aa rahi thi aur unko ek pair par pillow par flamingo dance karna pada! 😂🤣\n"
            "Dekhiye Mummy ka ye super hilarious balancing act!\n\n"
            "Kya aapne bhi bachpan me Floor is Lava game khela hai? Comment karke zaroor batayein! 👇❤️\n\n"
            "Aise hi funny 3D kids animation cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔\n\n"
            "#shorts #TheNaughtyDuo #thefloorislava #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #viralshorts #trending"
        ),
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "the floor is lava cartoon",
            "mummy flamingo dance", "funny kids animation", "3d animation shorts",
            "hindi cartoon shorts", "kartik and kaavya", "viral shorts 2026",
            "family comedy shorts", "relatable comedy"
        ],
        "scenes": [
            {
                "part": 1,
                "prompt": (
                    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
                    "Full 3D CGI animation. Bright cinematic Indian living room. Exactly ONE chubby 3D toddler boy Kaartik "
                    "(5 years old, rounded cute cheeks, expressive 3D brown eyes, volumetric black hair, bright yellow polo shirt, blue shorts) "
                    "leaps enthusiastically from the sofa onto the center wooden coffee table shouting with dramatic cartoon eyes: "
                    "'The floor is lava! 5, 4, 3, 2, 1!' Cute 3D toddler sister Kaavya (3.5 years old, curly hair, bright pink frock) "
                    "scrambles quickly onto the armchair clutching her teddy bear, giggling in sheer excitement. "
                    "Glossy Pixar 3D subsurface skin shaders, dynamic cinematic camera, vibrant warm studio lighting. "
                    "STRICTLY NO 2D drawings, NO flat sketches, NO line art outlines, NO speech bubbles, NO text."
                )
            },
            {
                "part": 2,
                "prompt": (
                    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
                    "Full 3D CGI animation. Seamless continuous scene. Beautiful 3D Indian mother Pinki (25, powder-blue traditional kurti) "
                    "steps out from kitchen holding a tray of snacks. Kaartik (yellow polo) screams frantically: 'Mummy rug mat chhoona, lava jal jayega!' "
                    "Pinki comically panics mid-step, jumping onto one foot on a small floor pillow, wobbling frantically like a funny cartoon flamingo "
                    "with wide comical shocked eyes, balancing the snack tray high in the air! "
                    "Ultra-detailed Pixar 3D character animation, comical slapstick physics, vibrant studio lighting. "
                    "STRICTLY NO 2D drawings, NO flat illustrations, NO speech bubbles, NO text."
                )
            },
            {
                "part": 3,
                "prompt": (
                    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
                    "Full 3D CGI animation. Seamless continuous scene. Kaartik (yellow polo) tosses another soft sofa cushion onto the floor "
                    "like a stepping stone: 'Mummy cushion bridge pakdo!' Pinki safely hops across onto the large soft sofa cushions, "
                    "collapsing into pillows laughing uncontrollably, wrapping both Kaartik and cute Kaavya (pink frock) into a big joyful group cuddle "
                    "while sharing warm samosas. Adorable heartwarming family comedy climax, ultra-smooth fluid animation, glowing warm lighting. "
                    "STRICTLY NO 2D drawings, NO pencil outlines, NO speech bubbles, NO text."
                )
            }
        ]
    },
    {
        "id": "ep_14_bubble_wrap_blast",
        "title": "Mummy Ka Bubble Wrap Trap! 💥🤣 Ghar Me Phate Patakhe! #TheNaughtyDuo #shorts",
        "desc": (
            "Online shopping ke dabbe me se nikla bada sa Bubble Wrap! 💥📦\n"
            "Kaartik aur Kaavya ne hallway me bicha diya secret trap, aur Mummy ne jaise hi kadam rakha... patakhe phutne lage! 😂🤣\n"
            "Dekhiye Mummy ka ye super energetic reaction!\n\n"
            "Bubble wrap phodne me kinko sabse zyada maza aata hai? Comment me batana! 👇❤️\n\n"
            "Aise hi pyare 3D Hindi animated cartoons ke liye @TheNaughtyDuoOfficial ko SUBSCRIBE karein! 🔔\n\n"
            "#shorts #TheNaughtyDuo #bubblewrapfunny #funnycartoon #3danimation #kartikandkaavya #comedy #familycomedy #viralshorts"
        ),
        "tags": [
            "The Naughty Duo", "@TheNaughtyDuoOfficial", "bubble wrap funny cartoon",
            "kids prank on mom", "3d animation shorts", "hindi cartoon shorts",
            "kartik and kaavya", "viral shorts 2026", "relatable comedy shorts"
        ],
        "scenes": [
            {
                "part": 1,
                "prompt": (
                    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
                    "Full 3D CGI animation. Sunny colorful hallway of Indian apartment. Exactly ONE chubby 3D toddler boy Kaartik "
                    "(5 years old, bright yellow polo shirt, blue shorts, rounded cheeks) unrolls a long 6-foot transparent plastic bubble-wrap sheet "
                    "from an online delivery box across the floor with a mischievous grin. Beside him, cute toddler sister Kaavya (3.5, pink frock) "
                    "pops two bubbles with her tiny fingers giggling quietly behind the wall corner. "
                    "Rich Pixar 3D lighting, glossy plastic shaders, vibrant primary colors. "
                    "STRICTLY NO 2D drawings, NO flat sketches, NO line art, NO speech bubbles, NO text."
                )
            },
            {
                "part": 2,
                "prompt": (
                    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
                    "Full 3D CGI animation. Seamless continuous hallway scene. 3D Indian mother Pinki (25, powder-blue kurti) walks down the hallway "
                    "in soft house slippers. Her foot steps onto the bubble wrap: loud comical POP-POP-POP! Pinki jumps a foot into the air with comical "
                    "wide cartoon shock eyes and flailing arms: 'Arey baap re! Ghar me patakha kisne chalaya?!' "
                    "Kaartik and Kaavya peek from doorway holding hands over mouths laughing hysterically. "
                    "Exaggerated funny cartoon physics, crisp 3D CGI render, volumetric lighting. "
                    "STRICTLY NO 2D drawings, NO flat art, NO comic speech bubbles, NO text."
                )
            },
            {
                "part": 3,
                "prompt": (
                    "High-definition Pixar 3D animated comedy, 9:16 vertical orientation, 8 seconds. "
                    "Full 3D CGI animation. Seamless continuous scene. Kaartik and Kaavya jump out rolling with laughter! "
                    "Pinki realizes it's bubble wrap, bursts into a cheerful wide smile, and starts playfully tap-dancing on the bubble wrap "
                    "making rapid-fire popping sounds with both kids jumping and dancing beside her in pure family delight! "
                    "Warm delightful comedy climax, ultra-smooth character motion, bright cheerful colors. "
                    "STRICTLY NO 2D drawings, NO sketches, NO speech bubbles, NO text."
                )
            }
        ]
    }
]

def update_live_status(ep_id, title, account_str, scene_str, pct, stage_str):
    status_data = {
        "active_id": ep_id,
        "active_title": title,
        "active_account": account_str,
        "active_scene": scene_str,
        "percentage": pct,
        "parts_text": f"{pct}% Progress | Autopilot Running",
        "stage": stage_str,
        "target_platform": "YouTube Shorts (Auto-Publish)",
        "delay_reason": f"🟢 Running: {stage_str}"
    }
    try:
        STATUS_FILE.write_text(json.dumps(status_data, indent=2), encoding="utf-8")
    except Exception:
        pass

def extract_last_frame(input_video, output_image):
    cmd = [
        FFMPEG_BIN, "-y",
        "-sseof", "-0.1",
        "-i", str(input_video),
        "-update", "1",
        "-q:v", "1",
        str(output_image)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and output_image.exists()

def attach_anchor_frame(page, image_path):
    print(f"[*] Attaching Frame Anchor: {image_path.name}...", flush=True)
    plus_btn = page.locator("[aria-label*='Add ingredients' i]").last
    if plus_btn.count() == 0:
        plus_btn = page.locator("button:has-text('add')").last
    plus_btn.click()
    page.wait_for_timeout(1000)

    with page.expect_file_chooser() as fc_info:
        up_btn = page.locator("button:has-text('Upload media')").first
        if up_btn.count() == 0:
            up_btn = page.locator("div:has-text('Upload media')").first
        up_btn.click(force=True)

    fc = fc_info.value
    fc.set_files(str(image_path))
    page.wait_for_timeout(5000)

    add_to_prompt = page.locator("button:has-text('Add to prompt'), [role='button']:has-text('Add to prompt')").first
    if add_to_prompt.count() > 0:
        add_to_prompt.click(force=True)
        page.wait_for_timeout(1500)
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
        print(f"[✓ Anchor Attached]: {image_path.name}", flush=True)
        return True
    return False

def configure_tune(page):
    tune_btn = page.locator("button:has-text('tune'), [aria-label*='settings' i], [aria-label*='tune' i]").last
    if tune_btn.count() > 0 and tune_btn.is_visible():
        try:
            tune_btn.click()
            page.wait_for_timeout(1000)
            never_radio = page.locator("span:has-text('Never'), [role='radio']:has-text('Never'), div:has-text('Never')").last
            if never_radio.count() > 0:
                never_radio.click(force=True)
                page.wait_for_timeout(300)
            v_916 = page.locator("button:has-text('9:16'), [role='button']:has-text('9:16'), div:has-text('9:16')").last
            if v_916.count() > 0:
                v_916.click(force=True)
                page.wait_for_timeout(300)
            save_btn = page.locator("button:has-text('Save'), [role='button']:has-text('Save')").first
            if save_btn.count() > 0 and save_btn.is_visible():
                save_btn.click()
                page.wait_for_timeout(1000)
        except Exception:
            pass

def handle_approvals(page):
    for _ in range(3):
        target = page.locator("button:has-text('Always approve'), [role='button']:has-text('Always approve')")
        if target.count() > 0 and target.last.is_visible():
            target.last.click(force=True)
            page.wait_for_timeout(1000)
            return
        app_target = page.locator("button:has-text('Approve'), [role='button']:has-text('Approve')")
        if app_target.count() > 0 and app_target.last.is_visible():
            app_target.last.click(force=True)
            page.wait_for_timeout(1000)
            return
        time.sleep(1)

def download_video_clip(page, out_path):
    for _ in range(3):
        cards = page.locator("[aria-label*='Open video in editor' i], flow-grid-tile-container, video")
        if cards.count() > 0:
            cards.last.click(force=True)
            page.wait_for_timeout(2500)
            dl_btn = page.locator("button[aria-label*='Download' i], button:has-text('Download')").first
            if dl_btn.count() > 0 and dl_btn.is_visible():
                dl_btn.click(force=True)
                page.wait_for_timeout(1500)
                target_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p'), button:has-text('Original size')").first
                if target_720.count() > 0:
                    with page.expect_download(timeout=60000) as dl_info:
                        target_720.click(force=True)
                    dl = dl_info.value
                    dl.save_as(str(out_path))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(1000)
                    if out_path.exists() and out_path.stat().st_size > 1000000:
                        return True
        time.sleep(5)
    return False

def stitch_and_export(clips, output_path):
    concat_txt = BASE_DIR / "data" / "concat_temp.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")

    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000000

def upload_to_youtube_with_seo(video_file, title, description, tags):
    print(f"\n[*] Uploading {video_file.name} to YouTube Shorts...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BRAVE_DATA,
            executable_path=BRAVE_EXE,
            headless=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1600, "height": 1000})

        page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)

        skip = page.locator("text='SKIP TO YOUTUBE STUDIO'").first
        if skip.count() > 0 and skip.is_visible():
            skip.click()
            page.wait_for_timeout(3000)

        create_btn = page.locator("ytcp-button#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')").first
        if create_btn.count() > 0:
            create_btn.click()
            page.wait_for_timeout(1500)
            upload_option = page.get_by_text("Upload videos", exact=False).first
            if upload_option.count() > 0:
                upload_option.click()
            page.wait_for_timeout(2000)

        file_input = page.locator("input[type='file']").first
        if file_input.count() == 0:
            browser.close()
            return None

        file_input.set_input_files(str(video_file))
        page.wait_for_timeout(8000)

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
            page.wait_for_timeout(1000)

        # Title
        title_box = page.locator("#textbox[aria-label*='title' i], ytcp-mention-textbox#title-textarea div#textbox").first
        if title_box.count() > 0:
            title_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(title[:100])
            page.wait_for_timeout(500)

        # Description
        desc_box = page.locator("#description-textarea div#textbox, ytcp-mention-textbox#description-textarea div#textbox").first
        if desc_box.count() == 0:
            tbs = page.locator("#textbox")
            if tbs.count() >= 2:
                desc_box = tbs.nth(1)
        if desc_box.count() > 0:
            desc_box.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            desc_box.fill(description)
            page.wait_for_timeout(500)

        # Audience
        not_kids = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        if not_kids.count() > 0:
            not_kids.click()
            page.wait_for_timeout(500)

        # Show more for tags
        show_more = page.locator("#toggle-button, button:has-text('Show more')").first
        if show_more.count() > 0 and show_more.is_visible():
            show_more.click()
            page.wait_for_timeout(1000)

        tags_input = page.locator("#tags-container input, input[aria-label='Tags'], #text-input").first
        if tags_input.count() > 0:
            tags_input.click()
            for t in tags:
                page.keyboard.type(t)
                page.keyboard.press("Enter")
                time.sleep(0.05)

        for _ in range(3):
            next_btn = page.locator("ytcp-button#next-button, button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                page.wait_for_timeout(2500)

        pub_radio = page.locator("ytcp-uploads-dialog tp-yt-paper-radio-button[name='PUBLIC'], tp-yt-paper-radio-button[name='PUBLIC']").first
        if pub_radio.count() > 0:
            pub_radio.click(force=True)
            page.wait_for_timeout(1500)

        publish_btn = page.locator("ytcp-uploads-dialog ytcp-button#done-button, ytcp-uploads-dialog button:has-text('Publish'), ytcp-uploads-dialog #publish-button").first
        if publish_btn.count() > 0:
            publish_btn.click(force=True)
            page.wait_for_timeout(4000)

        pub_anyway = page.locator("button:has-text('Publish anyway'), ytcp-button:has-text('Publish anyway')").first
        if pub_anyway.count() > 0 and pub_anyway.is_visible():
            pub_anyway.click(force=True)
            page.wait_for_timeout(4000)

        browser.close()
        return video_link

def sync_published_log(ep_id, title, filepath, yt_url):
    entry = {
        "key": ep_id,
        "filename": filepath.name,
        "size_mb": round(filepath.stat().st_size / (1024 * 1024), 2),
        "youtube": yt_url,
        "youtube_title": title,
        "visual_style": "High-Definition Pixar 3D CGI (100% Chained)",
        "youtube_status": "LIVE",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        data = json.loads(UPLOAD_LOG.read_text(encoding="utf-8")) if UPLOAD_LOG.exists() else {"uploaded": []}
        data.setdefault("uploaded", []).append(entry)
        UPLOAD_LOG.write_text(json.dumps(data, indent=4), encoding="utf-8")
    except Exception as e:
        print(f"[!] Log sync warning: {e}")

def run_harvest_and_produce_loop():
    print("=" * 70, flush=True)
    print("  THE NAUGHTY DUO — CONTINUOUS 24/7 AUTO-HARVEST & PRODUCTION ENGINE", flush=True)
    print("  High-Definition 3D CGI | Strict Frame Chaining | Full SEO Auto-Upload", flush=True)
    print("=" * 70, flush=True)

    slot_cycle_idx = 0

    for ep in EPISODES_TO_PRODUCE:
        ep_id = ep["id"]
        title = ep["title"]
        desc = ep["desc"]
        tags = ep["tags"]
        scenes = ep["scenes"]

        master_out = OUTPUT_DIR / f"{ep_id}_master.mp4"
        if master_out.exists() and master_out.stat().st_size > 1000000:
            print(f"[✓] Episode {ep_id} already assembled on disk. Skipping generation.", flush=True)
            continue

        assigned_slot = ACTIVE_SLOTS[slot_cycle_idx % len(ACTIVE_SLOTS)]
        slot_cycle_idx += 1
        slot_num = assigned_slot["slot"]
        slot_email = assigned_slot["email"]

        print(f"\n" + "=" * 60, flush=True)
        print(f"  STARTING EPISODE: {ep_id} ON SLOT {slot_num} ({slot_email})", flush=True)
        print(f"=" * 60, flush=True)

        update_live_status(ep_id, title, f"/u/{slot_num}/ ({slot_email})", "Starting Scene 1 of 3", 10, "Initializing Google Flow Canvas")

        rendered_clips = []
        anchor_frame_path = None

        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=BRAVE_DATA,
                executable_path=BRAVE_EXE,
                headless=True,
                accept_downloads=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = ctx.new_page()
            page.goto(f"https://flow.google.com/u/{slot_num}/", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(3000)

            new_btn = page.locator("button:has-text('New project'), [aria-label*='New project' i]").first
            if new_btn.count() > 0 and new_btn.is_visible():
                new_btn.click()
                page.wait_for_timeout(4000)

            configure_tune(page)

            for sc_idx, sc in enumerate(scenes):
                p_num = sc["part"]
                p_prompt = sc["prompt"]
                p_out = RAW_CLIPS / f"{ep_id}_p{p_num}.mp4"
                p_last = RAW_CLIPS / f"{ep_id}_p{p_num}_last.png"

                pct = 20 + (sc_idx * 25)
                update_live_status(ep_id, title, f"/u/{slot_num}/ ({slot_email})", f"Generating Scene {p_num} of 3", pct, f"Rendering Scene {p_num} in Google Flow")

                if p_out.exists() and p_out.stat().st_size > 1000000:
                    print(f"[✓ Reusing Scene {p_num}]: {p_out.name}", flush=True)
                    rendered_clips.append(p_out)
                    anchor_frame_path = p_last
                    continue

                if anchor_frame_path and anchor_frame_path.exists():
                    attach_anchor_frame(page, anchor_frame_path)

                editor = page.locator("[contenteditable='true'], div.ProseMirror, textarea").first
                editor.click()
                editor.fill(p_prompt)
                page.wait_for_timeout(500)

                send_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Submit' i]").first
                if send_btn.count() > 0 and send_btn.is_visible():
                    send_btn.click()
                else:
                    page.keyboard.press("Enter")

                print(f"[🚀 SENT] Scene {p_num} prompt dispatched to Slot {slot_num}!", flush=True)
                page.wait_for_timeout(2000)
                handle_approvals(page)

                time.sleep(65)
                for _ in range(8):
                    handle_approvals(page)
                    time.sleep(3)

                sc_ok = download_video_clip(page, p_out)
                if not sc_ok:
                    time.sleep(15)
                    sc_ok = download_video_clip(page, p_out)

                if sc_ok:
                    print(f"[✓ Scene {p_num} SAVED]: {p_out.name} ({p_out.stat().st_size} bytes)", flush=True)
                    rendered_clips.append(p_out)
                    extract_last_frame(p_out, p_last)
                    anchor_frame_path = p_last
                else:
                    print(f"[!] Scene {p_num} generation failed on Slot {slot_num}.", flush=True)
                    break

            ctx.close()

        if len(rendered_clips) == 3:
            update_live_status(ep_id, title, f"/u/{slot_num}/ ({slot_email})", "Stitching 3 Scenes", 85, "FFmpeg High-Definition Stitching")
            stitch_ok = stitch_and_export(rendered_clips, master_out)
            if stitch_ok:
                update_live_status(ep_id, title, f"/u/{slot_num}/ ({slot_email})", "Publishing to YouTube", 95, "Uploading with Full Viral SEO")
                yt_link = upload_to_youtube_with_seo(master_out, title, desc, tags)
                if yt_link:
                    print(f"\n[🎉 PUBLISHED SUCCESSFULLY]: {title} --> {yt_link}", flush=True)
                    sync_published_log(ep_id, title, master_out, yt_link)
                    update_live_status(ep_id, title, f"/u/{slot_num}/ ({slot_email})", "Completed & Live", 100, f"Published to YouTube Shorts: {yt_link}")
                else:
                    print("[!] Upload did not return link directly.", flush=True)
        else:
            print(f"[!] Skipping upload for {ep_id} as not all 3 clips were generated.", flush=True)

    print("\n[✓ ALL QUEUED HARVEST CYCLES COMPLETE]", flush=True)

if __name__ == "__main__":
    run_harvest_and_produce_loop()
