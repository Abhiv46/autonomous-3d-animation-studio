import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Set stdout encoding
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r"C:\TheNaughtyDuo_Automation\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
RAW_FRAMES_DIR = os.path.join(OUTPUT_DIR, "temp_code_frames")
os.makedirs(RAW_FRAMES_DIR, exist_ok=True)

FINAL_VIDEO = os.path.join(OUTPUT_DIR, "TheNaughtyDuo_Code_Demo_Short.mp4")
AUDIO_FILE = r"C:\TheNaughtyDuo_Automation\trending_sound\monkeys_spinning_monkeys_viral.mp3"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION_SEC = 8
TOTAL_FRAMES = FPS * DURATION_SEC

print(f"🎬 Starting Code-to-Video Engine: {TOTAL_FRAMES} frames @ {FPS}fps (1080x1920)...")

# Try to load Windows fonts
font_large = None
font_medium = None
font_small = None
font_paths = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\impact.ttf"
]
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font_large = ImageFont.truetype(fp, 88)
            font_title = ImageFont.truetype(fp, 105)
            font_medium = ImageFont.truetype(fp, 64)
            font_small = ImageFont.truetype(fp, 46)
            font_badge = ImageFont.truetype(fp, 38)
            break
        except Exception:
            pass

if not font_large:
    font_large = ImageFont.load_default()
    font_title = font_large
    font_medium = font_large
    font_small = font_large
    font_badge = font_large

# Load character image if exists
char_img_path = r"C:\TheNaughtyDuo_Automation\character_master_bible\Kaartik_Character_Sheet_Master.jpg"
char_img = None
if os.path.exists(char_img_path):
    try:
        raw_char = Image.open(char_img_path).convert("RGBA")
        # Resize to circular badge
        char_size = 460
        raw_char = raw_char.resize((char_size, char_size), Image.Resampling.LANCZOS)
        # Create circular mask
        mask = Image.new("L", (char_size, char_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, char_size, char_size), fill=255)
        char_img = Image.new("RGBA", (char_size, char_size), (0, 0, 0, 0))
        char_img.paste(raw_char, (0, 0), mask=mask)
    except Exception as e:
        print(f"Char image note: {e}")

# Precompute floating particles
np.random.seed(42)
NUM_PARTICLES = 40
particles = []
for _ in range(NUM_PARTICLES):
    particles.append({
        'x': np.random.uniform(50, WIDTH - 50),
        'y': np.random.uniform(100, HEIGHT - 100),
        'speed_y': np.random.uniform(-4, -1),
        'radius': np.random.uniform(4, 14),
        'hue': np.random.uniform(0, 1),
        'phase': np.random.uniform(0, math.pi * 2)
    })

# Audio Equalizer bars
NUM_BARS = 24

def ease_out_back(x):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * math.pow(x - 1, 3) + c1 * math.pow(x - 1, 2)

def ease_out_elastic(x):
    c4 = (2 * math.pi) / 3
    if x <= 0: return 0
    if x >= 1: return 1
    return math.pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1

