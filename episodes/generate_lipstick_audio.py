import asyncio
import edge_tts
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ep_dir = r"C:\TheNaughtyDuo_Automation\episodes\ep_mummy_lipstick"
os.makedirs(ep_dir, exist_ok=True)

dialogues = [
    {
        'id': 'd1_kaavya',
        'voice': 'hi-IN-SwaraNeural',
        'pitch': '+38Hz',
        'rate': '+10%',
        'text': 'अरे वाह! मम्मी की लाल लिपस्टिक मिल गई! हीहीही!'
    },
    {
        'id': 'd2_kaavya',
        'voice': 'hi-IN-SwaraNeural',
        'pitch': '+38Hz',
        'rate': '+10%',
        'text': 'भैया रुको, मैं तुम्हारे माथे पर बड़ी सी लाल बिंदी लगाती हूँ!'
    },
    {
        'id': 'd3_kaartik',
        'voice': 'hi-IN-MadhurNeural',
        'pitch': '+28Hz',
        'rate': '+15%',
        'text': 'अरे काव्या रुको! हाहाहा, मैं तुम्हारी मूंछें बनाता हूँ!'
    },
    {
        'id': 'd4_both',
        'voice': 'hi-IN-MadhurNeural',
        'pitch': '+26Hz',
        'rate': '+15%',
        'text': 'हाहाहाहा! देखो आईने में, हम कैसे कार्टून लग रहे हैं!'
    },
    {
        'id': 'd5_mummy',
        'voice': 'hi-IN-SwaraNeural',
        'pitch': '+0Hz',
        'rate': '+0%',
        'text': 'अरे मेरे नटखट बच्चों! ये चेहरे पर क्या कर दिया! हाहाहा, इधर आओ दोनों!'
    },
    {
        'id': 'd6_outro',
        'voice': 'hi-IN-SwaraNeural',
        'pitch': '+35Hz',
        'rate': '+10%',
        'text': 'लव यू मम्मी! सब्सक्राइब करो!'
    }
]

async def gen_all():
    print("🎙️ Generating Lipstick Episode Dialogues via Edge TTS...")
    for d in dialogues:
        out_p = os.path.join(ep_dir, f"{d['id']}.mp3")
        comm = edge_tts.Communicate(d['text'], d['voice'], pitch=d['pitch'], rate=d['rate'])
        await comm.save(out_p)
        print(f"  ✅ Generated {d['id']}: {d['text']}")

if __name__ == "__main__":
    asyncio.run(gen_all())
