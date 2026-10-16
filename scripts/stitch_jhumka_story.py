import os
import subprocess

ffmpeg = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
folder = r"C:\Users\user\Downloads\For YouTube"
parts = [f"part{i}.mp4" for i in range(1, 8)]

concat_file = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\concat_parts1_7.txt"
with open(concat_file, "w", encoding="utf-8") as f:
    for p in parts:
        fpath = os.path.join(folder, p).replace("\\", "/")
        f.write("file '" + fpath + "'\n")

out_dir = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output"
os.makedirs(out_dir, exist_ok=True)
merged_raw = os.path.join(out_dir, "MummyKaJhumka_merged_raw.mp4")
bg_music = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\Carefree.mp3"
final_output = os.path.join(out_dir, "TheNaughtyDuo_MummyKaJhumka_Master.mp4")

# Step 1: Concat
cmd1 = [ffmpeg, "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", merged_raw, "-y"]
print("Running concat...")
res1 = subprocess.run(cmd1, capture_output=True, text=True)
print("Concat return code:", res1.returncode)
if os.path.exists(merged_raw):
    print("Merged raw size:", os.path.getsize(merged_raw), "bytes")
else:
    print("Concat error:", res1.stderr)
    exit(1)

# Step 2: Overlay background music with volume 0.16 and fade out at 53s (total 56s)
filter_str = "[1:a]volume=0.16,afade=t=out:st=53:d=3[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
cmd2 = [
    ffmpeg,
    "-i", merged_raw,
    "-i", bg_music,
    "-filter_complex", filter_str,
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    final_output,
    "-y"
]
print("Running audio mix and final mastering...")
res2 = subprocess.run(cmd2, capture_output=True, text=True)
print("Master return code:", res2.returncode)
if os.path.exists(final_output):
    print("SUCCESS: Master video created at:", final_output)
    print("Final file size:", os.path.getsize(final_output), "bytes")
else:
    print("Mastering error:", res2.stderr)
