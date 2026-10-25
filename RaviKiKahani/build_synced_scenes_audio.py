import asyncio
import edge_tts
import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = r"C:\TheNaughtyDuo_Automation\RaviKiKahani"
AUDIO_DIR = os.path.join(PROJECT_DIR, "scene_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

scenes_data = [
    {
        "scene": 1,
        "text": "एक छोटे से गाँव में रवि नाम का एक लड़का रहता था। वह बहुत गरीब था, लेकिन उसके सपने बहुत बड़े थे।",
        "duration": 8.0
    },
    {
        "scene": 2,
        "text": "रोज़ सुबह वह पाँच किलोमीटर पैदल स्कूल जाता था।",
        "duration": 8.0
    },
    {
        "scene": 3,
        "text": "एक दिन रास्ते में उसे एक पुराना, चमकता हुआ जादुई पेड़ मिला।",
        "duration": 10.0
    },
    {
        "scene": 4,
        "text": "पेड़ ने कहा — रवि, तुम्हारी मेहनत देखी मैंने। यह ले, एक जादुई बीज। इसे बो लो, और अपने सपने पूरे करो।",
        "duration": 10.0
    },
    {
        "scene": 5,
        "text": "रवि ने बीज बोया। अगले दिन वहाँ से एक सोने का पेड़ उगा।",
        "duration": 10.0
    },
    {
        "scene": 6,
        "text": "रवि ने उस पेड़ से अपने गाँव के सब बच्चों को पढ़ाया। और गाँव का नाम रोशनी से भर गया।",
        "duration": 8.0
    },
    {
        "scene": 7,
        "text": "Moral: मेहनत कभी बेकार नहीं जाती।",
        "duration": 6.0
    }
]

async def generate_scene_tracks():
    print("🎙️ Generating Frame-Perfect Scene Voiceovers via hi-IN-MadhurNeural...")
    padded_files = []

    for item in scenes_data:
        s_num = item["scene"]
        dur = item["duration"]
        raw_out = os.path.join(AUDIO_DIR, f"scene_{s_num}_raw.mp3")
        padded_out = os.path.join(AUDIO_DIR, f"scene_{s_num}_padded.mp3")

        # Edge TTS Communicate
        comm = edge_tts.Communicate(item["text"], "hi-IN-MadhurNeural", pitch="+1Hz", rate="-2%")
        await comm.save(raw_out)

        # Pad with silence to exact duration
        cmd = [
            "ffmpeg", "-y",
            "-i", raw_out,
            "-af", f"adelay=400|400,apad=whole_dur={dur}",
            "-t", str(dur),
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            padded_out
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        padded_files.append(padded_out)
        print(f"  ✅ Scene {s_num} ({dur}s): {item['text'][:40]}...")

    # Concatenate all 7 scenes
    concat_list = os.path.join(AUDIO_DIR, "concat_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in padded_files:
            f.write(f"file '{p}'\n")

    full_vo = os.path.join(PROJECT_DIR, "voiceover_synced.mp3")
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        full_vo
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"🎉 Full Synced Voiceover generated: {full_vo}")

    # Mix with soft background music
    bgm_path = r"C:\TheNaughtyDuo_Automation\trending_sound\carefree_viral.mp3"
    final_audio = os.path.join(PROJECT_DIR, "final_audio_60s.mp3")
    cmd_mix = [
        "ffmpeg", "-y",
        "-i", full_vo,
        "-i", bgm_path,
        "-filter_complex",
        "[0:a]volume=1.2[vo];[1:a]volume=0.10,atrim=0:60,afade=t=out:st=57:d=3[bgm];[vo][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-t", "60",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        final_audio
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"✨ 100% Synced Final 60s Audio: {final_audio}")

if __name__ == "__main__":
    asyncio.run(generate_scene_tracks())
