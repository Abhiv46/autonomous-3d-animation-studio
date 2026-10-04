import subprocess
import os
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
video = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output\TheNaughtyDuo_GoodHabits_Master.mp4"
out_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"

# Get duration and stream details
cmd = [FFMPEG, "-i", video]
res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
for l in res.stderr.splitlines():
    if "Duration" in l or "Stream #0" in l:
        print(l.strip())

# Extract 6 proof frames (one from each of the 6 scenes)
timestamps = [5, 15, 25, 35, 45, 55]
names = [
    "good_habits_s1_wakeup.jpg",
    "good_habits_s2_brush.jpg",
    "good_habits_s3_handwash.jpg",
    "good_habits_s4_fruit.jpg",
    "good_habits_s5_toys.jpg",
    "good_habits_s6_park.jpg"
]

for ts, name in zip(timestamps, names):
    out_path = os.path.join(out_dir, name)
    subprocess.run([FFMPEG, "-y", "-ss", str(ts), "-i", video, "-vframes", "1", "-q:v", "2", out_path], capture_output=True)
    print(f"Extracted {name} at {ts}s")
