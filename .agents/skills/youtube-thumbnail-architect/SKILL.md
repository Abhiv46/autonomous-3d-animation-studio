---
name: youtube-thumbnail-architect
description: High-CTR 3D thumbnail generation and composition engineering. Eye-tracking rules, emotional facial expressions, color contrast psychology, mobile viewport safe-zones, and PIL/Photoshop text overlay scripts.
---

# 🎨 YouTube Thumbnail Architect Skill

Engineering thumbnails with **>12% Click-Through Rate (CTR)** for YouTube Shorts and YouTube Longform.

---

## 👁️ 1. The 3 Pillars of Kids & Toddler CTR

1. **Extreme Facial Emotion**:
   - Shocked wide eyes (O-shaped mouth, raised eyebrows).
   - Uncontrollable toddler laughter (crinkled eyes, wide smile).
   - Characters must look directly towards the camera or towards the focal object.

2. **Color Contrast Psychology**:
   - Primary vibrant palette: **Warm Golden Yellow (`#FFD700`)**, **Electric Cyan (`#00E5FF`)**, and **Vivid Ruby Red (`#FF1744`)**.
   - Character foreground must be separated from background with a subtle rim-light (soft white/gold glow).

3. **Bold Dual-Stroked Text (< 4 Words)**:
   - Text must be readable on a 3-inch mobile screen in 0.2 seconds.
   - Font: Extra-bold sans-serif / comic style (e.g., Montserrat Black, Luckiest Guy, Impact).
   - Style: Yellow fill with thick black stroke (8px) + soft drop shadow.

---

## 📱 2. YouTube Shorts 9:16 Safe-Zone Grid

In the YouTube Shorts mobile player, YouTube places UI elements over parts of the video:
- **Top 15% (0–288px)**: Channel logo, search icon, sound badge.
- **Bottom 25% (1440–1920px)**: Channel name, subscribe button, title, audio title.
- **Right 18% (885–1080px)**: Like, Dislike, Comments, Share, Remix buttons.

> [!IMPORTANT]
> **Golden Safe Zone**: Keep key faces, expressions, and text overlays strictly within **Y: 300px to Y: 1350px** and **X: 60px to X: 850px**.

---

## 🐍 3. Automated PIL Overlay Script Template

```python
from PIL import Image, ImageDraw, ImageFont

def render_viral_thumbnail(base_image_path, top_text, output_path):
    img = Image.open(base_image_path).convert("RGBA").resize((1080, 1920))
    draw = ImageDraw.Draw(img)
    # Load bold font
    font = ImageFont.truetype("arialbd.ttf", 90)
    
    # Draw thick stroke (black) + Yellow fill
    # Placed in the Golden Safe Zone (Y: 320px)
    draw.text((540, 320), top_text, font=font, fill="#FFD700",
              stroke_width=10, stroke_fill="#000000", anchor="mm")
    
    img.convert("RGB").save(output_path, "JPEG", quality=95)
```
