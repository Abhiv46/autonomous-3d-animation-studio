---
name: viral-shorts-autopilot
description: Automated end-to-end production and publishing pipeline for The Naughty Duo YouTube Shorts & TikTok. Enforces the 8 mandatory viral gatekeeper rules, dual-audio (100% original + 0% viral sound), 3D high-CTR thumbnails, bilingual metadata, and 24/7 RTMP live streaming with 8-hour VOD archival compliance.
---

# 🚀 Viral Shorts Autopilot Skill — The Naughty Duo

This skill provides the comprehensive runbook, standards, and automation scripts for generating, assembling, validating, and publishing viral 3D animated Nursery Rhymes & Stories on YouTube Shorts and TikTok.

---

## 📌 Core Architecture & Workflows

### 1. Dual-Audio Assembly (`standard_viral_assembler.py`)
- **Original AI Audio**: Kept at **100% Volume (`volume=1.0`)** directly from raw video clips. Never overlay mismatched external voices.
- **Viral Trending Audio**: High-reach background sound with millions of views in Shorts feed (`C:\TheNaughtyDuo_Automation\trending_sound\monkeys_spinning_monkeys_viral.mp3`) mixed at **Zero Volume (`volume=0.0`)** via `amix=inputs=2:duration=first:normalize=0:weights=1 0`.
- **Resolution**: Normalized to **1080x1920 Full HD Vertical (9:16)** @ 30fps.
- **Thumbnail**: Automatic extraction of peak frame (10–18s) with bold yellow stroked top text and white bottom stroked text.

---

### 2. Mandatory 8-Point Gatekeeper Check (`strict_shorts_validator.py`)
No video may be posted or scheduled unless `validate_shorts_payload()` passes 100%:
1. **Video**: Exists, 1080x1920 Full HD, H.264/AAC.
2. **Audio**: Dual-Audio active (100% Original + 0% Viral).
3. **Title**: Bilingual (Hindi Devanagari script + Emoji + English + `#Shorts`).
4. **Description**: Script summary + mandatory 24/7 Live Stream Link (`https://www.youtube.com/channel/UCULzzCCm0Y-ZHiyF480ioLg/live`) + `#TheNaughtyDuo #Shorts`.
5. **Tags**: >50 chars, rich search keywords in English + Roman Hindi.
6. **Related Video**: Explicitly selected in YouTube Studio.
7. **Language**: Set to `Hindi`.
8. **Thumbnail**: 1080x1920 custom 3D image verified on disk.

---

### 3. Multi-Platform Deployment
- **YouTube Studio**: Upload via Playwright in persistent Brave context, fill bilingual metadata, expand details, set Language to Hindi, set Audience to Not Made for Kids, link Related Video, and schedule to specific time slot (12:30 PM, 3:30 PM, or 6:30 PM IST). Zero drafts allowed.
- **TikTok Studio**: Upload via Playwright, attach caption with viral tags (`#TheNaughtyDuo #KidsCartoon #HindiRhymes #FYP`), and confirm post live.

---

### 4. 24/7 Live Streaming Daemon (`live_stream_daemon.py`)
- Source: `TheNaughtyDuo_2GB_StreamAdda_LiveMaster.mp4` (90-clip master compilation).
- Transcoder: `-preset ultrafast -tune zerolatency` @ 2600 kbps (1.00x real-time sync, zero buffer starvation).
- **8-Hour VOD Archival Rule**: Automatically stops stream at 8 hours, rests 45 seconds for YouTube VOD finalization (preserving 100% watch time within the 12-hour limit), and restarts a fresh session.
- Watchdog: Windows Scheduled Task `TheNaughtyDuo_LiveStream_Watchdog` monitors health every 10 minutes silently via `run_watchdog_silent.vbs`.

---

## 🛠️ Helper Utilities Available

- **`yt-dlp`**: Extract trending sound clips, competitor metadata, and analyze Shorts feed.
- **`standard_viral_assembler.py`**: Assemble raw clips into master MP4 + thumbnail.
- **`strict_shorts_validator.py`**: Validate all criteria before uploading.
