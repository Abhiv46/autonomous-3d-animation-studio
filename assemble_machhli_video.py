import os
import sys
import subprocess
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

RAW_DIR = r"C:\TheNaughtyDuo_Automation\raw_clips"
OUT_DIR = r"C:\TheNaughtyDuo_Automation\output"
os.makedirs(OUT_DIR, exist_ok=True)

c1 = os.path.join(RAW_DIR, "Children_watching_glowing_fish_leap_20261025143958.mp4")
c2 = os.path.join(RAW_DIR, "Children_interacting_with_golden_fish_20261025144010.mp4")
c3 = os.path.join(RAW_DIR, "Children_feeding_fish_in_pond_20261025144054.mp4")

clips = [c1, c2, c3]
for c in clips:
    if not os.path.exists(c):
        print(f"[ERROR] Missing clip: {c}")
        sys.exit(1)

out_video = os.path.join(OUT_DIR, "TheNaughtyDuo_MachhliRani_Master.mp4")
out_thumb = os.path.join(OUT_DIR, "machhli_rani_thumbnail.jpg")

print(f"[*] Assembling 3 clips into Master Short: {out_video}")

# Video Concat + Audio Mix
# User Rule: Keep original video audio at 100% full volume (volume=1.0)
# Mix trending audio tag at volume=0.0
inputs = []
for c in clips:
    inputs.extend(["-i", c])

fc = ""
for i in range(3):
    fc += f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,setpts=PTS-STARTPTS[v{i}];"
for i in range(3):
    fc += f"[v{i}]"
fc += "concat=n=3:v=1:a=0[outv];"
# Concat original video audio at 100% full volume
fc += "[0:a][1:a][2:a]concat=n=3:v=0:a=1[raw_a];"
fc += "[raw_a]volume=1.0[final_a]"

cmd_v = ["ffmpeg", "-y"] + inputs + [
    "-filter_complex", fc,
    "-map", "[outv]", "-map", "[final_a]",
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-t", "30.00",
    "-movflags", "+faststart",
    out_video
]

res = subprocess.run(cmd_v, capture_output=True, text=True)
if res.returncode == 0 and os.path.exists(out_video):
    size_mb = os.path.getsize(out_video) / (1024 * 1024)
    print(f"[OK] Master Video created successfully! Size: {size_mb:.2f} MB")
else:
    print(f"[ERROR] Assembly failed: {res.stderr}")
    sys.exit(1)

# Generate Custom 3D High-CTR Thumbnail
print(f"[*] Generating Thumbnail: {out_thumb}")
temp_frame = os.path.join(OUT_DIR, "temp_machhli_frame.jpg")
cmd_frame = ["ffmpeg", "-y", "-ss", "00:00:08", "-i", out_video, "-vframes", "1", "-q:v", "2", temp_frame]
subprocess.run(cmd_frame, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if not os.path.exists(temp_frame):
    cmd_frame2 = ["ffmpeg", "-y", "-ss", "00:00:18", "-i", out_video, "-vframes", "1", "-q:v", "2", temp_frame]
    subprocess.run(cmd_frame2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

img = Image.open(temp_frame).convert("RGBA")
img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(img)

try:
    font_main = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 95)
    font_sub = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 85)
except Exception:
    font_main = ImageFont.load_default()
    font_sub = font_main

def draw_stroked_text(d, pos, text, font, fill_col, stroke_col, stroke_w=8):
    x, y = pos
    for dx in range(-stroke_w, stroke_w + 1):
        for dy in range(-stroke_w, stroke_w + 1):
            if dx*dx + dy*dy <= stroke_w*stroke_w:
                d.text((x + dx, y + dy), text, font=font, fill=stroke_col)
    d.text((x, y), text, font=font, fill=fill_col)

t1 = "MACHHLI JAL KI RANI HAI!"
t2 = "JEEVAN USKA PAANI HAI! 🐟🌊"

# Top Text (Bright Yellow)
bbox1 = draw.textbbox((0, 0), t1, font=font_main)
w1 = bbox1[2] - bbox1[0]
draw_stroked_text(draw, ((1080 - w1)//2, 160), t1, font_main, (255, 235, 59, 255), (0, 0, 0, 255), 8)

# Bottom Text (Clean White)
bbox2 = draw.textbbox((0, 0), t2, font=font_sub)
w2 = bbox2[2] - bbox2[0]
draw_stroked_text(draw, ((1080 - w2)//2, 1680), t2, font_sub, (255, 255, 255, 255), (0, 0, 0, 255), 8)

final_rgb = img.convert("RGB")
final_rgb.save(out_thumb, quality=95)
if os.path.exists(temp_frame):
    os.remove(temp_frame)

# Copy thumbnail to artifact dir for instant clickable preview
artifact_thumb = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\machhli_rani_thumbnail.jpg"
final_rgb.save(artifact_thumb, quality=95)
print(f"[OK] Thumbnail saved successfully: {out_thumb}")
