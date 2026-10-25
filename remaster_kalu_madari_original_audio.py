import os
import sys
import subprocess
from PIL import Image, ImageDraw, ImageFont

RAW_DIR = r"C:\TheNaughtyDuo_Automation\raw_clips"
OUT_DIR = r"C:\TheNaughtyDuo_Automation\output"
TRENDING_DIR = r"C:\TheNaughtyDuo_Automation\trending_sound"

c1 = os.path.join(RAW_DIR, "Children_meeting_bear_and_performer_20261025130004.mp4")
c2 = os.path.join(RAW_DIR, "Children_and_bear_dancing_20261025130015.mp4")
c3 = os.path.join(RAW_DIR, "Children_and_bear_spinning_together_20261025130028.mp4")
viral_sound = os.path.join(TRENDING_DIR, "monkeys_spinning_monkeys_viral.mp3")

out_video = os.path.join(OUT_DIR, "TheNaughtyDuo_KaluMadari_Master.mp4")
out_thumb = os.path.join(OUT_DIR, "kalu_madari_thumbnail.jpg")

print(f"[*] Reassembling Kalu Madari (Bhalu) Master Video...")
print(f"    - Clip 1: {c1}")
print(f"    - Clip 2: {c2}")
print(f"    - Clip 3: {c3}")
print(f"    - Viral Sound: {viral_sound} (Volume = 0.0)")
print(f"    - Original Raw Voice: 100% Volume (Separate external audio REMOVED)")

# Filter complex:
# Scale 3 video clips to 1080x1920, concat
# Concat 3 raw audio clips to 100% original volume
# Mix viral sound at volume 0.0 with normalize=0, weights=1 0
fc = (
    "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,setpts=PTS-STARTPTS[v0];"
    "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,setpts=PTS-STARTPTS[v1];"
    "[2:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,setpts=PTS-STARTPTS[v2];"
    "[v0][v1][v2]concat=n=3:v=1:a=0[outv];"
    "[0:a][1:a][2:a]concat=n=3:v=0:a=1[orig_raw_a];"
    "[orig_raw_a]volume=1.0,aformat=sample_rates=48000:channel_layouts=stereo[a_orig];"
    "[3:a]volume=0.0,aformat=sample_rates=48000:channel_layouts=stereo[a_viral];"
    "[a_orig][a_viral]amix=inputs=2:duration=first:normalize=0:weights=1 0[final_a]"
)

cmd = [
    r"C:\Users\user\scoop\apps\ffmpeg\current\bin\ffmpeg.exe",
    "-y",
    "-i", c1,
    "-i", c2,
    "-i", c3,
    "-i", viral_sound,
    "-filter_complex", fc,
    "-map", "[outv]",
    "-map", "[final_a]",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "192k",
    "-t", "30.00",
    "-movflags", "+faststart",
    out_video
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.exists(out_video):
    sz_mb = os.path.getsize(out_video) / (1024 * 1024)
    print(f"[OK] Kalu Madari Master Video reassembled successfully! Size: {sz_mb:.2f} MB")
else:
    print(f"[ERROR] Reassembly failed: {res.stderr}")
    sys.exit(1)

# Generate 3D High CTR Thumbnail
print("[*] Re-generating High-CTR 3D Thumbnail...")
temp_frame = os.path.join(OUT_DIR, "temp_kalu_thumb_frame.jpg")
cmd_frame = [
    r"C:\Users\user\scoop\apps\ffmpeg\current\bin\ffmpeg.exe",
    "-y", "-ss", "00:00:15", "-i", out_video, "-vframes", "1", "-q:v", "2", temp_frame
]
subprocess.run(cmd_frame, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if not os.path.exists(temp_frame):
    cmd_frame = [
        r"C:\Users\user\scoop\apps\ffmpeg\current\bin\ffmpeg.exe",
        "-y", "-ss", "00:00:10", "-i", out_video, "-vframes", "1", "-q:v", "2", temp_frame
    ]
    subprocess.run(cmd_frame, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

img = Image.open(temp_frame).convert("RGBA")
img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(img)

try:
    font_main = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 95)
    font_sub = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 85)
except Exception:
    font_main = ImageFont.load_default()
    font_sub = font_main

def draw_stroked(d, pos, text, font, fill_col, stroke_col, stroke_w=8):
    x, y = pos
    for dx in range(-stroke_w, stroke_w + 1):
        for dy in range(-stroke_w, stroke_w + 1):
            if dx*dx + dy*dy <= stroke_w*stroke_w:
                d.text((x + dx, y + dy), text, font=font, fill=stroke_col)
    d.text((x, y), text, font=font, fill=fill_col)

# Top & Bottom Text
t1 = "KALU MADARI AAYA!"
t2 = "BHALU KA DANCE! 🐻🥁"

bbox1 = draw.textbbox((0, 0), t1, font=font_main)
w1 = bbox1[2] - bbox1[0]
draw_stroked(draw, ((1080 - w1)//2, 160), t1, font_main, (255, 235, 59, 255), (0, 0, 0, 255), 8)

bbox2 = draw.textbbox((0, 0), t2, font=font_sub)
w2 = bbox2[2] - bbox2[0]
draw_stroked(draw, ((1080 - w2)//2, 1680), t2, font_sub, (255, 255, 255, 255), (0, 0, 0, 255), 8)

final_rgb = img.convert("RGB")
final_rgb.save(out_thumb, quality=95)
if os.path.exists(temp_frame):
    os.remove(temp_frame)

artifact_thumb = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\kalu_madari_thumbnail.jpg"
final_rgb.save(artifact_thumb, quality=95)
print(f"[OK] High CTR Thumbnail ready at {out_thumb} & artifact directory!")
