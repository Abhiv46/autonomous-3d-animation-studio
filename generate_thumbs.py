import os
import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = Path(r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\color_adventure_thumbs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

folder = r"C:\Users\user\Downloads\For YouTube"

ordered_files = [
    ("01_portal", os.path.join(folder, "Children_discovering_magical_rai._1080p_20261003210753.mp4")),
    ("02_red_apple", os.path.join(folder, "Children_discover_glowing_red_apple_20261003211131.mp4")),
    ("03_blue_butterfly", os.path.join(folder, "Children_chasing_blue_butterfly_._20261003211136.mp4")),
    ("04_yellow_sun", os.path.join(folder, "Children_discover_giant_golden_b._20261003211804.mp4")),
    ("05_green_seed", os.path.join(folder, "Children_planting_glowing_green_._20261003211800.mp4")),
    ("06_orange_fruit", os.path.join(folder, "Children_picking_fruit_in_orchard_20261003211809.mp4")),
    ("07_color_doors", os.path.join(folder, "Children_choose_magical_colored_._20261003212712.mp4")),
    ("08_match_colors", os.path.join(folder, "Kaavya_solves_color_matching_puzzle_20261003212718.mp4")),
    ("09_balloon_race", os.path.join(folder, "Children_following_balloons_in_m._20261003212723.mp4")),
    ("10_color_mixing", os.path.join(folder, "Children_mixing_paint_colors_ani._20261003212730.mp4")),
    ("11_stepping_stones", os.path.join(folder, "Children_navigating_magical_gree._20261003213118.mp4")),
    ("12_memory_box", os.path.join(folder, "Boy_taps_red_magic_box_20261003213331.mp4")),
    ("13_underwater", os.path.join(folder, "Children_entering_underwater_world_20261003213340.mp4")),
]

for label, path in ordered_files:
    if os.path.exists(path):
        out_jpg = OUT_DIR / f"{label}.jpg"
        cmd = [ffmpeg_exe, "-y", "-ss", "00:00:03", "-i", path, "-vframes", "1", "-q:v", "3", str(out_jpg)]
        subprocess.run(cmd, capture_output=True)
        print(f"Generated thumb for {label}: exists={out_jpg.exists()}")
    else:
        print(f"NOT FOUND: {path}")
