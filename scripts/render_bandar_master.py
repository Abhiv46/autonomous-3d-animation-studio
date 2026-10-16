import os
import subprocess

ffmpeg = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
folder = r"C:\Users\user\Downloads\For YouTube"
trimmed_dir = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\trimmed_clips"
os.makedirs(trimmed_dir, exist_ok=True)

clips = [
    ("part1.mp4", os.path.join(folder, "Mummy Ne Bandar Ko Pakda1.mp4"), 8.0),
    ("part2.mp4", os.path.join(folder, "Mummy Ne Bandar Ko Pakda2.mp4"), 8.0),
    ("part3.mp4", os.path.join(trimmed_dir, "part3_trimmed.mp4"), None),
    ("part4.mp4", os.path.join(folder, "Mummy Ne Bandar Ko Pakda4.mp4"), 8.0),
    ("part5.mp4", os.path.join(folder, "Mummy Ne Bandar Ko Pakda5.mp4"), 8.0),
    ("part6.mp4", os.path.join(folder, "Mummy Ne Bandar Ko Pakda6.mp4"), 8.0),
    ("part7.mp4", os.path.join(folder, "Mummy Ne Bandar Ko Pakda7.mp4"), 8.0),
    ("part8.mp4", os.path.join(folder, "Mummy Ne Bandar Ko Pakda8.mp4"), 8.0),
]

norm_list = []
for name, path, t in clips:
    out_norm = os.path.join(trimmed_dir, f"norm_{name}")
    norm_list.append(out_norm)
    cmd = [ffmpeg, "-i", path]
    if t is not None:
        cmd.extend(["-t", str(t)])
    cmd.extend([
        "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "48000", "-ac", "2",
        out_norm, "-y"
    ])
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Norm {name}: code={res.returncode}, size={os.path.getsize(out_norm) if os.path.exists(out_norm) else 0}")

concat_file = os.path.join(trimmed_dir, "concat_bandar_final.txt")
with open(concat_file, "w", encoding="utf-8") as f:
    for fp in norm_list:
        clean_path = fp.replace("\\", "/")
        f.write("file '" + clean_path + "'\n")

out_dir = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\output"
os.makedirs(out_dir, exist_ok=True)
merged_raw = os.path.join(out_dir, "MummyNeBandarKoPakda_raw.mp4")

cmd_concat = [ffmpeg, "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", merged_raw, "-y"]
res_cat = subprocess.run(cmd_concat, capture_output=True, text=True)
print(f"Concat return: {res_cat.returncode}, raw size={os.path.getsize(merged_raw) if os.path.exists(merged_raw) else 0}")

# Mix with background music Carefree.mp3
bg_music = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\Carefree.mp3"
final_master = os.path.join(out_dir, "TheNaughtyDuo_MummyNeBandarKoPakda_Master.mp4")

# Total duration is 7*8 + 2.8 = 58.8 seconds
filter_str = "[1:a]volume=0.15,afade=t=out:st=55:d=3.5[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
cmd_mix = [
    ffmpeg,
    "-i", merged_raw,
    "-i", bg_music,
    "-filter_complex", filter_str,
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    final_master,
    "-y"
]
res_mix = subprocess.run(cmd_mix, capture_output=True, text=True)
print(f"Master return: {res_mix.returncode}, final size={os.path.getsize(final_master) if os.path.exists(final_master) else 0}")
print("SUCCESS MASTER VIDEO PATH:", final_master)
