import os
import subprocess
import imageio_ffmpeg

ff = imageio_ffmpeg.get_ffmpeg_exe()
folder = r"C:\Users\user\Downloads\For YouTube"
out_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\new_thumbs"
os.makedirs(out_dir, exist_ok=True)

files = [f for f in os.listdir(folder) if f.endswith(".mp4")]

for f in sorted(files):
    p = os.path.join(folder, f)
    # Check duration using ffmpeg
    r = subprocess.run([ff, "-i", p], capture_output=True, text=True, errors="ignore")
    dur_str = "unknown"
    res_str = "unknown"
    for line in r.stderr.split("\n"):
        if "Duration:" in line:
            dur_str = line.split("Duration:")[1].split(",")[0].strip()
        if "Video:" in line:
            parts = line.split(",")
            for pt in parts:
                if "x" in pt and any(c.isdigit() for c in pt):
                    res_str = pt.strip()
                    break
    
    # Extract thumbnail
    thumb_path = os.path.join(out_dir, f"{os.path.splitext(f)[0]}.jpg")
    subprocess.run([ff, "-y", "-ss", "00:00:03", "-i", p, "-vframes", "1", "-q:v", "2", thumb_path], capture_output=True)
    print(f"{f:35} | Dur: {dur_str} | Res: {res_str}")
