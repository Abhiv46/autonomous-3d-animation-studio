import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Set UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = r"C:\TheNaughtyDuo_Automation\RaviKiKahani"
OUT_DIR = os.path.join(PROJECT_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

TEMP_FRAMES_DIR = os.path.join(PROJECT_DIR, "temp_frames")
os.makedirs(TEMP_FRAMES_DIR, exist_ok=True)

FINAL_VIDEO = os.path.join(OUT_DIR, "video.mp4")
AUDIO_FILE = os.path.join(PROJECT_DIR, "final_audio_60s.mp3")

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION_SEC = 60
TOTAL_FRAMES = FPS * DURATION_SEC  # 1800 frames

print(f"🎬 Starting High-Performance Video Renderer: {TOTAL_FRAMES} frames @ {FPS}fps (1080x1920)...")

# Fonts
font_title = None
font_sub = None
font_hindi = None
font_badge = None

# Load Official Noto Sans Devanagari Font
noto_path = os.path.join(PROJECT_DIR, "fonts", "NotoSansDevanagari-Bold.ttf")
if os.path.exists(noto_path):
    font_hindi = ImageFont.truetype(noto_path, 44)
    font_hindi_large = ImageFont.truetype(noto_path, 58)
    font_title = ImageFont.truetype(noto_path, 66)
    font_sub = ImageFont.truetype(noto_path, 42)
    font_badge = ImageFont.truetype(noto_path, 50)
    print("✅ Loaded official NotoSansDevanagari-Bold font successfully!")
else:
    for fp in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]:
        if os.path.exists(fp):
            font_title = ImageFont.truetype(fp, 68)
            font_sub = ImageFont.truetype(fp, 44)
            font_badge = ImageFont.truetype(fp, 52)
            font_hindi = font_sub
            font_hindi_large = font_title
            break

# Helper function to draw Stick Man
def draw_stickman(draw, x, y, scale=1.0, walk_frame=0, arm_pose="walk", has_bag=False, has_seed=False, is_happy=False, color=(30, 30, 30, 255)):
    head_r = int(26 * scale)
    body_len = int(95 * scale)
    leg_len = int(90 * scale)
    arm_len = int(70 * scale)
    line_w = max(4, int(7 * scale))

    # Walking cycle: alternates legs every 15 frames (30 frames full cycle)
    cycle = (walk_frame % 30) / 30.0
    leg_angle = math.sin(cycle * math.pi * 2) * 28.0

    neck_y = y - body_len - int(head_r * 2)
    head_cy = neck_y - head_r
    hip_y = y - leg_len

    # Head
    draw.ellipse((x - head_r, head_cy - head_r, x + head_r, head_cy + head_r),
                 outline=color, width=line_w, fill=(255, 255, 255, 255))
    # Eyes
    eye_r = max(2, int(3 * scale))
    draw.ellipse((x - int(8*scale) - eye_r, head_cy - int(4*scale) - eye_r, x - int(8*scale) + eye_r, head_cy - int(4*scale) + eye_r), fill=color)
    draw.ellipse((x + int(8*scale) - eye_r, head_cy - int(4*scale) - eye_r, x + int(8*scale) + eye_r, head_cy - int(4*scale) + eye_r), fill=color)

    # Smile
    if is_happy:
        draw.arc((x - int(12*scale), head_cy, x + int(12*scale), head_cy + int(14*scale)),
                 start=0, end=180, fill=color, width=max(2, int(3*scale)))
    else:
        draw.line((x - int(8*scale), head_cy + int(10*scale), x + int(8*scale), head_cy + int(10*scale)),
                  fill=color, width=max(2, int(3*scale)))

    # Backpack
    if has_bag:
        bag_w, bag_h = int(24*scale), int(45*scale)
        draw.rounded_rectangle((x - int(30*scale), neck_y + int(15*scale), x - int(30*scale) + bag_w, neck_y + int(15*scale) + bag_h),
                               radius=int(6*scale), fill=(230, 81, 0, 255), outline=(191, 54, 12, 255), width=max(2, int(3*scale)))

    # Spine Body
    draw.line((x, neck_y, x, hip_y), fill=color, width=line_w)

    # Arms
    shoulder_y = neck_y + int(18 * scale)
    if arm_pose == "walk":
        arm_ang = -leg_angle * 0.9
        rad1 = math.radians(arm_ang)
        rad2 = math.radians(-arm_ang)
        arm1_x = x + math.sin(rad1) * arm_len
        arm1_y = shoulder_y + math.cos(rad1) * arm_len
        arm2_x = x + math.sin(rad2) * arm_len
        arm2_y = shoulder_y + math.cos(rad2) * arm_len
    elif arm_pose == "wonder":
        arm1_x = x - int(45 * scale)
        arm1_y = shoulder_y - int(30 * scale)
        arm2_x = x + int(45 * scale)
        arm2_y = shoulder_y - int(30 * scale)
    elif arm_pose == "receive":
        arm1_x = x + int(25 * scale)
        arm1_y = shoulder_y + int(15 * scale)
        arm2_x = x + int(55 * scale)
        arm2_y = shoulder_y + int(15 * scale)
    elif arm_pose == "teach":
        arm1_x = x - int(25 * scale)
        arm1_y = shoulder_y + int(30 * scale)
        arm2_x = x + int(65 * scale)
        arm2_y = shoulder_y - int(35 * scale)
    elif arm_pose == "cheer":
        arm1_x = x - int(50 * scale)
        arm1_y = shoulder_y - int(50 * scale)
        arm2_x = x + int(50 * scale)
        arm2_y = shoulder_y - int(50 * scale)
    else:  # down
        arm1_x = x - int(15 * scale)
        arm1_y = shoulder_y + arm_len
        arm2_x = x + int(15 * scale)
        arm2_y = shoulder_y + arm_len

    draw.line((x, shoulder_y, arm1_x, arm1_y), fill=color, width=line_w)
    draw.line((x, shoulder_y, arm2_x, arm2_y), fill=color, width=line_w)

    # Magic Seed
    if has_seed:
        seed_r = int(12 * scale)
        draw.ellipse((arm2_x - seed_r, arm2_y - seed_r, arm2_x + seed_r, arm2_y + seed_r),
                     fill=(255, 215, 0, 255), outline=(255, 143, 0, 255), width=3)

    # Legs
    rad_l1 = math.radians(leg_angle)
    rad_l2 = math.radians(-leg_angle)
    leg1_x = x + math.sin(rad_l1) * leg_len
    leg1_y = hip_y + math.cos(rad_l1) * leg_len
    leg2_x = x + math.sin(rad_l2) * leg_len
    leg2_y = hip_y + math.cos(rad_l2) * leg_len

    draw.line((x, hip_y, leg1_x, leg1_y), fill=color, width=line_w)
    draw.line((x, hip_y, leg2_x, leg2_y), fill=color, width=line_w)

