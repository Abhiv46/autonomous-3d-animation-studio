import subprocess
from pathlib import Path

FFMPEG = r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
DATA_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data")
RAW_DIR = DATA_DIR / "raw_clips"
AUDIO_DIR = DATA_DIR / "audio_samples"
PROCESSED_DIR = DATA_DIR / "processed_episodes"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def mux_scene1():
    v = RAW_DIR / "ep21_highheels_scene1_raw.mp4"
    a1 = AUDIO_DIR / "ep21_s1_kaavya.mp3"
    a2 = AUDIO_DIR / "ep21_s1_kaartik.mp3"
    out = PROCESSED_DIR / "ep21_s1_dubbed.mp4"
    
    # Mix a1 at 0.3s, a2 at 4.2s
    # Using ffmpeg amix or adelay
    filter_complex = (
        "[1:a]adelay=300|300[k1]; "
        "[2:a]adelay=4200|4200[k2]; "
        "[k1][k2]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    cmd = [
        FFMPEG, "-y",
        "-i", str(v),
        "-i", str(a1),
        "-i", str(a2),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(out)
    ]
    subprocess.run(cmd, check=True)
    print("Muxed Scene 1 successfully to", out)

def mux_scene2():
    v = RAW_DIR / "ep21_highheels_scene2_raw.mp4"
    a1 = AUDIO_DIR / "ep21_s2_kaartik_snappy.mp3"
    a2 = AUDIO_DIR / "ep21_s2_kaavya_snappy.mp3"
    out = PROCESSED_DIR / "ep21_s2_dubbed.mp4"
    
    filter_complex = (
        "[1:a]adelay=300|300[kt]; "
        "[2:a]adelay=4100|4100[kv]; "
        "[kt][kv]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    cmd = [
        FFMPEG, "-y",
        "-i", str(v),
        "-i", str(a1),
        "-i", str(a2),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(out)
    ]
    subprocess.run(cmd, check=True)
    print("Muxed Scene 2 successfully to", out)

if __name__ == "__main__":
    mux_scene1()
    mux_scene2()
