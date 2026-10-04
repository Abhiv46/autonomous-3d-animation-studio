import subprocess
import glob
import os
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
files = sorted(glob.glob(r"C:\Users\user\Downloads\For YouTube\*.mp4"))
out_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2"

for i, f in enumerate(files):
    thumb = os.path.join(out_dir, f"thumb_clip_{i}.jpg")
    cmd = [ffmpeg_exe, "-y", "-ss", "00:00:03", "-i", f, "-vframes", "1", "-q:v", "2", thumb]
    subprocess.run(cmd, capture_output=True)
    print(f"Clip {i} ({os.path.basename(f)}): {thumb}")
