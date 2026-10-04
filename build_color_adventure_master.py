import os
import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

FOLDER = r"C:\Users\user\Downloads\For YouTube"
MUSIC_FILE = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\Carefree.mp3"
OUTPUT_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MASTER_OUTPUT = OUTPUT_DIR / "TheNaughtyDuo_YouTube_MagicColorAdventure_Master.mp4"

all_files = os.listdir(FOLDER)

def find_file(ts):
    for f in all_files:
        if ts in f and f.endswith(".mp4"):
            return os.path.join(FOLDER, f)
    return None

sequence = [
    ("01_portal", "20261003210753", 10.0),
    ("02_red_apple", "20261003211131", 10.0),
    ("03_blue_butterfly", "20261003211136", 10.0),
    ("04_yellow_sun", "20261003211804", 10.0),
    ("05_green_seed", "20261003211800", 10.0),
    ("06_orange_fruit", "20261003211809", 10.0),
    ("07_color_doors", "20261003212712", 8.0),
    ("08_match_colors", "20261003212718", 8.0),
    ("09_balloon_race", "20261003212723", 8.0),
    ("10_color_mixing", "20261003212730", 8.0),
    ("11_stepping_stones", "20261003213118", 8.0),
    ("12_memory_box", "20261003213331", 8.0),
    ("13_underwater", "20261003213340", 8.0),
]

clip_paths = []
for label, ts, dur in sequence:
    p = find_file(ts)
    if not p:
        raise FileNotFoundError(f"Missing clip {label} with timestamp {ts}")
    clip_paths.append((label, p, dur))

print(f"[1] Verified all {len(clip_paths)} clips exist!")

# Pre-process / normalize each clip: scale to 1080x1920, fps=24, ensure stereo audio at 48kHz
TEMP_DIR = OUTPUT_DIR / "temp_norm_clips"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

norm_clips = []
for i, (label, p, dur) in enumerate(clip_paths):
    out_norm = TEMP_DIR / f"norm_{i:02d}_{label}.mp4"
    print(f"  [*] Normalizing {label}...", flush=True)
    
    # Check if clip has audio
    probe_cmd = [ffmpeg_exe, "-i", p]
    pr = subprocess.run(probe_cmd, capture_output=True, text=True)
    has_audio = "Audio:" in pr.stderr
    
    if has_audio:
        vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24"
        cmd = [
            ffmpeg_exe, "-y",
            "-i", p,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            str(out_norm)
        ]
    else:
        # Generate silent audio track
        vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24"
        cmd = [
            ffmpeg_exe, "-y",
            "-i", p,
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            str(out_norm)
        ]
    subprocess.run(cmd, check=True, capture_output=True)
    norm_clips.append(str(out_norm))

print(f"[2] All {len(norm_clips)} clips normalized to 1080x1920 @ 24fps!")

# Create concat list
concat_list = TEMP_DIR / "concat_list.txt"
with open(concat_list, "w", encoding="utf-8") as f:
    for nc in norm_clips:
        escaped = nc.replace("\\", "/")
        f.write(f"file '{escaped}'\n")

# Concat video
temp_concat = TEMP_DIR / "temp_concat.mp4"
print(f"[3] Concatenating normalized clips...", flush=True)
cmd_concat = [
    ffmpeg_exe, "-y",
    "-f", "concat", "-safe", "0",
    "-i", str(concat_list),
    "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
    str(temp_concat)
]
subprocess.run(cmd_concat, check=True, capture_output=True)

# Probe duration of temp_concat
pr = subprocess.run([ffmpeg_exe, "-i", str(temp_concat)], capture_output=True, text=True)
total_dur = 116.0
for line in pr.stderr.split("\n"):
    if "Duration:" in line:
        parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
        total_dur = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
        break

print(f"[4] Total video duration: {total_dur:.2f} seconds")

# Mix with viral background music Carefree.mp3
print(f"[5] Mixing background nursery rhyme music (Carefree.mp3) with video audio...", flush=True)
fade_out_start = max(0, total_dur - 2.5)

# Audio filter:
# [1:a]aloop=loop=-1:size=2e+09,volume=0.45,afade=t=in:ss=0:d=1,afade=t=out:st={fade_out_start}:d=2.5[bg];
# [0:a]volume=1.0[orig];
# [orig][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]
afilt = (
    f"[1:a]aloop=loop=-1:size=2e+09,volume=0.50,afade=t=in:ss=0:d=1,afade=t=out:st={fade_out_start:.2f}:d=2.5[bg];"
    f"[0:a]volume=1.0[orig];"
    f"[orig][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
)

cmd_master = [
    ffmpeg_exe, "-y",
    "-i", str(temp_concat),
    "-i", MUSIC_FILE,
    "-filter_complex", afilt,
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
    "-t", f"{total_dur:.2f}",
    str(MASTER_OUTPUT)
]
subprocess.run(cmd_master, check=True, capture_output=True)

print(f"[SUCCESS] Master video created: {MASTER_OUTPUT}")
print(f"File size: {os.path.getsize(MASTER_OUTPUT) / (1024*1024):.2f} MB")
