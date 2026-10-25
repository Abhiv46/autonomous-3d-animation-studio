# 🚀 THE NAUGHTY DUO — PERMANENT VIRAL SHORTS PUBLISHING RULES

---

## 📌 RULE 1: DUAL-AUDIO SYSTEM (EVERY VIDEO)
Har ek video par do audio tracks laazmi honge:
1. **Audio Track 1 (Original Audio - 100% Volume)**:
   - Video generator (Hailuo / Minimax / Omni) dwara generate ki gayi original character voices, dialogues aur ambient effects ko **100% volume (`volume=1.0`)** par rakhna hai.
   - Koi bhi external robot/mismatched voiceover add nahi karna hai.
2. **Audio Track 2 (Viral / Trending Shorts Audio - 0% Volume)**:
   - YouTube Shorts aur TikTok feed me jisme **Millions me views** aa rahe hain (jaise Kevin MacLeod's *Monkeys Spinning Monkeys* ya *Carefree*), wo audio video me attach karna hai.
   - Uska volume **ZERO (`volume=0.0`)** rakhna hai (`normalize=0:weights=1 0`).
   - **Purpose**: Algorithm video ko viral sound ke page aur trending sound feed par push karega, jabki viewers ko 100% clear original voice sunai degi.

---

## 📌 RULE 2: SEO & METADATA ARCHITECTURE
Har ek YouTube Shorts aur TikTok release ke liye:
1. **Bilingual Title**:
   - Format: `[Hindi Script] [Emoji] [English Transliteration] | The Naughty Duo #Shorts`
   - Example: `कालू मदारी आया 🐻🥁 Kalu Madari Aaya | The Naughty Duo #Shorts`
2. **Full SEO Description**:
   - Story / Dialogue Summary (Hindi + English).
   - **Live Stream Link**: 24/7 Live Stream / Compilation link included in description.
   - Channel CTA (Subscribe & Bell icon).
   - High-impact viral hashtags (`#TheNaughtyDuo #Shorts #HindiRhymes #3DAnimation #ViralShorts`).
3. **500-Character Search Tags**:
   - Top ranking search terms in both Roman Hindi and English.
4. **Language Setting**:
   - YouTube Studio me Video Language hamesha **Hindi** set hogi.

---

## 📌 RULE 3: RELATED VIDEO LINKING (YOUTUBE STUDIO)
- Har ek scheduled Short me YouTube Studio ke **"Related video"** feature me channel ki doosri popular video ya 24/7 Live Stream ko select karna zaroori hai.
- Isse Short ke bottom me clickable link aata hai jisse viewers automatically doosri video par jaate hain aur watch time multiply hota hai.

---

## 📌 RULE 4: HIGH-CTR CLICK-BASED 3D THUMBNAIL
- Har video ke peak engaging frame (10–18 seconds) se high-res 1080x1920 thumbnail extract karna hai.
- Top me **Bright Yellow Stroked Text** (e.g. `KALU MADARI AAYA!`).
- Bottom me **Clean White Stroked Text** with emojis (e.g. `BHALU KA DANCE! 🐻🥁`).
- Thumbnail ko YouTube aur TikTok dono par set karna hai.

---

## 📌 RULE 5: AUTOMATED PIPELINE SCRIPT
- Master assembly hamesha `standard_viral_assembler.py` se hogi jo automatically:
  1. Clips ko 1080x1920 standard 30fps par normalize karega.
  2. Original audio ko 100% volume par rakhega.
  3. Trending audio ko 0% volume par attach karega.
  4. 3D high-CTR thumbnail generate karega.
