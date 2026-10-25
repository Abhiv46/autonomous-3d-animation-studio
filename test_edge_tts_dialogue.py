import asyncio
import edge_tts
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r"C:\TheNaughtyDuo_Automation\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

test_files = [
    {
        "role": "Kaartik",
        "text": "अरे काव्या देखो! मम्मी की लाल लिपस्टिक मिल गई!",
        "voice": "hi-IN-MadhurNeural",
        "pitch": "+28Hz",
        "rate": "+15%",
        "out": os.path.join(OUTPUT_DIR, "voice_test_kaartik.mp3")
    },
    {
        "role": "Kaavya",
        "text": "हीहीही भैया, मुझे भी प्यारी बिंदी लगानी है!",
        "voice": "hi-IN-SwaraNeural",
        "pitch": "+38Hz",
        "rate": "+10%",
        "out": os.path.join(OUTPUT_DIR, "voice_test_kaavya.mp3")
    },
    {
        "role": "Mummy",
        "text": "अरे मेरे प्यारे शरारती बच्चों! ये चेहरे पर क्या लगा लिया!",
        "voice": "hi-IN-SwaraNeural",
        "pitch": "+0Hz",
        "rate": "+0%",
        "out": os.path.join(OUTPUT_DIR, "voice_test_mummy.mp3")
    }
]

async def generate_all():
    print("🎙️ Testing Edge TTS Dialogue Generation...")
    for item in test_files:
        communicate = edge_tts.Communicate(
            item["text"],
            item["voice"],
            pitch=item["pitch"],
            rate=item["rate"]
        )
        await communicate.save(item["out"])
        size_kb = os.path.getsize(item["out"]) / 1024
        print(f"✅ {item['role']}: {item['text']}")
        print(f"   -> File: {item['out']} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    asyncio.run(generate_all())
