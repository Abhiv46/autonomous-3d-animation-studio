---
name: edge-tts-voiceover
description: Free neural text-to-speech voiceover generation using Microsoft Edge TTS for The Naughty Duo characters (Kaartik, Kaavya, Mummy, Papa, Narrator) in Hindi and Indian English. Includes pitch and rate formulas for authentic toddler kid voice synthesis.
---

# 🎙️ Edge TTS Voiceover Skill — The Naughty Duo

This skill provides complete recipes, character vocal profiles, and automated Python scripts for generating 100% free, natural, studio-quality neural voiceovers via Microsoft Edge TTS (`edge-tts`).

---

## 🎭 The Naughty Duo Character Vocal Profiles

| Character | Target Voice | Pitch Shift | Speech Rate | Vocal Archetype |
| :--- | :--- | :--- | :--- | :--- |
| **Kaartik (4yo Boy)** | `hi-IN-MadhurNeural` | `+28Hz` | `+15%` | High-energy, playful toddler boy, mischievous giggle |
| **Kaavya (2.5yo Girl)**| `hi-IN-SwaraNeural` | `+38Hz` | `+10%` | Sweet, bubbly baby girl voice, cute, expressive |
| **Mummy** | `hi-IN-SwaraNeural` | `+0Hz` | `+0%` | Warm, loving, gentle Indian mother tone |
| **Papa / Narrator** | `hi-IN-MadhurNeural` | `-5Hz` | `+0%` | Deep, comforting, expressive storytelling voice |
| **English Narrator** | `en-IN-NeerjaExpressiveNeural`| `+0Hz` | `+5%` | Clear bilingual Indian English narration |

---

## ⚡ 1. One-Line CLI Command

```bash
edge-tts --voice hi-IN-SwaraNeural --text "हीहीही भैया, मुझे भी प्यारी बिंदी लगानी है!" --write-media dialogue.mp3
```

---

## 🐍 2. Python Programmatic Generation Script

```python
import asyncio
import edge_tts

async def synthesize_speech(text, voice="hi-IN-SwaraNeural", pitch="+30Hz", rate="+10%", output_path="out.mp3"):
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    await communicate.save(output_path)
    print(f"✅ Generated: {output_path}")

# Run synthesis
asyncio.run(synthesize_speech("अरे काव्या देखो!", voice="hi-IN-MadhurNeural", pitch="+28Hz"))
```

---

## 🔊 3. Audio Loudness & Post-Processing (FFmpeg)
To normalize the voiceover to YouTube broadcast standards (-14 LUFS):

```bash
ffmpeg -i dialogue.mp3 -af "loudnorm=I=-14:TP=-1.0:LRA=7" -c:a libmp3lame -q:a 2 dialogue_normalized.mp3
```
