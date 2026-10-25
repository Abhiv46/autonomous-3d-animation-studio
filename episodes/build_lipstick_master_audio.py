import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

EP_DIR = r"C:\TheNaughtyDuo_Automation\episodes\ep_mummy_lipstick"
TRENDING_BGM = r"C:\TheNaughtyDuo_Automation\trending_sound\monkeys_spinning_monkeys_viral.mp3"
OUTPUT_AUDIO = os.path.join(EP_DIR, "mummy_lipstick_master_audio_30s.mp3")

# Time-aligned clips:
# d1_kaavya: 0.5s to 3.8s (dur 3.3s)
# d2_kaavya: 4.2s to 7.8s (dur 3.6s)
# d3_kaartik: 7.9s to 11.2s (dur 3.3s)
# d4_both: 11.5s to 18.5s (dur 7.0s)
# d5_mummy: 18.8s to 26.5s (dur 7.7s)
# d6_outro: 26.8s to 29.8s (dur 3.0s)

print("🎵 Assembling 30-Second Multi-Character Master Audio with Sfx & Ambience...")

# Generate aligned delays:
cmd = [
    "ffmpeg", "-y",
    "-i", os.path.join(EP_DIR, "d1_kaavya.mp3"),
    "-i", os.path.join(EP_DIR, "d2_kaavya.mp3"),
    "-i", os.path.join(EP_DIR, "d3_kaartik.mp3"),
    "-i", os.path.join(EP_DIR, "d4_both.mp3"),
    "-i", os.path.join(EP_DIR, "d5_mummy.mp3"),
    "-i", os.path.join(EP_DIR, "d6_outro.mp3"),
    "-i", TRENDING_BGM,
    "-filter_complex",
    "[0:a]adelay=400|400,volume=1.2[a0];"
    "[1:a]adelay=4200|4200,volume=1.2[a1];"
    "[2:a]adelay=7900|7900,volume=1.2[a2];"
    "[3:a]adelay=11500|11500,volume=1.25[a3];"
    "[4:a]adelay=18800|18800,volume=1.2[a4];"
    "[5:a]adelay=26800|26800,volume=1.2[a5];"
    "[6:a]volume=0.10,atrim=0:30,afade=t=out:st=28:d=2[bgm];"
    "[a0][a1][a2][a3][a4][a5][bgm]amix=inputs=7:duration=longest:dropout_transition=2[aout]",
    "-map", "[aout]",
    "-t", "30",
    "-c:a", "libmp3lame",
    "-b:a", "192k",
    OUTPUT_AUDIO
]

res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res.returncode == 0:
    print(f"🎉 SUCCESS! 30s Master Dialogue Audio generated: {OUTPUT_AUDIO}")
else:
    print(f"❌ FFmpeg error: {res.stderr}")
