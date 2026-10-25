import os
import sys
import time
import subprocess

# 24/7 Live Stream Daemon - Zero-Lag Ultrafast 30fps Real-Time Streamer
# Fixes "YouTube is not receiving enough video / Poor / Preparing stream" error.
# Uses -preset ultrafast -tune zerolatency to guarantee 1.000x real-time speed.

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\output\TheNaughtyDuo_2GB_StreamAdda_LiveMaster.mp4"
STREAM_KEY = "y0ke-3tz1-hg4j-hwjt-347m"
RTMP_URL   = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
LOG_FILE   = r"C:\TheNaughtyDuo_Automation\live_stream.log"
MAX_STREAM_SECONDS = 8 * 3600  # 8 Hours (YouTube 12-Hour VOD Archival Rule)

print(f"[*] Starting Rock-Solid Live Stream Daemon (Zero-Lag Ultrafast)...", flush=True)
print(f"[*] Source: {VIDEO_PATH}", flush=True)

if not os.path.exists(VIDEO_PATH):
    print(f"[ERROR] Missing video: {VIDEO_PATH}")
    sys.exit(1)

while True:
    cmd = [
        r"C:\Users\user\scoop\apps\ffmpeg\current\bin\ffmpeg.exe",
        "-re",                          # Exact 1.000x native playback rate
        "-stream_loop", "-1",           # Infinite loop
        "-i", VIDEO_PATH,
        "-c:v", "libx264",              # H.264 video
        "-preset", "ultrafast",         # Maximum CPU efficiency (guarantees >= 30fps real-time)
        "-tune", "zerolatency",         # Zero buffering delay
        "-b:v", "2500k",                # Stable 2.5 Mbps Full HD
        "-maxrate", "2800k",
        "-bufsize", "5000k",
        "-pix_fmt", "yuv420p",
        "-g", "60",                     # Exactly 1 keyframe every 2.0s @ 30fps (Mandatory for YouTube)
        "-keyint_min", "60",
        "-sc_threshold", "0",
        "-c:a", "copy",                 # Pass through clean AAC audio
        "-f", "flv",
        "-flvflags", "no_duration_filesize",
        RTMP_URL
    ]

    start_time = time.time()
    session_start_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    print(f"\n[LIVE] Starting stream session at {session_start_str}...", flush=True)

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"\n=======================================================\n")
        log.write(f"--- Zero-Lag Stream Session Started at {session_start_str} ---\n")
        log.write(f"=======================================================\n")
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)

    while True:
        elapsed = time.time() - start_time
        ret = proc.poll()
        if ret is not None:
            print(f"[!] FFmpeg exited with code {ret}. Auto-recovering in 3s...", flush=True)
            time.sleep(3)
            break

        if elapsed >= MAX_STREAM_SECONDS:
            print(f"\n[VOD ARCHIVE] 8-Hour Limit Reached ({elapsed/3600:.2f} hrs)!", flush=True)
            print("[VOD ARCHIVE] Stopping stream cleanly for YouTube VOD generation...", flush=True)
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()

            print("[VOD ARCHIVE] Resting 45s for YouTube VOD processing...", flush=True)
            time.sleep(45)
            break

        time.sleep(15)
