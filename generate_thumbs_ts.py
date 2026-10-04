import os
import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\color_adventure_thumbs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

folder = r"C:\Users\user\Downloads\For YouTube"
all_files = os.listdir(folder)

def find_file(ts):
    for f in all_files:
        if ts in f and f.endswith(".mp4"):
            return os.path.join(folder, f)
    return None

sequence = [
    ("01_portal", "20261003210753"),
    ("02_red_apple", "20261003211131"),
    ("03_blue_butterfly", "20261003211136"),
    ("04_yellow_sun", "20261003211804"),
    ("05_green_seed", "20261003211800"),
    ("06_orange_fruit", "20261003211809"),
    ("07_color_doors", "20261003212712"),
    ("08_match_colors", "20261003212718"),
    ("09_balloon_race", "20261003212723"),
    ("10_color_mixing", "20261003212730"),
    ("11_stepping_stones", "20261003213118"),
    ("12_memory_box", "20261003213331"),
    ("13_underwater", "20261003213340"),
]

for label, ts in sequence:
    p = find_file(ts)
    if p:
        out_jpg = OUT_DIR / f"{label}.jpg"
        cmd = [ffmpeg_exe, "-y", "-ss", "00:00:03", "-i", p, "-vframes", "1", "-q:v", "3", str(out_jpg)]
        subprocess.run(cmd, capture_output=True)
        print(f"Generated {label}: exists={out_jpg.exists()} ({os.path.basename(p)})")
    else:
        print(f"MISSING: {label} (ts={ts})")
