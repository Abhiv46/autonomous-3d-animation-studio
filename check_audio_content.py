import subprocess
import os
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
sequence = [
    r"C:\Users\user\Downloads\For YouTube\Children_waking_up_and_brushing_20261003082034.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_demonstrating_good_habits_20261003082503.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_washing_hands_with_soap_20261003082108.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_sharing_fruit_together_20261003082511.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_cleaning_toys_in_playroom_20261003082115.mp4",
    r"C:\Users\user\Downloads\For YouTube\Children_playing_in_park_20261003082609.mp4"
]

# Check if speech_recognition or whisper or any package is installed
try:
    import speech_recognition as sr
    r = sr.Recognizer()
    for idx, path in enumerate(sequence, 1):
        wav_path = f"temp_aud_{idx}.wav"
        subprocess.run([ffmpeg_exe, "-y", "-i", path, "-ar", "16000", "-ac", "1", wav_path], capture_output=True)
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio)
                print(f"Clip {idx} recognized speech:", text)
            except Exception as e:
                print(f"Clip {idx} no speech recognized ({e})")
        if os.path.exists(wav_path):
            os.remove(wav_path)
except Exception as e:
    print("Speech recognition not available:", e)
