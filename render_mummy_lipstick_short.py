import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\TheNaughtyDuo_Automation"
EP_DIR = os.path.join(BASE_DIR, "episodes", "ep_mummy_lipstick")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEMP_FRAMES_DIR = os.path.join(EP_DIR, "temp_render_frames")
os.makedirs(TEMP_FRAMES_DIR, exist_ok=True)

MASTER_AUDIO = os.path.join(EP_DIR, "mummy_lipstick_master_audio_30s.mp3")
TRENDING_AUDIO = os.path.join(BASE_DIR, "trending_sound", "monkeys_spinning_monkeys_viral.mp3")
FINAL_SHORT = os.path.join(OUTPUT_DIR, "TheNaughtyDuo_MummyLipstick_Master.mp4")
FINAL_THUMB = os.path.join(OUTPUT_DIR, "TheNaughtyDuo_MummyLipstick_Thumb.jpg")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION_SEC = 30
TOTAL_FRAMES = FPS * DURATION_SEC  # 900 frames

print(f"🎬 Starting 3D Animated Short Production: {TOTAL_FRAMES} frames @ {FPS}fps (1080x1920)...")

# Load Noto Sans Devanagari Font
font_path = os.path.join(BASE_DIR, "RaviKiKahani", "fonts", "NotoSansDevanagari-Bold.ttf")
if not os.path.exists(font_path):
    font_path = r"C:\Windows\Fonts\arialbd.ttf"

font_title = ImageFont.truetype(font_path, 66)
font_sub = ImageFont.truetype(font_path, 42)
font_sub_large = ImageFont.truetype(font_path, 48)
font_badge = ImageFont.truetype(font_path, 52)
font_big_hook = ImageFont.truetype(font_path, 76)

# Load Character Sheets
char_bible = os.path.join(BASE_DIR, "character_master_bible")
kaartik_p = os.path.join(char_bible, "Kaartik_Character_Sheet_Master.jpg")
kaavya_p = os.path.join(char_bible, "Kaavya_Character_Sheet_Master.jpg")
mummy_p = os.path.join(char_bible, "mummy_face_anchor.jpg")
family_p = os.path.join(char_bible, "master_ref_1_bedtime_love.jpg")

def load_circular_badge(path, size):
    if not os.path.exists(path):
        return None
    raw = Image.open(path).convert("RGBA")
    raw = raw.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size, size), fill=255)
    badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    badge.paste(raw, (0, 0), mask=mask)
    return badge

badge_kaartik = load_circular_badge(kaartik_p, 480)
badge_kaavya = load_circular_badge(kaavya_p, 480)
badge_mummy = load_circular_badge(mummy_p, 480)

# Precompute floating sparkles and hearts
np.random.seed(99)
sparkles = [{'x': np.random.randint(60, WIDTH - 60), 'y': np.random.randint(150, HEIGHT - 350), 'rad': np.random.randint(6, 18), 'phase': np.random.uniform(0, 6.28)} for _ in range(35)]
hearts = [{'x': np.random.randint(80, WIDTH - 80), 'y': np.random.randint(200, HEIGHT - 400), 'size': np.random.randint(24, 50), 'speed': np.random.uniform(2, 5), 'phase': np.random.uniform(0, 6.28)} for _ in range(25)]

# Gradient generator
def make_gradient(top_c, bot_c):
    y = np.linspace(0, 1, HEIGHT)[:, None]
    r = (top_c[0] * (1 - y) + bot_c[0] * y).astype(np.uint8)
    g = (top_c[1] * (1 - y) + bot_c[1] * y).astype(np.uint8)
    b = (top_c[2] * (1 - y) + bot_c[2] * y).astype(np.uint8)
    return np.dstack([np.repeat(r, WIDTH, axis=1), np.repeat(g, WIDTH, axis=1), np.repeat(b, WIDTH, axis=1)])

bg_scene1 = make_gradient((255, 182, 193), (255, 105, 180))  # Baby pink room
bg_scene2 = make_gradient((255, 239, 213), (255, 160, 122))  # Playful warm peach
bg_scene3 = make_gradient((176, 224, 230), (221, 160, 221))  # Ornate mirror pastel
bg_scene4 = make_gradient((255, 228, 225), (255, 105, 180))  # Loving rose
bg_scene5 = make_gradient((255, 215, 0), (255, 69, 0))        # Golden celebration

