import os
import subprocess
import time

OUTPUT_DIR = r"C:\TheNaughtyDuo_Automation\output"
TARGET_OUTPUT = os.path.join(OUTPUT_DIR, "TheNaughtyDuo_2GB_StreamAdda_LiveMaster.mp4")
LIST_FILE = r"C:\TheNaughtyDuo_Automation\streamadda_concat_list.txt"

episodes = [
    "TheNaughtyDuo_BandarMama_Master.mp4",
    "TheNaughtyDuo_MachhliRani_Master.mp4",
    "TheNaughtyDuo_KaluMadari_Master.mp4",
    "TheNaughtyDuo_BilliMeow_Master.mp4",
    "TheNaughtyDuo_ChuheKoBukhar_Master.mp4",
    "TheNaughtyDuo_RoadSafety_Master.mp4",
    "TheNaughtyDuo_TableManners_Master.mp4",
    "TheNaughtyDuo_PlantSeed_Master.mp4",
    "TheNaughtyDuo_MorningSunshine_Master.mp4",
    "TheNaughtyDuo_ChidiyaDana_Master.mp4",
    "TheNaughtyDuo_3MagicWords_Master.mp4",
    "TheNaughtyDuo_Shoes_Dressing_Master.mp4",
    "TheNaughtyDuo_Sneeze_Manners_Master.mp4",
    "TheNaughtyDuo_Water_Drinking_Master.mp4",
    "TheNaughtyDuo_Potty_Song_Master.mp4",
    "TheNaughtyDuo_No_Screen_Time_Master.mp4",
    "TheNaughtyDuo_Hand_Wash_Master.mp4",
    "TheNaughtyDuo_Brush_Teeth_Master.mp4",
    "TheNaughtyDuo_EP25_Remastered_Master.mp4",
    "TheNaughtyDuo_EP26_Master.mp4",
    "TheNaughtyDuo_EP25_Master.mp4",
    "TheNaughtyDuo_EP24_OriginalAudio_Master.mp4",
    "TheNaughtyDuo_EP22_OriginalAudio_Master.mp4",
    "TheNaughtyDuo_NanhaDoctor_TeddyCheckup_Master_30s.mp4",
    "TheNaughtyDuo_CleanUpRace_Toys_Master_30s.mp4",
    "TheNaughtyDuo_Chhapaak_BathTime_Master_30s.mp4",
    "TheNaughtyDuo_ChhotiSiChot_MagicKiss_Master_30s.mp4"
]

total_bytes = 0
playlist = []
for _ in range(3):
    for ep in episodes:
        fp = os.path.join(OUTPUT_DIR, ep)
        if os.path.exists(fp):
            playlist.append(fp)
            total_bytes += os.path.getsize(fp)

# Fill safely up to 1920 MB (1.875 GB)
for ep in episodes:
    fp = os.path.join(OUTPUT_DIR, ep)
    if os.path.exists(fp):
        sz = os.path.getsize(fp)
        if total_bytes + sz < 1920 * 1024 * 1024:
            playlist.append(fp)
            total_bytes += sz

print(f"Total clips to concatenate: {len(playlist)}")
print(f"Projected size: {total_bytes / (1024*1024):.2f} MB ({total_bytes / (1024*1024*1024):.3f} GB)")

with open(LIST_FILE, "w", encoding="utf-8") as f:
    for p in playlist:
        p_esc = p.replace("\\", "/")
        f.write(f"file '{p_esc}'\n")

print(f"Created concat playlist at {LIST_FILE}")

# Now execute ffmpeg concat
cmd = [
    r"C:\Users\user\scoop\apps\ffmpeg\current\bin\ffmpeg.exe",
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", LIST_FILE,
    "-c", "copy",
    "-movflags", "+faststart",
    TARGET_OUTPUT
]

print("Starting FFmpeg concatenation (zero re-encode loss)...")
t0 = time.time()
result = subprocess.run(cmd, capture_output=True, text=True)
t1 = time.time()

if result.returncode == 0 and os.path.exists(TARGET_OUTPUT):
    out_sz = os.path.getsize(TARGET_OUTPUT)
    print(f"[SUCCESS] Master Compilation generated in {t1-t0:.1f}s!")
    print(f"Output File: {TARGET_OUTPUT}")
    print(f"Exact File Size: {out_sz / (1024*1024):.2f} MB ({out_sz / (1024*1024*1024):.3f} GB)")
else:
    print(f"[ERROR] FFmpeg failed with code {result.returncode}")
    print(result.stderr[-1000:])
