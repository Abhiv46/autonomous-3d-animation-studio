"""
Standard Viral Shorts Assembler for The Naughty Duo
Rules enforced:
1. 100% Original AI Audio (Character Voices + Dialogue) at volume=1.0.
2. Trending Viral Audio (Millions of views in Shorts feed) at volume=0.0 (normalize=0, weights=1 0).
3. 1080x1920 Full HD Vertical (9:16) 30 fps.
4. Click-based 3D High-CTR Thumbnail with Top Yellow & Bottom White stroked text.
5. Faststart MP4 encoding.
"""

import os
import sys
import subprocess
from PIL import Image, ImageDraw, ImageFont

VIRAL_AUDIO_DIR = r"C:\TheNaughtyDuo_Automation\trending_sound"
DEFAULT_VIRAL_SOUND = os.path.join(VIRAL_AUDIO_DIR, "monkeys_spinning_monkeys_viral.mp3")

def assemble_viral_short(
    clip_paths,
    output_video_path,
    output_thumbnail_path,
    top_text,
    bottom_text,
    viral_sound_path=DEFAULT_VIRAL_SOUND,
    duration=30.00
):
    print(f"[*] Assembling Viral Short with Dual-Audio System...")
    print(f"    - Clips: {len(clip_paths)}")
    print(f"    - Output: {output_video_path}")
    print(f"    - Viral Sound: {viral_sound_path} (Volume: 0.0)")

    if not os.path.exists(viral_sound_path):
        raise FileNotFoundError(f"Viral audio not found at: {viral_sound_path}")

    for cp in clip_paths:
        if not os.path.exists(cp):
            raise FileNotFoundError(f"Source clip not found: {cp}")

    # Build FFmpeg filter_complex
    # Video scale/pad/fps
    n_clips = len(clip_paths)
    fc_parts = []
    for i in range(n_clips):
        fc_parts.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,setpts=PTS-STARTPTS[v{i}]"
        )
    v_inputs = "".join(f"[v{i}]" for i in range(n_clips))
    fc_parts.append(f"{v_inputs}concat=n={n_clips}:v=1:a=0[outv]")

    # Audio concat original clips
    a_inputs = "".join(f"[{i}:a]" for i in range(n_clips))
    fc_parts.append(f"{a_inputs}concat=n={n_clips}:v=0:a=1[orig_raw_a]")
    fc_parts.append("[orig_raw_a]volume=1.0,aformat=sample_rates=48000:channel_layouts=stereo[a_orig]")

    # Viral sound at volume 0.0
    viral_idx = n_clips
    fc_parts.append(f"[{viral_idx}:a]volume=0.0,aformat=sample_rates=48000:channel_layouts=stereo[a_viral]")

    # Amix with normalize=0 and weights=1 0
    fc_parts.append("[a_orig][a_viral]amix=inputs=2:duration=first:normalize=0:weights=1 0[final_a]")

    filter_complex_str = ";".join(fc_parts)

    cmd = [r"C:\Users\user\scoop\apps\ffmpeg\current\bin\ffmpeg.exe", "-y"]
    for cp in clip_paths:
        cmd.extend(["-i", cp])
    cmd.extend(["-i", viral_sound_path])

    cmd.extend([
        "-filter_complex", filter_complex_str,
        "-map", "[outv]",
        "-map", "[final_a]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{duration:.2f}",
        "-movflags", "+faststart",
        output_video_path
    ])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(output_video_path):
        raise RuntimeError(f"FFmpeg assembly failed: {res.stderr}")

    sz_mb = os.path.getsize(output_video_path) / (1024 * 1024)
    print(f"[OK] Master Video generated successfully! Size: {sz_mb:.2f} MB")

    # Generate Click-based 3D Thumbnail
    print(f"[*] Generating Click-based 3D Thumbnail: {output_thumbnail_path}...")
    temp_frame = output_video_path + ".thumb_temp.jpg"
    cmd_frame = [
        r"C:\Users\user\scoop\apps\ffmpeg\current\bin\ffmpeg.exe",
        "-y", "-ss", "00:00:14", "-i", output_video_path, "-vframes", "1", "-q:v", "2", temp_frame
    ]
    subprocess.run(cmd_frame, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(temp_frame):
        cmd_frame[3] = "00:00:08"
        subprocess.run(cmd_frame, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    img = Image.open(temp_frame).convert("RGBA")
    img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    try:
        font_main = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 95)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 85)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = font_main

    def draw_stroked(d, pos, text, font, fill_col, stroke_col, stroke_w=8):
        x, y = pos
        for dx in range(-stroke_w, stroke_w + 1):
            for dy in range(-stroke_w, stroke_w + 1):
                if dx*dx + dy*dy <= stroke_w*stroke_w:
                    d.text((x + dx, y + dy), text, font=font, fill=stroke_col)
        d.text((x, y), text, font=font, fill=fill_col)

    # Top Text (Yellow)
    bbox1 = draw.textbbox((0, 0), top_text, font=font_main)
    w1 = bbox1[2] - bbox1[0]
    draw_stroked(draw, ((1080 - w1)//2, 160), top_text, font_main, (255, 235, 59, 255), (0, 0, 0, 255), 8)

    # Bottom Text (White)
    bbox2 = draw.textbbox((0, 0), bottom_text, font=font_sub)
    w2 = bbox2[2] - bbox2[0]
    draw_stroked(draw, ((1080 - w2)//2, 1680), bottom_text, font_sub, (255, 255, 255, 255), (0, 0, 0, 255), 8)

    final_rgb = img.convert("RGB")
    final_rgb.save(output_thumbnail_path, quality=95)
    if os.path.exists(temp_frame):
        os.remove(temp_frame)

    print(f"[OK] 3D Thumbnail ready: {output_thumbnail_path}")
    return output_video_path, output_thumbnail_path
