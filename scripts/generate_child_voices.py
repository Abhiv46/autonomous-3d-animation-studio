import asyncio
import edge_tts
from pathlib import Path

AUDIO_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\audio_samples")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

async def generate_dialogue():
    # Kaavya: Cute Toddler Voice (+32Hz pitch, +12% rate)
    kaavya_text = "Dekho Kaartik bhaiyya! Main Mummy ki high heels pehan ke itni badi ho gayi!"
    kaavya_tts = edge_tts.Communicate(
        text=kaavya_text,
        voice="hi-IN-SwaraNeural",
        pitch="+32Hz",
        rate="+12%"
    )
    await kaavya_tts.save(str(AUDIO_DIR / "kaavya_line1.mp3"))
    print("[+] Generated Kaavya Line 1!")

    # Kaartik: Playful 5-year-old brother voice (+20Hz pitch, +8% rate)
    kaartik_text = "Arre Kaavya! Gir jaogi, Mummy aake bohot daantengi!"
    kaartik_tts = edge_tts.Communicate(
        text=kaartik_text,
        voice="hi-IN-MadhurNeural",
        pitch="+20Hz",
        rate="+8%"
    )
    await kaartik_tts.save(str(AUDIO_DIR / "kaartik_line1.mp3"))
    print("[+] Generated Kaartik Line 1!")

    # Kaavya: Sassy comeback
    kaavya_text2 = "Nahi girti! Dekho main to super model hoon, he he he!"
    kaavya_tts2 = edge_tts.Communicate(
        text=kaavya_text2,
        voice="hi-IN-SwaraNeural",
        pitch="+34Hz",
        rate="+14%"
    )
    await kaavya_tts2.save(str(AUDIO_DIR / "kaavya_line2.mp3"))
    print("[+] Generated Kaavya Line 2!")

if __name__ == "__main__":
    asyncio.run(generate_dialogue())
