import subprocess
import glob
import os

files = glob.glob(r"C:\Users\user\Downloads\For YouTube\*.mp4")
for f in files:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=width,height,r_frame_rate,codec_name,codec_type",
        "-of", "default=noprint_wrappers=1", f
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("FILE:", os.path.basename(f))
    print(res.stdout.strip())
    print("-" * 40)
