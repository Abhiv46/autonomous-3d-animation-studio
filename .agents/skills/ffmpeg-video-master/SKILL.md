---
name: ffmpeg-video-master
description: Production-grade local video and audio processing via FFmpeg for YouTube Shorts. Covers audio loudness normalization (-14 LUFS), 9:16 vertical re-framing, dual-audio stream mixing, subtitle burning, and hardware-accelerated H.264/NVENC encoding.
---

# 🎬 FFmpeg Video Master Skill

High-performance video and audio engineering recipes specifically tuned for YouTube Shorts and YouTube Studio standards.

---

## 🔊 1. YouTube Audio Loudness Normalization (-14 LUFS)
YouTube automatically penalizes audio that is too quiet and lowers volume on audio that is too loud.
To meet the official YouTube standard (-14 LUFS, -1 dBFS True Peak):

```bash
ffmpeg -i input.mp4 -af "loudnorm=I=-14:TP=-1.0:LRA=7" -c:v copy -c:a aac -b:a 192k output_normalized.mp4
```

---

## 📐 2. Dual-Audio Viral Stream Mixing (Original 100% + Trending 0%)
Shorts feed algorithm ranks videos higher when attached to trending sounds. We attach the viral sound at 0% volume while keeping 100% original dialogue:

```bash
ffmpeg -i speech.mp4 -i trending.mp3 -filter_complex "[0:a]volume=1.0[a1];[1:a]volume=0.0[a2];[a1][a2]amix=inputs=2:duration=first:normalize=0:weights=1 0[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k final_mixed.mp4
```

---

## 📱 3. 9:16 Full HD Crop / Re-frame (1080x1920)
Convert any aspect ratio to standard 9:16 vertical with center crop:

```bash
ffmpeg -i input.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a copy output_916.mp4
```

---

## ⚡ 4. Fast Web Streaming Optimization (`-movflags +faststart`)
Places the MP4 `moov` atom at the beginning of the file so YouTube and browsers start playback instantly without waiting for the full video to download:

```bash
ffmpeg -i input.mp4 -c copy -movflags +faststart output_faststart.mp4
```

---

## 🖼️ 5. High-CTR Frame Extraction for Thumbnails
Extract the most expressive facial frame (e.g. at 12.5 seconds) as an uncompressed PNG:

```bash
ffmpeg -ss 00:00:12.500 -i input.mp4 -frames:v 1 -q:v 1 thumbnail_raw.png
```