# Precompute sparkles
np.random.seed(123)
sparkles = [{'x': np.random.randint(80, WIDTH - 80), 'y': np.random.randint(200, HEIGHT - 500), 'rad': np.random.randint(6, 16), 'phase': np.random.uniform(0, 6.28)} for _ in range(50)]

# Pre-generate gradient backgrounds for performance
def get_gradient(top_c, bot_c):
    y = np.linspace(0, 1, HEIGHT)[:, None]
    r = (top_c[0] * (1 - y) + bot_c[0] * y).astype(np.uint8)
    g = (top_c[1] * (1 - y) + bot_c[1] * y).astype(np.uint8)
    b = (top_c[2] * (1 - y) + bot_c[2] * y).astype(np.uint8)
    return np.dstack([np.repeat(r, WIDTH, axis=1), np.repeat(g, WIDTH, axis=1), np.repeat(b, WIDTH, axis=1)])

bg_day = get_gradient((135, 206, 235), (255, 255, 255))
bg_sunrise = get_gradient((255, 112, 67), (255, 224, 130))
bg_night = get_gradient((26, 35, 126), (48, 63, 159))
bg_golden = get_gradient((255, 249, 196), (255, 215, 0))
bg_school = get_gradient((232, 245, 233), (165, 214, 167))
bg_moral = get_gradient((26, 35, 126), (74, 20, 140))