# Generate frames
for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS  # current time in seconds
    progress = frame_idx / TOTAL_FRAMES

    # 1. Background: Dynamic animated gradient (Sunset / Royal Purple)
    # Background color shifting with time
    shift = math.sin(t * 1.5) * 35
    top_color = (int(25 + shift * 0.3), int(15 + shift * 0.2), int(60 + shift * 0.5))
    bottom_color = (int(180 + shift * 0.8), int(45 + shift * 0.4), int(95 + shift * 0.6))

    # Fast vertical gradient array
    y_ratios = np.linspace(0, 1, HEIGHT)[:, None]
    r = (top_color[0] * (1 - y_ratios) + bottom_color[0] * y_ratios).astype(np.uint8)
    g = (top_color[1] * (1 - y_ratios) + bottom_color[1] * y_ratios).astype(np.uint8)
    b = (top_color[2] * (1 - y_ratios) + bottom_color[2] * y_ratios).astype(np.uint8)
    gradient_array = np.dstack([np.repeat(r, WIDTH, axis=1),
                                np.repeat(g, WIDTH, axis=1),
                                np.repeat(b, WIDTH, axis=1)])

    frame_img = Image.fromarray(gradient_array, mode="RGB")
    draw = ImageDraw.Draw(frame_img, "RGBA")

    # 2. Animated floating sparkles / particles
    for p in particles:
        py = (p['y'] + p['speed_y'] * frame_idx * 2) % HEIGHT
        px = p['x'] + math.sin(t * 2 + p['phase']) * 20
        sparkle = 0.5 + 0.5 * math.sin(t * 6 + p['phase'])
        alpha = int(120 + 135 * sparkle)
        r_p = int(p['radius'] * (0.8 + 0.4 * sparkle))
        draw.ellipse((px - r_p, py - r_p, px + r_p, py + r_p),
                     fill=(255, 235, 120, alpha),
                     outline=(255, 255, 255, int(alpha * 0.8)), width=2)

    # 3. Top Banner: "THE NAUGHTY DUO"
    top_banner_y = 180
    badge_w, badge_h = 620, 90
    bx1 = (WIDTH - badge_w) // 2
    bx2 = bx1 + badge_w
    draw.rounded_rectangle((bx1, top_banner_y, bx2, top_banner_y + badge_h),
                           radius=45, fill=(0, 0, 0, 160), outline=(255, 215, 0, 230), width=4)
    draw.text((WIDTH // 2, top_banner_y + badge_h // 2),
              "⭐ THE NAUGHTY DUO ⭐", font=font_badge,
              fill="#FFD700", stroke_width=2, stroke_fill="#000", anchor="mm")

    # 4. Center Character Badge with Animated Spring scale & Ring Glow
    center_y = 750
    if char_img:
        # Scale animation with bounce on entry
        entry_t = min(1.0, t / 1.0)
        scale_factor = ease_out_elastic(entry_t) * 0.95 + 0.05 * math.sin(t * 4)
        curr_size = int(460 * scale_factor)
        if curr_size > 20:
            resized_char = char_img.resize((curr_size, curr_size), Image.Resampling.BILINEAR)
            cx = (WIDTH - curr_size) // 2
            cy = center_y - curr_size // 2

            # Glowing rings
            glow_rad = (curr_size // 2) + int(18 + 8 * math.sin(t * 5))
            draw.ellipse((WIDTH // 2 - glow_rad, center_y - glow_rad,
                          WIDTH // 2 + glow_rad, center_y + glow_rad),
                         outline=(255, 215, 0, 220), width=8)
            glow_rad2 = glow_rad + 14
            draw.ellipse((WIDTH // 2 - glow_rad2, center_y - glow_rad2,
                          WIDTH // 2 + glow_rad2, center_y + glow_rad2),
                         outline=(255, 105, 180, 160), width=4)

            frame_img.paste(resized_char, (cx, cy), mask=resized_char)

    # 5. Scene-Based Animated Headings (Kinetic Typography)
    # Scene 1 (0s-2.5s): Hook
    # Scene 2 (2.5s-5.0s): Code Reveal
    # Scene 3 (5.0s-8.0s): CTA
    if t < 2.5:
        local_t = min(1.0, t / 0.5)
        offset_y = int((1 - ease_out_back(local_t)) * 150)
        main_text = "Kaartik & Kaavya! 💖"
        sub_text = "Masti aur Mazedaar Kahaaniyan"
        pulse = 1.0 + 0.04 * math.sin(t * 8)
        color = "#FFFFFF"
    elif t < 5.2:
        local_t = min(1.0, (t - 2.5) / 0.5)
        offset_y = int((1 - ease_out_back(local_t)) * 150)
        main_text = "Pure Code Se Bani Video! 💻🚀"
        sub_text = "Python + FFmpeg Programmatic Engine"
        pulse = 1.0 + 0.05 * math.sin((t - 2.5) * 8)
        color = "#FFD700"
    else:
        local_t = min(1.0, (t - 5.2) / 0.5)
        offset_y = int((1 - ease_out_back(local_t)) * 150)
        main_text = "Subscribe For Daily Shorts! 🔔"
        sub_text = "24/7 Live Stream Link In Description"
        pulse = 1.0 + 0.06 * math.sin((t - 5.2) * 10)
        color = "#00FFA3"

    text_y = 1120 + offset_y
    draw.text((WIDTH // 2, text_y), main_text, font=font_large,
              fill=color, stroke_width=8, stroke_fill="#000000", anchor="mm")
    draw.text((WIDTH // 2, text_y + 100), sub_text, font=font_medium,
              fill="#FFF099", stroke_width=4, stroke_fill="#000000", anchor="mm")

    # 6. Audio Waveform Equalizer (Jumping to beat)
    eq_base_y = 1460
    bar_w = 26
    spacing = 16
    total_eq_w = NUM_BARS * bar_w + (NUM_BARS - 1) * spacing
    start_eq_x = (WIDTH - total_eq_w) // 2

    for b_idx in range(NUM_BARS):
        # Fake rhythmic frequency height
        freq = math.sin(t * 12 + b_idx * 0.45) * 0.5 + 0.5
        freq2 = math.cos(t * 8 - b_idx * 0.3) * 0.3 + 0.3
        bar_h = int(25 + 140 * (freq * 0.7 + freq2 * 0.3))
        bx = start_eq_x + b_idx * (bar_w + spacing)
        # Equalizer gradient color
        eq_color = (
            int(255 * (b_idx / NUM_BARS)),
            int(220 * (1 - b_idx / NUM_BARS) + 35),
            220,
            240
        )
        draw.rounded_rectangle((bx, eq_base_y - bar_h, bx + bar_w, eq_base_y),
                               radius=8, fill=eq_color, outline=(255, 255, 255, 180), width=2)

    # 7. Animated Subscribe Button (Bottom CTA)
    btn_y = 1620
    btn_w = 520
    btn_h = 110
    btn_x1 = (WIDTH - btn_w) // 2
    btn_x2 = btn_x1 + btn_w
    btn_scale = 1.0 + 0.04 * math.sin(t * 7)
    draw.rounded_rectangle((btn_x1, btn_y, btn_x2, btn_y + btn_h),
                           radius=55, fill=(230, 20, 50, 240), outline=(255, 255, 255, 255), width=5)
    draw.text((WIDTH // 2, btn_y + btn_h // 2), "SUBSCRIBE ▶", font=font_large,
              fill="#FFFFFF", stroke_width=4, stroke_fill="#000000", anchor="mm")

    # 8. Bottom Scrub Progress Bar
    prog_w = int(WIDTH * progress)
    draw.rectangle((0, HEIGHT - 16, WIDTH, HEIGHT), fill=(40, 40, 40, 200))
    draw.rectangle((0, HEIGHT - 16, prog_w, HEIGHT), fill=(255, 215, 0, 255))

    # Save frame
    frame_path = os.path.join(RAW_FRAMES_DIR, f"frame_{frame_idx:05d}.jpg")
    frame_img.save(frame_path, "JPEG", quality=90)

    if frame_idx % 30 == 0:
        print(f"  Frame {frame_idx}/{TOTAL_FRAMES} rendered ({int(progress * 100)}%)...")

print("✅ All frames rendered! Assembling final video with FFmpeg + Music...")

# FFmpeg assembly command
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(RAW_FRAMES_DIR, "frame_%05d.jpg"),
    "-ss", "00:00:02",
    "-i", AUDIO_FILE,
    "-t", str(DURATION_SEC),
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "19",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    FINAL_VIDEO
]

result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if result.returncode == 0:
    print(f"🎉 SUCCESS! Final Video Rendered: {FINAL_VIDEO}")
    file_size_mb = os.path.getsize(FINAL_VIDEO) / (1024 * 1024)
    print(f"📊 Video Size: {file_size_mb:.2f} MB | Resolution: 1080x1920 | FPS: {FPS} | Duration: {DURATION_SEC}s")
else:
    print(f"❌ FFmpeg Error:\n{result.stderr}")
