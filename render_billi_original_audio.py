import os
import sys
import subprocess

RAW_DIR = r"C:\TheNaughtyDuo_Automation\raw_clips"
OUT_DIR = r"C:\TheNaughtyDuo_Automation\output"
TRENDING_DIR = r"C:\TheNaughtyDuo_Automation\trending_sound"

c1 = os.path.join(RAW_DIR, "Children_finding_kitten_on_porch_20261025122712.mp4")
c2 = os.path.join(RAW_DIR, "Kitten_drinking_milk_and_children_20261025122723.mp4")
c3 = os.path.join(RAW_DIR, "Children_and_kitten_dancing_together_20261025122734.mp4")
viral_sound = os.path.join(TRENDING_DIR, "monkeys_spinning_monkeys_viral.mp3")

out_video = os.path.join(OUT_DIR, "TheNaughtyDuo_BilliMeow_Master.mp4")

print(f"[*] Rebuilding Billi Meow Master Video with 100% ORIGINAL RAW AUDIO...")
print(f"    - Clip 1: {c1}")
print(f"    - Clip 2: {c2}")
print(f"    - Clip 3: {c3}")
print(f"    - Viral Sound: {viral_sound} (Volume = 0.0)")
print(f"    - External TTS / Voiceover: COMPLETELY REMOVED")

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
if res.returncode == 0:
    size_mb = os.path.getsize(out_video) / (1024 * 1024)
    print(f"[SUCCESS] Billi Meow Master Rendered: {out_video} ({size_mb:.2f} MB)")
else:
    print(f"[ERROR] FFmpeg failed: {res.stderr}")
    sys.exit(1)
