import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path
import asyncio

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Paths
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
PARENT_DIR = Path(r"C:\TheNaughtyDuo_Automation")
CATALOG_PATH = PARENT_DIR / "stories_catalog.json"
CHANNEL_HISTORY_PATH = PARENT_DIR / "channel_existing_videos.json"
STATE_PATH = BASE_DIR / "factory_state.json"
RAW_CLIPS_DIR = BASE_DIR / "data" / "raw_clips"
PROCESSED_DIR = BASE_DIR / "data" / "processed_episodes"
FFMPEG_EXE = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

RAW_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "factory_engine.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("FactoryEngine")

# All 8 Google Accounts
ACCOUNTS = [
    {"slot": 0, "email": "abhiv46@gmail.com"},
    {"slot": 1, "email": "rkumar.pub@gmail.com"},
    {"slot": 2, "email": "pinku.pub@gmail.com"},
    {"slot": 3, "email": "infolillylooks@gmail.com"},
    {"slot": 4, "email": "elegantdriveways4u@gmail.com"},
    {"slot": 5, "email": "abhiv446@gmail.com"},
    {"slot": 6, "email": "rkumar.ukb@gmail.com"},
    {"slot": 7, "email": "techwire9999@gmail.com"},
]

from direct_cdp import DirectCDPClient, get_browser_ws

def load_state():
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"current_slot": 0, "completed_episodes": []}

def save_state(state):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving state: {e}")

def load_catalog():
    if CATALOG_PATH.exists():
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading catalog: {e}")
    return []

def get_existing_channel_titles():
    titles = set()
    if CHANNEL_HISTORY_PATH.exists():
        try:
            with open(CHANNEL_HISTORY_PATH, "r", encoding="utf-8") as f:
                ch_data = json.load(f)
                for item in ch_data:
                    t = item.get("title", "").strip().lower()
                    if t:
                        titles.add(t)
        except Exception:
            pass
    return titles

def get_next_story():
    catalog = load_catalog()
    state = load_state()
    completed = set(state.get("completed_episodes", []))
    existing_titles = get_existing_channel_titles()
    
    # Exclude legacy completed IDs
    excluded_legacy = {
        "ep_01", "ep_02", "ep_03", "ep_04", "ep_05", "ep_06", "ep_07", "ep_08", "ep_09", "ep_10",
        "ep_11_shaving_foam_santa", "ep_12_balloon_monster", "ep_13_floor_is_lava", "ep_14_bubble_wrap_blast",
        "ep_15_fake_moustache_cop", "ep_16_papa_big_shoes", "ep_17_roohafza_pink_rabbit",
        "ep_06_toy_mouse", "ep_07_spicy_golgappa", "ep_08_super_magnet", "ep_09_remote_fight",
        "ep_10_invisible_prank", "ep_21", "ep21_highheels"
    }
    completed.update(excluded_legacy)
            
    for story in catalog:
        s_id = story.get("id")
        s_title = story.get("title", "").strip().lower()
        
        # 1. Check if ID marked completed in state
        if s_id in completed:
            continue
            
        # 2. Check if Master video already exists on disk
        master_file = PROCESSED_DIR / f"TheNaughtyDuo_{s_id}_OriginalAudio_Master.mp4"
        if master_file.exists() and master_file.stat().st_size > 1000000:
            logger.info(f"Skipping {s_id}: Master video already produced on disk ({master_file.name})")
            completed.add(s_id)
            state["completed_episodes"] = list(completed)
            save_state(state)
            continue
            
        # 3. Check if Title already published on YouTube/TikTok
        if any(s_title[:30] in t for t in existing_titles):
            logger.info(f"Skipping {s_id}: Title already exists in channel history: '{story.get('title')}'")
            completed.add(s_id)
            state["completed_episodes"] = list(completed)
            save_state(state)
            continue
            
        return story
    return None

def stitch_master_video(story_id: str, p1_path: Path, p2_path: Path, p3_path: Path) -> Path:
    master_path = PROCESSED_DIR / f"TheNaughtyDuo_{story_id}_OriginalAudio_Master.mp4"
    concat_list_path = PROCESSED_DIR / f"{story_id}_concat_list.txt"
    
    with open(concat_list_path, "w", encoding="utf-8") as f:
        f.write(f"file '{p1_path.resolve().as_posix()}'\n")
        f.write(f"file '{p2_path.resolve().as_posix()}'\n")
        f.write(f"file '{p3_path.resolve().as_posix()}'\n")
        
    logger.info(f"Stitching master video for {story_id} with 100% ORIGINAL natural audio...")
    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_path),
        "-vf", "scale=1080:1920:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(master_path)
    ]
    subprocess.run(cmd, check=True)
    logger.info(f"[SUCCESS] Master video created: {master_path} ({os.path.getsize(master_path)} bytes)")
    return master_path

async def run_flow_generation(story, current_slot):
    ws_url = await get_browser_ws()
    client = DirectCDPClient(ws_url)
    await client.connect()
    try:
        targets = await client.get_targets()
        flow_target = None
        for t in targets:
            if t.get("type") == "page" and "flow.google.com" in t.get("url", ""):
                flow_target = t
                break
                
        if not flow_target:
            for t in targets:
                if t.get("type") == "page":
                    flow_target = t
                    break
                    
        session = await client.attach_to_target(flow_target["targetId"])
        logger.info(f"Connected to Flow session on Slot {current_slot} ({ACCOUNTS[current_slot]['email']})")
        
        # Check current URL
        cur_url = await session.eval("window.location.href")
        target_flow_url = f"https://flow.google.com/u/{current_slot}/"
        if f"/u/{current_slot}/" not in cur_url:
            logger.info(f"Navigating to {target_flow_url}")
            await session.navigate(target_flow_url)
            await asyncio.sleep(6)
            
        return session, client
    except Exception as e:
        await client.close()
        raise e

def main_loop():
    logger.info("=" * 70)
    logger.info("   THE NAUGHTY DUO - AUTONOMOUS CONTENT FACTORY (V2 PRO)")
    logger.info("=" * 70)
    logger.info("[*] Pure Pixar 3D Animation: ACTIVE (Zero CGI / Zero Semi-Realistic)")
    logger.info("[*] Cute Hindi Dialogues in All 3 Scenes: ACTIVE")
    logger.info("[*] Cute LIKE Request (CTA) in Scene 3: ACTIVE")
    logger.info("[*] 100% Original Flow Natural Audio: ACTIVE")
    logger.info("[*] 9:16 Vertical Full HD: ACTIVE")
    logger.info("[*] Multi-Account Credit Factory (Slots 0-7): ACTIVE")
    logger.info("[*] Auto-Publish to YouTube Shorts & TikTok: ACTIVE")
    logger.info("=" * 70)

    state = load_state()
    current_slot = state.get("current_slot", 0)
    
    story = get_next_story()
    if not story:
        logger.info("All episodes completed! Factory in standby mode.")
        return
        
    story_id = story["id"]
    story_title = story["title"]
    logger.info(f"\n>>> [NEXT TARGET] Episode: {story_id} - '{story_title}' <<<")
    logger.info(f"Active Google Account: Slot {current_slot} ({ACCOUNTS[current_slot]['email']})")

if __name__ == "__main__":
    main_loop()
