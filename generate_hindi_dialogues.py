import asyncio
import edge_tts
from pathlib import Path

OUT_DIR = Path(r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\audio_samples")
OUT_DIR.mkdir(parents=True, exist_ok=True)

async def generate_dialogues():
    # Scene 1:
    # Kaavya: toddler excitement
    s1_k = edge_tts.Communicate("Bhaiyya dekho! Main kitni badi ho gayi!", "hi-IN-SwaraNeural", pitch="+36Hz", rate="+25%")
    await s1_k.save(str(OUT_DIR / "ep21_s1_kaavya.mp3"))
    
    # Kaartik: protective brother
    s1_kt = edge_tts.Communicate("Arre Kaavya gir jaogi! Utaro jaldi!", "hi-IN-MadhurNeural", pitch="+22Hz", rate="+20%")
    await s1_kt.save(str(OUT_DIR / "ep21_s1_kaartik.mp3"))

    # Scene 2:
    # Kaartik acting strict
    s2_kt = edge_tts.Communicate("Yeh Mummy ki heels kisne pehni? Abhi daant padegi!", "hi-IN-MadhurNeural", pitch="+22Hz", rate="+22%")
    await s2_kt.save(str(OUT_DIR / "ep21_s2_kaartik.mp3"))
    
    # Kaavya cute puppy-dog eyes plea
    s2_k = edge_tts.Communicate("Bhaiyya please mat batao na! Main to bas model ban rahi thi!", "hi-IN-SwaraNeural", pitch="+36Hz", rate="+25%")
    await s2_k.save(str(OUT_DIR / "ep21_s2_kaavya.mp3"))

    print("All dialogue files generated successfully!")

asyncio.run(generate_dialogues())
