import subprocess
import os
from pathlib import Path

FFMPEG = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
BASE_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine")
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw_clips"
AUDIO_DIR = DATA_DIR / "audio_samples"
OUT_DIR = DATA_DIR / "processed_episodes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def mux_scene(video_in, a1_in, a2_in, delay1_ms, delay2_ms, video_out):
    print(f"Muxing {video_out.name}...")
    filter_complex = (
        f"[1:a]adelay={delay1_ms}|{delay1_ms}[a1]; "
        f"[2:a]adelay={delay2_ms}|{delay2_ms}[a2]; "
        f"[a1][a2]amix=inputs=2:duration=longest[aout]"
    )
    cmd = [
        FFMPEG, "-y",
        "-i", str(video_in),
        "-i", str(a1_in),
        "-i", str(a2_in),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "8.0",
        str(video_out)
    ]
    subprocess.run(cmd, check=True)
    print(f"[OK] {video_out.name} ready!")

def main():
    # Scene 1
    s1_v = RAW_DIR / "ep21_highheels_scene1_raw.mp4"
    s1_a1 = AUDIO_DIR / "ep21_s1_kaavya.mp3"
    s1_a2 = AUDIO_DIR / "ep21_s1_kaartik.mp3"
    s1_out = OUT_DIR / "ep21_s1_dubbed.mp4"
    mux_scene(s1_v, s1_a1, s1_a2, 300, 4100, s1_out)

    # Scene 2
    s2_v = RAW_DIR / "ep21_highheels_scene2_raw.mp4"
    s2_a1 = AUDIO_DIR / "ep21_s2_kaartik_snappy.mp3"
    s2_a2 = AUDIO_DIR / "ep21_s2_kaavya_snappy.mp3"
    s2_out = OUT_DIR / "ep21_s2_dubbed.mp4"
    mux_scene(s2_v, s2_a1, s2_a2, 300, 4100, s2_out)

    # Scene 3
    s3_v = RAW_DIR / "ep21_highheels_scene3_raw.mp4"
    s3_a1 = AUDIO_DIR / "ep21_s3_kaavya.mp3"
    s3_a2 = AUDIO_DIR / "ep21_s3_kaartik.mp3"
    s3_out = OUT_DIR / "ep21_s3_dubbed.mp4"
    mux_scene(s3_v, s3_a1, s3_a2, 300, 4000, s3_out)

    # Create concat list
    concat_file = OUT_DIR / "ep21_concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        # Use forward slashes for ffmpeg concat
        f.write(f"file '{s1_out.resolve().as_posix()}'\n")
        f.write(f"file '{s2_out.resolve().as_posix()}'\n")
        f.write(f"file '{s3_out.resolve().as_posix()}'\n")

    # Concat and upscale to 1080x1920 Full HD vertical 9:16
    master_out = OUT_DIR / "TheNaughtyDuo_EP21_MummyKiHighHeels_Master.mp4"
    print("Concatenating and upscaling to 1080x1920 Full HD...")
    concat_cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-vf", "scale=1080:1920:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "256k",
        str(master_out)
    ]
    subprocess.run(concat_cmd, check=True)
    print("\n==================================================")
    print("[SUCCESS] Master Episode 21 created at:")
    print(str(master_out))
    print(f"Size: {os.path.getsize(master_out)} bytes")
    print("==================================================")

if __name__ == "__main__":
    main()