def draw_subtitle_pill(draw, text, color="#FFD700"):
    box_w = 980
    box_h = 110
    bx1 = (WIDTH - box_w) // 2
    by1 = HEIGHT - 240
    draw.rounded_rectangle((bx1, by1, bx1 + box_w, by1 + box_h),
                           radius=35, fill=(0, 0, 0, 230), outline=(255, 215, 0, 255), width=5)
    draw.text((WIDTH // 2, by1 + box_h // 2), text, font=font_sub_large,
              fill=color, stroke_width=2, stroke_fill="#000", anchor="mm")

# Render loop
for f in range(TOTAL_FRAMES):
    t = f / FPS

    if f < 120:
        # Scene 1 (0–4s): Kaavya discovers Mummy's lipstick
        frame_img = Image.fromarray(bg_scene1)
        draw = ImageDraw.Draw(frame_img, "RGBA")

        # Top Badge
        draw.rounded_rectangle((200, 100, 880, 210), radius=50, fill=(0, 0, 0, 190), outline=(255, 215, 0, 255), width=4)
        draw.text((WIDTH // 2, 155), "💄 मम्मी की लाल लिपस्टिक! 💄", font=font_badge, fill="#FFD700", anchor="mm")

        # Dressing Table Mirror
        draw.ellipse((240, 320, 840, 920), fill=(255, 255, 255, 180), outline=(218, 165, 32, 255), width=16)
        draw.ellipse((270, 350, 810, 890), fill=(240, 248, 255, 140))

        # Kaavya Character Badge bouncing in
        bounce = 1.0 + 0.05 * math.sin(t * 8)
        k_size = int(480 * bounce)
        k_x = (WIDTH - k_size) // 2
        k_y = 960 - (k_size // 2)
        if badge_kaavya:
            resized_k = badge_kaavya.resize((k_size, k_size), Image.Resampling.BILINEAR)
            # Glowing rim
            draw.ellipse((k_x - 12, k_y - 12, k_x + k_size + 12, k_y + k_size + 12), outline=(255, 20, 147, 240), width=10)
            frame_img.paste(resized_k, (k_x, k_y), mask=resized_k)

        # Huge Golden Lipstick Prop floating
        lip_y = 1260 + int(math.sin(t * 6) * 20)
        draw.rectangle((500, lip_y, 580, lip_y + 160), fill=(218, 165, 32, 255), outline=(184, 134, 11, 255), width=4) # gold tube
        draw.polygon([(515, lip_y), (565, lip_y), (555, lip_y - 80), (525, lip_y - 80)], fill=(220, 20, 60, 255)) # ruby lipstick
        # Sparkles around lipstick
        for sp in sparkles[:15]:
            draw.ellipse((sp['x'] - sp['rad'], sp['y'] - sp['rad'], sp['x'] + sp['rad'], sp['y'] + sp['rad']), fill=(255, 255, 255, 220))

        draw_subtitle_pill(draw, "अरे वाह! मम्मी की लाल लिपस्टिक मिल गई! हीहीही! 💄")

    elif f < 330:
        # Scene 2 (4–11s): Bindi & Mustache Mischief
        local_f = f - 120
        frame_img = Image.fromarray(bg_scene2)
        draw = ImageDraw.Draw(frame_img, "RGBA")

        # Top Badge
        draw.rounded_rectangle((220, 100, 860, 210), radius=50, fill=(0, 0, 0, 190), outline=(255, 20, 147, 255), width=4)
        draw.text((WIDTH // 2, 155), "🤣 शरारती भाई-बहन! 🤣", font=font_badge, fill="#FF69B4", anchor="mm")

        # Kaartik (Left) and Kaavya (Right) Badges
        p_size = 400
        # Kaartik Left
        if badge_kaartik:
            b_k = badge_kaartik.resize((p_size, p_size))
            frame_img.paste(b_k, (100, 560), mask=b_k)
            # Big Red Bindi on Kaartik's forehead!
            draw.ellipse((270, 640, 330, 700), fill=(220, 20, 60, 255), outline=(255, 255, 255, 255), width=4)
            draw.ellipse((285, 655, 315, 685), fill=(255, 215, 0, 255)) # golden center

        # Kaavya Right
        if badge_kaavya:
            b_kv = badge_kaavya.resize((p_size, p_size))
            frame_img.paste(b_kv, (580, 560), mask=b_kv)
            # Funny Mustache drawn on Kaavya!
            draw.arc((720, 800, 800, 850), start=0, end=180, fill=(30, 30, 30, 255), width=10)
            draw.arc((800, 800, 880, 850), start=0, end=180, fill=(30, 30, 30, 255), width=10)

        # Animated lipstick trail connecting them
        trail_prog = min(1.0, (local_f % 90) / 90.0)
        curr_x = int(580 - trail_prog * 250)
        curr_y = int(680 + math.sin(trail_prog * math.pi) * 80)
        draw.ellipse((curr_x - 18, curr_y - 18, curr_x + 18, curr_y + 18), fill=(255, 20, 60, 255))
        draw.text((WIDTH // 2, 1080), "💄 BINDI & MOUSTACHE! 🎨", font=font_big_hook, fill="#D84315", stroke_width=6, stroke_fill="#FFF", anchor="mm")

        if local_f < 110:
            draw_subtitle_pill(draw, "काव्या: 'भैया रुको, मैं तुम्हारे माथे पर बड़ी बिंदी लगाती हूँ!'")
        else:
            draw_subtitle_pill(draw, "कार्तिक: 'अरे काव्या रुको! हाहाहा, मैं तुम्हारी मूंछें बनाता हूँ!'")

    elif f < 570:
        # Scene 3 (11–19s): Mirror Fun & Uncontrollable Laughter
        local_f = f - 330
        frame_img = Image.fromarray(bg_scene3)
        draw = ImageDraw.Draw(frame_img, "RGBA")

        # Huge Ornate Mirror in center
        draw.ellipse((140, 280, 940, 1180), fill=(255, 255, 255, 200), outline=(255, 215, 0, 255), width=18)

        # Floating reflection with giggle vibration
        vib_x = int(math.sin(local_f * 0.8) * 12)
        vib_y = int(math.cos(local_f * 0.8) * 8)

        p_size = 360
        if badge_kaartik:
            bk = badge_kaartik.resize((p_size, p_size))
            frame_img.paste(bk, (240 + vib_x, 520 + vib_y), mask=bk)
            # Red Bindi & painted cheeks
            draw.ellipse((400 + vib_x, 580 + vib_y, 445 + vib_x, 625 + vib_y), fill=(220, 20, 60, 255))
            draw.ellipse((340 + vib_x, 700 + vib_y, 375 + vib_x, 735 + vib_y), fill=(255, 105, 180, 200))

        if badge_kaavya:
            bkv = badge_kaavya.resize((p_size, p_size))
            frame_img.paste(bkv, (520 + vib_x, 520 + vib_y), mask=bkv)
            # Funny Mustache
            draw.arc((650 + vib_x, 720 + vib_y, 710 + vib_x, 760 + vib_y), start=0, end=180, fill=(30, 30, 30, 255), width=8)
            draw.arc((710 + vib_x, 720 + vib_y, 770 + vib_x, 760 + vib_y), start=0, end=180, fill=(30, 30, 30, 255), width=8)

        # Laughter Emojis floating
        draw.text((WIDTH // 2, 1340), "🤣🤣 हाहाहाहा! 🤣🤣", font=font_big_hook, fill="#FF1744", stroke_width=8, stroke_fill="#FFF", anchor="mm")
        draw_subtitle_pill(draw, "हाहाहाहा! देखो आईने में, हम कैसे कार्टून लग रहे हैं! 🤣")

    elif f < 810:
        # Scene 4 (19–27s): Mummy Catches Them & Loving Hug
        local_f = f - 570
        frame_img = Image.fromarray(bg_scene4)
        draw = ImageDraw.Draw(frame_img, "RGBA")

        # Top Badge
        draw.rounded_rectangle((220, 100, 860, 210), radius=50, fill=(0, 0, 0, 190), outline=(255, 215, 0, 255), width=4)
        draw.text((WIDTH // 2, 155), "❤️ मम्मी का प्यार! ❤️", font=font_badge, fill="#FFD700", anchor="mm")

        # Mummy in Center Top
        m_size = 460
        m_x = (WIDTH - m_size) // 2
        m_y = 380
        if badge_mummy:
            bm = badge_mummy.resize((m_size, m_size))
            draw.ellipse((m_x - 10, m_y - 10, m_x + m_size + 10, m_y + m_size + 10), outline=(255, 105, 180, 255), width=10)
            frame_img.paste(bm, (m_x, m_y), mask=bm)

        # Kaartik & Kaavya hugging Mummy from both sides
        ch_size = 340
        if badge_kaartik:
            bk = badge_kaartik.resize((ch_size, ch_size))
            frame_img.paste(bk, (120, 880), mask=bk)
        if badge_kaavya:
            bkv = badge_kaavya.resize((ch_size, ch_size))
            frame_img.paste(bkv, (620, 880), mask=bkv)

        # Floating Hearts
        for h in hearts[:18]:
            hy = (h['y'] - int(local_f * 3)) % 1400 + 200
            hx = h['x'] + int(math.sin(local_f * 0.1 + h['phase']) * 15)
            draw.text((hx, hy), "💖", font=font_title)

        draw_subtitle_pill(draw, "मम्मी: 'अरे मेरे नटखट बच्चों! ये क्या कर दिया! इधर आओ दोनों! 🥰'")

    else:
        # Scene 5 (27–30s): Love You Mummy & Subscribe Pulse
        local_f = f - 810
        frame_img = Image.fromarray(bg_scene5)
        draw = ImageDraw.Draw(frame_img, "RGBA")

        # Large Loving Family Banner
        draw.text((WIDTH // 2, 280), "LOVE YOU MUMMY! ❤️", font=font_big_hook, fill="#FFFFFF", stroke_width=8, stroke_fill="#000", anchor="mm")
        draw.text((WIDTH // 2, 380), "The Naughty Duo Family", font=font_badge, fill="#FFE082", stroke_width=4, stroke_fill="#000", anchor="mm")

        # Center Hug
        center_s = 480
        cx = (WIDTH - center_s) // 2
        cy = 550
        if badge_mummy:
            bm = badge_mummy.resize((center_s, center_s))
            draw.ellipse((cx - 15, cy - 15, cx + center_s + 15, cy + center_s + 15), outline=(255, 255, 255, 255), width=12)
            frame_img.paste(bm, (cx, cy), mask=bm)

        # Pulsing Red Subscribe Button
        pulse = 1.0 + 0.08 * math.sin(local_f * 0.3)
        btn_w, btn_h = int(680 * pulse), int(130 * pulse)
        bx1 = (WIDTH - btn_w) // 2
        by1 = 1380 - (btn_h // 2)
        draw.rounded_rectangle((bx1, by1, bx1 + btn_w, by1 + btn_h), radius=65, fill=(229, 9, 20, 255), outline=(255, 255, 255, 255), width=8)
        draw.text((WIDTH // 2, by1 + btn_h // 2), "SUBSCRIBE ▶ 🔔", font=font_badge, fill="#FFFFFF", stroke_width=4, stroke_fill="#000", anchor="mm")

        # Floating Golden Sparkles
        for sp in sparkles:
            draw.ellipse((sp['x'] - 6, sp['y'] - 6, sp['x'] + 6, sp['y'] + 6), fill=(255, 255, 255, 240))

        draw_subtitle_pill(draw, "लव यू मम्मी! सब्सक्राइब करो रोज नई मस्ती के लिए! ❤️🔔")

    # Global Top Channel Identifier
    draw.rounded_rectangle((280, 20, 800, 90), radius=35, fill=(0, 0, 0, 200), outline=(255, 215, 0, 240), width=3)
    draw.text((WIDTH // 2, 55), "⭐ THE NAUGHTY DUO ⭐", font=font_sub, fill="#FFD700", anchor="mm")

    # Bottom Progress Line
    prog_w = int(WIDTH * (f / TOTAL_FRAMES))
    draw.rectangle((0, HEIGHT - 14, WIDTH, HEIGHT), fill=(40, 40, 40, 255))
    draw.rectangle((0, HEIGHT - 14, prog_w, HEIGHT), fill=(255, 20, 147, 255))

    # Save Frame
    frame_path = os.path.join(TEMP_FRAMES_DIR, f"frame_{f:05d}.jpg")
    frame_img.save(frame_path, "JPEG", quality=90)

    # Save High-CTR Peak Thumbnail at frame 420 (Scene 3 laughing face)
    if f == 420:
        thumb_img = frame_img.copy()
        t_draw = ImageDraw.Draw(thumb_img)
        # Bold Yellow Top Text in Safe-Zone (Y: 340)
        t_draw.text((WIDTH // 2, 340), "मम्मी की लिपस्टिक! 💄🤣", font=font_big_hook,
                    fill="#FFD700", stroke_width=10, stroke_fill="#000000", anchor="mm")
        thumb_img.save(FINAL_THUMB, "JPEG", quality=95)
        print(f"📸 3D High-CTR Thumbnail Captured: {FINAL_THUMB}")

    if f % 150 == 0:
        p = int((f / TOTAL_FRAMES) * 100)
        print(f"  Rendered {f}/{TOTAL_FRAMES} frames ({p}%)...")

print("✅ All 900 frames rendered! Assembling Dual-Audio Master Video...")

# Dual Audio FFmpeg assembly:
# Master Dialogue (100% Volume) + Trending Viral Track (0% Volume for Algorithm Indexing)
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(TEMP_FRAMES_DIR, "frame_%05d.jpg"),
    "-i", MASTER_AUDIO,
    "-i", TRENDING_AUDIO,
    "-filter_complex",
    "[1:a]volume=1.0[a_dialogue];[2:a]volume=0.0[a_viral];[a_dialogue][a_viral]amix=inputs=2:duration=first:normalize=0:weights=1 0[aout]",
    "-map", "0:v",
    "-map", "[aout]",
    "-t", str(DURATION_SEC),
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    FINAL_SHORT
]

result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if result.returncode == 0:
    size_mb = os.path.getsize(FINAL_SHORT) / (1024 * 1024)
    print(f"🎉 MASTER SHORT RENDERED: {FINAL_SHORT}")
    print(f"📊 Specs: {size_mb:.2f} MB | 1080x1920 | 30 FPS | 30s | Dual-Audio Compliant")
else:
    print(f"❌ FFmpeg Error:\n{result.stderr}")
