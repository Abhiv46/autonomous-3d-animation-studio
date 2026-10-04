import os
import subprocess
import json
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
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
    res = subprocess.run([ffmpeg_exe, "-i", p], capture_output=True, text=True)
    out = res.stderr
    v_lines = [l.strip() for l in out.split("\n") if "Video:" in l]
    d_lines = [l.strip() for l in out.split("\n") if "Duration:" in l]
    print(f"{label}:")
    print(f"  {d_lines[0] if d_lines else 'No duration'}")
    print(f"  {v_lines[0] if v_lines else 'No video stream'}")
