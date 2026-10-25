import asyncio
import os
import sys
import subprocess
import edge_tts

sys.stdout.reconfigure(encoding="utf-8")

AUDIO_DIR = r"C:\TheNaughtyDuo_Automation\output\kalu_madari_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

LINES = [
    # Scene 1 (0s - 10s): Kalu Madari arrival hook with Damru beats
    ("s1_madari_hook", "डम-डम-डम-डम डमरू बाजे! कालू मदारी आया, साथ में गोलू भालू लाया!", "hi-IN-MadhurNeural", "-5Hz", "+15%"),
    ("s1_kaavya_excited", "अरे भैया देखो! कितना प्यारा और बड़ा भालू आया है!", "hi-IN-SwaraNeural", "+75Hz", "+22%"),
    ("s1_kaartik_clap", "डम डम डमरू! भालू भैया अपना डांस दिखाओ ना!", "hi-IN-SwaraNeural", "+20Hz", "+18%"),

    # Scene 2 (10s - 20s): Bear funny joyful dance
    ("s2_madari_command", "नाच मेरे भालू नाच! बच्चों को अपना गोल-गोल डांस दिखा!", "hi-IN-MadhurNeural", "-5Hz", "+18%"),
    ("s2_bhalu_growl_happy", "हाहाहा! छम-छम-छम! देखो मैं कैसे थिरक रहा हूँ!", "hi-IN-MadhurNeural", "+15Hz", "+25%"),
    ("s2_kaavya_laugh", "हाहाहा! भालू तो मटक-मटक के कितना फनी नाच रहा है!", "hi-IN-SwaraNeural", "+80Hz", "+22%"),

    # Scene 3 (20s - 30s): Grand Finale Celebration & Organic High-Retention CTA
    ("s3_all_cheer", "वाह भालू भैया वाह! आपने तो सबका दिल जीत लिया!", "hi-IN-SwaraNeural", "+25Hz", "+20%"),
    ("s3_organic_cta", "अगर आपको गोलू भालू का डांस मजेदार लगा, तो जल्दी से LIKE करो और चैनल को सब्सक्राइब करो! बाय-बाय!", "hi-IN-SwaraNeural", "+15Hz", "+16%"),
]

async def generate_audio():
    print("[*] Generating high-fidelity Hindi audio tracks for Kalu Madari Aaya...", flush=True)
    for lid, text, voice, pitch, rate in LINES:
        out_p = os.path.join(AUDIO_DIR, f"{lid}.mp3")
        comm = edge_tts.Communicate(text, voice=voice, pitch=pitch, rate=rate)
        await comm.save(out_p)
        
        res = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', out_p],
            capture_output=True, text=True
        )
        dur = float(res.stdout.strip()) if res.stdout.strip() else 0.0
        print(f"  [✓] {lid}: {dur:.2f}s | '{text}'", flush=True)

if __name__ == "__main__":
    asyncio.run(generate_audio())
