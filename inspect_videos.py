import subprocess
import os
import json

folder = r"C:\Users\user\Downloads\For YouTube"
out_thumb_dir = r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\new_videos_thumbs"
os.makedirs(out_thumb_dir, exist_ok=True)

files = [
    "1.mp4", "2.mp4", "3.mp4", "5.mp4", "6.mp4", "7.mp4", "8.mp4",
    "Character_performing_rhythmic_vo._1080p_20261004184242.mp4",
    "Children_arguing_about_missing_c._20261004180339.mp4",
    "Family_cleans_messy_bedroom_20261004183933.mp4",
    "Kaavya_avoids_school_on_Monday_20261004183940.mp4"
]

for f in files:
    p = os.path.join(folder, f)
    if os.path.exists(p):
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type", "-of", "json", p]
        res = subprocess.run(cmd, capture_output=True, text=True)
        try:
            info = json.loads(res.stdout)
            dur = float(info["format"]["duration"])
            streams = info.get("streams", [])
            v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
            has_audio = any(s.get("codec_type") == "audio" for s in streams)
            w = v_stream.get("width")
            h = v_stream.get("height")
            print(f"{f:35} -> {dur:.2f}s | {w}x{h} | Audio: {has_audio}")
            
            # Extract thumbnail frame at middle
            t_out = os.path.join(out_thumb_dir, f"{os.path.splitext(f)[0]}.jpg")
            subprocess.run([
                "ffmpeg", "-y", "-ss", str(dur / 2), "-i", p,
                "-vframes", "1", "-q:v", "2", t_out
            ], capture_output=True)
        except Exception as e:
            print(f"{f} error: {e}")
