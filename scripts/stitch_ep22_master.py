import subprocess
from pathlib import Path
import imageio_ffmpeg
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
RAW_CLIPS_DIR = BASE_DIR / "data" / "raw_clips"
OUTPUT_DIR = BASE_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

c1 = RAW_CLIPS_DIR / "ep22_scene1_real.mp4"
c2 = RAW_CLIPS_DIR / "ep22_scene2_real.mp4"
c3 = RAW_CLIPS_DIR / "ep22_scene3_real.mp4"

master_out = OUTPUT_DIR / "TheNaughtyDuo_EP22_OriginalAudio_Master.mp4"
concat_list = RAW_CLIPS_DIR / "ep22_concat.txt"

print("[*] Preparing concat list...")
with open(concat_list, "w", encoding="utf-8") as f:
    f.write(f"file '{c1.resolve()}'\n")
    f.write(f"file '{c2.resolve()}'\n")
    f.write(f"file '{c3.resolve()}'\n")

print(f"[*] Stitching 3 scenes with 1080x1920 upscale and 100% original audio...")
cmd = [
    FFMPEG, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_list),
    "-vf", "scale=1080:1920:flags=lanczos",
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "18",
    "-c:a", "copy",
    str(master_out)
]
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"[SUCCESS] Masterpiece Stitched: {master_out}")
    print(f"Size: {master_out.stat().st_size} bytes ({master_out.stat().st_size / (1024*1024):.2f} MB)")
else:
    print("Direct audio copy failed, re-encoding audio with aac...")
    cmd_fallback = [
        FFMPEG, "-y",
        "-i", str(c1),
        "-i", str(c2),
        "-i", str(c3),
        "-filter_complex", "[0:v]scale=1080:1920:flags=lanczos[v0];[1:v]scale=1080:1920:flags=lanczos[v1];[2:v]scale=1080:1920:flags=lanczos[v2];[v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[outv][outa]",
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(master_out)
    ]
    res2 = subprocess.run(cmd_fallback, capture_output=True, text=True)
    if res2.returncode == 0:
        print(f"[SUCCESS via filter] Masterpiece Stitched: {master_out}")
        print(f"Size: {master_out.stat().st_size} bytes ({master_out.stat().st_size / (1024*1024):.2f} MB)")
    else:
        print("Error:", res2.stderr)
        sys.exit(1)

# Extract proof frames from master: 2s (Scene 1), 10s (Scene 2), 18s (Scene 3)
print("[*] Extracting proof frames from stitched master...")
for ts, name in [(2, "ep22_proof_frame_scene1.png"), (10, "ep22_proof_frame_scene2.png"), (18, "ep22_proof_frame_scene3.png")]:
    out_img = SCREENSHOT_DIR / name
    cmd_f = [
        FFMPEG, "-y",
        "-ss", str(ts),
        "-i", str(master_out),
        "-vframes", "1",
        str(out_img)
    ]
    subprocess.run(cmd_f, capture_output=True)
    print(f"  Frame at {ts}s saved: {out_img}")

print("\n[ALL DONE] Episode 22 Masterpiece is 100% Ready!")
