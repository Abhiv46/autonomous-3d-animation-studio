"""
Viral Sound Extractor using yt-dlp
Allows fetching any trending sound from YouTube Shorts or TikTok into the project.
Usage:
    python fetch_trending_shorts_sound.py "https://www.youtube.com/shorts/..." "sound_name"
"""

import os
import sys
import subprocess

TRENDING_DIR = r"C:\TheNaughtyDuo_Automation\trending_sound"
os.makedirs(TRENDING_DIR, exist_ok=True)

def fetch_audio(source_url, sound_name):
    output_template = os.path.join(TRENDING_DIR, f"{sound_name}.%(ext)s")
    print(f"[*] Extracting high-quality audio from: {source_url}...")
    
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", output_template,
        source_url
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    final_file = os.path.join(TRENDING_DIR, f"{sound_name}.mp3")
    if os.path.exists(final_file):
        sz_kb = os.path.getsize(final_file) / 1024
        print(f"[SUCCESS] Viral audio saved: {final_file} ({sz_kb:.1f} KB)")
        return final_file
    else:
        print(f"[ERROR] Failed to extract audio: {res.stderr}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fetch_trending_shorts_sound.py <url> <sound_name>")
    else:
        fetch_audio(sys.argv[1], sys.argv[2])