# Subtitle helper
def draw_subtitles(draw, text):
    box_w = 980
    box_h = 100
    bx1 = (WIDTH - box_w) // 2
    by1 = HEIGHT - 220
    draw.rounded_rectangle((bx1, by1, bx1 + box_w, by1 + box_h),
                           radius=30, fill=(0, 0, 0, 220), outline=(255, 215, 0, 255), width=4)
    draw.text((WIDTH // 2, by1 + box_h // 2), text, font=font_hindi,
              fill="#FFFFFF", anchor="mm")

# Render Loop
for f in range(TOTAL_FRAMES):
    t = f / FPS
    # Determine Scene
    if f < 240:
        # Scene 1: Village Walk (0-8s)
        frame_img = Image.fromarray(bg_day)
        draw = ImageDraw.Draw(frame_img, "RGBA")
        # Sun
        draw.ellipse((140, 180, 280, 320), fill=(255, 215, 0, 255), outline=(255, 165, 0, 255), width=6)
        # Village Green Hill
        draw.chord((-100, 1100, 1200, 1700), start=180, end=360, fill=(102, 187, 106, 255))
        # Village Hut
        draw.polygon([(260, 1120), (120, 1220), (400, 1220)], fill=(141, 110, 99, 255), outline=(78, 52, 46, 255))
        draw.rectangle((160, 1220, 360, 1370), fill=(215, 204, 200, 255), outline=(78, 52, 46, 255), width=4)
        draw.rectangle((230, 1270, 290, 1370), fill=(93, 64, 55, 255))
        # Ground
        draw.rectangle((0, 1400, WIDTH, HEIGHT), fill=(224, 169, 109, 255))
        draw.line((0, 1400, WIDTH, 1400), fill=(129, 199, 132, 255), width=12)
        # Ravi Walking
        walk_x = 100 + int((f / 240) * 850)
        draw_stickman(draw, walk_x, 1400, scale=1.9, walk_frame=f, arm_pose="walk")
        draw_subtitles(draw, "एक छोटे से गाँव में रवि नाम का एक लड़का रहता था...")

    elif f < 480:
        # Scene 2: 5 KM Walk to School (8-16s)
        local_f = f - 240
        frame_img = Image.fromarray(bg_sunrise)
        draw = ImageDraw.Draw(frame_img, "RGBA")
        # Morning Sun
        draw.ellipse((440, 320, 640, 520), fill=(255, 245, 157, 255), outline=(255, 152, 0, 255), width=8)
        # Road
        draw.rectangle((0, 1380, WIDTH, HEIGHT), fill=(188, 170, 164, 255))
        draw.line((0, 1380, WIDTH, 1380), fill=(165, 214, 167, 255), width=10)
        # Milestone
        draw.rounded_rectangle((780, 1260, 920, 1380), radius=50, fill=(236, 239, 241, 255), outline=(55, 71, 79, 255), width=5)
        draw.text((850, 1290), "SCHOOL", font=font_sub, fill="#D32F2F", anchor="mm")
        draw.text((850, 1340), "5 KM", font=font_title, fill="#263238", anchor="mm")
        # 5 KM PAIDAL Badge
        pulse = 1.0 + 0.05 * math.sin(local_f * 0.2)
        bw, bh = int(620 * pulse), int(100 * pulse)
        bx = (WIDTH - bw) // 2
        draw.rounded_rectangle((bx, 580, bx + bw, 580 + bh), radius=35, fill=(216, 67, 21, 255), outline=(255, 255, 255, 255), width=5)
        draw.text((WIDTH // 2, 580 + bh // 2), "🏃‍♂️ 5 KM PAIDAL", font=font_badge, fill="#FFFFFF", anchor="mm")
        # Ravi with bag walking
        walk_x = 120 + int((local_f / 240) * 800)
        draw_stickman(draw, walk_x, 1380, scale=1.9, walk_frame=f, arm_pose="walk", has_bag=True)
        draw_subtitles(draw, "रोज़ सुबह वह 5 किलोमीटर पैदल स्कूल जाता था।")

    elif f < 780:
        # Scene 3: Glowing Magic Tree (16-26s)
        local_f = f - 480
        frame_img = Image.fromarray(bg_night)
        draw = ImageDraw.Draw(frame_img, "RGBA")
        draw.rectangle((0, 1420, WIDTH, HEIGHT), fill=(27, 94, 32, 255))
        # Glowing Tree
        glow = int(25 + 18 * math.sin(local_f * 0.15))
        tx, ty = 760, 920
        draw.ellipse((tx - 260 - glow, ty - 260 - glow, tx + 260 + glow, ty + 260 + glow), fill=(255, 215, 0, 70))
        draw.rectangle((tx - 40, ty + 80, tx + 40, 1420), fill=(93, 64, 55, 255))
        draw.ellipse((tx - 220, ty - 220, tx + 220, ty + 220), fill=(255, 215, 0, 255), outline=(255, 160, 0, 255), width=10)
        # Sparkles around tree
        for sp in sparkles[:25]:
            sx = tx + int(math.sin(local_f * 0.1 + sp['phase']) * 200)
            sy = ty + int(math.cos(local_f * 0.1 + sp['phase']) * 180)
            draw.ellipse((sx - sp['rad'], sy - sp['rad'], sx + sp['rad'], sy + sp['rad']), fill=(255, 255, 255, 240))
        # Ravi in wonder
        draw_stickman(draw, 340, 1420, scale=1.9, walk_frame=0, arm_pose="wonder")
        draw_subtitles(draw, "रास्ते में उसे एक पुराना, चमकता हुआ जादुई पेड़ मिला!")

    elif f < 1080:
        # Scene 4: Tree Speaks & Gives Seed (26-36s)
        local_f = f - 780
        frame_img = Image.fromarray(bg_night)
        draw = ImageDraw.Draw(frame_img, "RGBA")
        draw.rectangle((0, 1420, WIDTH, HEIGHT), fill=(46, 125, 50, 255))
        # Tree
        tx, ty = 800, 940
        draw.rectangle((tx - 40, ty + 80, tx + 40, 1420), fill=(93, 64, 55, 255))
        draw.ellipse((tx - 200, ty - 200, tx + 200, ty + 200), fill=(255, 215, 0, 255), outline=(255, 160, 0, 255), width=8)
        # Speech Bubble
        bubble_w, bubble_h = 580, 130
        draw.rounded_rectangle((320, 560, 320 + bubble_w, 560 + bubble_h), radius=35, fill=(255, 255, 255, 255), outline=(255, 160, 0, 255), width=6)
        draw.polygon([(460, 690), (510, 690), (490, 730)], fill=(255, 255, 255, 255))
        draw.text((320 + bubble_w // 2, 560 + bubble_h // 2), "रवि, ये जादुई बीज लो! 🌟", font=font_hindi_large, fill="#D84315", anchor="mm")
        # Floating seed to Ravi
        seed_x = int(700 - min(1.0, local_f / 150) * 380)
        seed_y = 1100 + int(math.sin(local_f * 0.2) * 15)
        draw.ellipse((seed_x - 18, seed_y - 18, seed_x + 18, seed_y + 18), fill=(255, 215, 0, 255), outline=(255, 143, 0, 255), width=4)
        # Ravi receiving
        draw_stickman(draw, 320, 1420, scale=1.9, walk_frame=0, arm_pose="receive", has_seed=(local_f > 150))
        draw_subtitles(draw, "पेड़ ने कहा — 'रवि, ये जादुई बीज लो और सपने पूरे करो!'")

    elif f < 1380:
        # Scene 5: Golden Tree Grows (36-46s)
        local_f = f - 1080
        frame_img = Image.fromarray(bg_golden)
        draw = ImageDraw.Draw(frame_img, "RGBA")
        draw.rectangle((0, 1420, WIDTH, HEIGHT), fill=(93, 64, 55, 255))
        # Growing Tree Scale
        grow = min(1.0, local_f / 200)
        curr_r = int(70 + grow * 210)
        tree_top_y = int(1420 - grow * 650)
        trunk_w = int(20 + grow * 70)
        trunk_y0 = min(1415, tree_top_y + curr_r // 2)
        trunk_y1 = 1420
        if trunk_y0 < trunk_y1:
            draw.rectangle((540 - trunk_w // 2, trunk_y0, 540 + trunk_w // 2, trunk_y1), fill=(255, 143, 0, 255))
        draw.ellipse((540 - curr_r, tree_top_y - curr_r // 2, 540 + curr_r, tree_top_y + curr_r * 1.5), fill=(255, 215, 0, 255), outline=(255, 255, 255, 255), width=8)
        # Explosion of Sparkles
        for sp in sparkles:
            sy = (sp['y'] - int(local_f * 3)) % 1300 + 100
            sx = sp['x']
            draw.ellipse((sx - sp['rad'], sy - sp['rad'], sx + sp['rad'], sy + sp['rad']), fill=(255, 255, 255, 220))
        # Ravi Happy
        draw_stickman(draw, 240, 1420, scale=1.9, walk_frame=0, arm_pose="wonder", is_happy=True)
        draw_subtitles(draw, "रवि ने बीज बोया... अगले दिन सोने का पेड़ उगा! ✨")

    elif f < 1620:
        # Scene 6: Teaching Village Kids (46-54s)
        local_f = f - 1380
        frame_img = Image.fromarray(bg_school)
        draw = ImageDraw.Draw(frame_img, "RGBA")
        draw.rectangle((0, 1380, WIDTH, HEIGHT), fill=(165, 214, 167, 255))
        # Blackboard
        draw.rounded_rectangle((360, 480, 840, 780), radius=20, fill=(27, 94, 32, 255), outline=(93, 64, 55, 255), width=10)
        draw.text((600, 560), "📖 क ख ग", font=font_title, fill="#FFFFFF", anchor="mm")
        draw.text((600, 680), "गांव की पाठशाला", font=font_hindi_large, fill="#FFD700", anchor="mm")
        # Ravi Teacher
        draw_stickman(draw, 260, 1380, scale=1.8, walk_frame=0, arm_pose="teach")
        # 3 Students
        draw_stickman(draw, 560, 1440, scale=1.3, walk_frame=0, arm_pose="down", is_happy=True)
        draw_stickman(draw, 730, 1440, scale=1.3, walk_frame=0, arm_pose="down", is_happy=True)
        draw_stickman(draw, 900, 1440, scale=1.3, walk_frame=0, arm_pose="down", is_happy=True)
        draw_subtitles(draw, "रवि ने उस पेड़ से गाँव के सब बच्चों को पढ़ाया! 📚")

    else:
        # Scene 7: Moral & Follow Karo Pulse (54-60s)
        local_f = f - 1620
        frame_img = Image.fromarray(bg_moral)
        draw = ImageDraw.Draw(frame_img, "RGBA")
        # Moral Title
        draw.text((WIDTH // 2, 340), "MORAL OF THE STORY", font=font_sub, fill="#FFD700", anchor="mm")
        draw.text((WIDTH // 2, 450), "मेहनत कभी बेकार नहीं जाती!", font=font_hindi_large, fill="#FFFFFF", stroke_width=6, stroke_fill="#000", anchor="mm")
        # Celebratory Confetti
        for sp in sparkles:
            cy = (sp['y'] + int(local_f * 8)) % HEIGHT
            draw.ellipse((sp['x'] - 8, cy - 8, sp['x'] + 8, cy + 8), fill=(255, 215, 0, 220))
        # Ravi Cheering
        draw_stickman(draw, 540, 1280, scale=2.3, walk_frame=0, arm_pose="cheer", is_happy=True)
        # FOLLOW KARO Pulsing Button
        pulse = 1.0 + 0.08 * math.sin(local_f * 0.3)
        btn_w, btn_h = int(640 * pulse), int(120 * pulse)
        bx1 = (WIDTH - btn_w) // 2
        by1 = 1460 - (btn_h // 2)
        draw.rounded_rectangle((bx1, by1, bx1 + btn_w, by1 + btn_h), radius=60, fill=(229, 9, 20, 255), outline=(255, 255, 255, 255), width=6)
        draw.text((WIDTH // 2, by1 + btn_h // 2), "💖 FOLLOW KARO 🔔", font=font_badge, fill="#FFFFFF", anchor="mm")
        draw_subtitles(draw, "Moral: मेहनत कभी बेकार नहीं जाती! Follow Karo 💖")

    # Global Top Channel Title
    draw.rounded_rectangle((280, 80, 800, 160), radius=40, fill=(0, 0, 0, 200), outline=(255, 215, 0, 240), width=4)
    draw.text((WIDTH // 2, 120), "✨ रवि की कहानी ✨", font=font_hindi, fill="#FFD700", anchor="mm")

    # Progress Bar at bottom
    prog_w = int(WIDTH * (f / TOTAL_FRAMES))
    draw.rectangle((0, HEIGHT - 14, WIDTH, HEIGHT), fill=(40, 40, 40, 255))
    draw.rectangle((0, HEIGHT - 14, prog_w, HEIGHT), fill=(255, 215, 0, 255))

    # Save Frame
    frame_path = os.path.join(TEMP_FRAMES_DIR, f"frame_{f:05d}.jpg")
    frame_img.save(frame_path, "JPEG", quality=88)

    if f % 150 == 0:
        percent = int((f / TOTAL_FRAMES) * 100)
        print(f"  Progress: {f}/{TOTAL_FRAMES} frames ({percent}%)...")

print("✅ All 1800 frames rendered! Assembling final video with FFmpeg + 60s Voiceover...")

# FFmpeg Final Encode Command
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(TEMP_FRAMES_DIR, "frame_%05d.jpg"),
    "-i", AUDIO_FILE,
    "-t", str(DURATION_SEC),
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    FINAL_VIDEO
]

result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if result.returncode == 0:
    file_size_mb = os.path.getsize(FINAL_VIDEO) / (1024 * 1024)
    print(f"🎉 SUCCESS! Final Video Rendered: {FINAL_VIDEO}")
    print(f"📊 Specs: {file_size_mb:.2f} MB | Resolution: {WIDTH}x{HEIGHT} | FPS: {FPS} | Duration: {DURATION_SEC}s")
else:
    print(f"❌ FFmpeg Error:\n{result.stderr}")
