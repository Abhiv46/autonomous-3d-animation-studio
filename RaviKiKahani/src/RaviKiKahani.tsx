import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { StickMan } from "./StickMan";

export const RaviKiKahani: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Helper for scene fade in/out
  const getSceneOpacity = (start: number, end: number) => {
    const fadeIn = interpolate(frame, [start, start + 15], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    const fadeOut = interpolate(frame, [end - 15, end], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    return Math.min(fadeIn, fadeOut);
  };

  return (
    <AbsoluteFill style={{ backgroundColor: "#F7F9FC", fontFamily: "sans-serif" }}>
      {/* Background Audio / Voiceover */}
      <Audio src={staticFile("final_audio_60s.mp3")} />

      {/* ============================================================== */}
      {/* SCENE 1: Village Walk (0 - 8 sec / frames 0 - 240)             */}
      {/* ============================================================== */}
      <Sequence from={0} durationInFrames={240}>
        <Scene1 frame={frame} />
      </Sequence>

      {/* ============================================================== */}
      {/* SCENE 2: Walking 5 KM to School (8 - 16 sec / frames 240 - 480) */}
      {/* ============================================================== */}
      <Sequence from={240} durationInFrames={240}>
        <Scene2 frame={frame - 240} />
      </Sequence>

      {/* ============================================================== */}
      {/* SCENE 3: Glowing Magical Tree (16 - 26 sec / frames 480 - 780) */}
      {/* ============================================================== */}
      <Sequence from={480} durationInFrames={300}>
        <Scene3 frame={frame - 480} />
      </Sequence>

      {/* ============================================================== */}
      {/* SCENE 4: Tree Speaks & Gives Seed (26 - 36 sec / frames 780 - 1080) */}
      {/* ============================================================== */}
      <Sequence from={780} durationInFrames={300}>
        <Scene4 frame={frame - 780} />
      </Sequence>

      {/* ============================================================== */}
      {/* SCENE 5: Golden Tree Grows (36 - 46 sec / frames 1080 - 1380) */}
      {/* ============================================================== */}
      <Sequence from={1080} durationInFrames={300}>
        <Scene5 frame={frame - 1080} />
      </Sequence>

      {/* ============================================================== */}
      {/* SCENE 6: Teaching Village Kids (46 - 54 sec / frames 1380 - 1620) */}
      {/* ============================================================== */}
      <Sequence from={1380} durationInFrames={240}>
        <Scene6 frame={frame - 1380} />
      </Sequence>

      {/* ============================================================== */}
      {/* SCENE 7: Moral & Follow Pulse (54 - 60 sec / frames 1620 - 1800) */}
      {/* ============================================================== */}
      <Sequence from={1620} durationInFrames={180}>
        <Scene7 frame={frame - 1620} fps={fps} />
      </Sequence>

      {/* Global Top Channel Tag */}
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 0,
          right: 0,
          textAlign: "center",
          zIndex: 50,
        }}
      >
        <span
          style={{
            backgroundColor: "rgba(0,0,0,0.75)",
            color: "#FFD700",
            padding: "14px 40px",
            borderRadius: 40,
            fontSize: 38,
            fontWeight: 800,
            letterSpacing: 2,
            border: "3px solid #FFD700",
          }}
        >
          ✨ रवि की कहानी ✨
        </span>
      </div>
    </AbsoluteFill>
  );
};

// =========================================================================
// SCENE IMPLEMENTATIONS
// =========================================================================

const Scene1: React.FC<{ frame: number }> = ({ frame }) => {
  const walkProgress = (frame / 240) * 850 + 100;
  return (
    <AbsoluteFill style={{ backgroundColor: "#87CEEB" }}>
      {/* Sun & Clouds */}
      <div style={{ position: "absolute", top: 180, left: 140, width: 140, height: 140, borderRadius: "50%", backgroundColor: "#FFD700", boxShadow: "0 0 50px #FFA500" }} />
      {/* Village Hills */}
      <svg style={{ position: "absolute", bottom: 450, width: "100%", height: 600 }}>
        <path d="M 0 400 Q 300 200 650 380 T 1080 320 L 1080 600 L 0 600 Z" fill="#66BB6A" />
      </svg>
      {/* Simple Village Hut */}
      <svg style={{ position: "absolute", bottom: 520, left: 160, width: 340, height: 300 }}>
        <polygon points="170,40 40,150 300,150" fill="#8D6E63" stroke="#4E342E" strokeWidth="6" />
        <rect x="70" y="150" width="200" height="150" fill="#D7CCC8" stroke="#4E342E" strokeWidth="6" />
        <rect x="140" y="200" width="60" height="100" fill="#5D4037" />
      </svg>
      {/* Ground Road */}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 520, backgroundColor: "#E0A96D", borderTop: "12px solid #81C784" }} />
      {/* Stickman Ravi Walking */}
      <StickMan x={walkProgress} y={1150} scale={1.8} walkFrame={frame} armPose="walk" />
      {/* Subtitles */}
      <SubtitleBox text="एक छोटे से गाँव में रवि नाम का एक लड़का रहता था..." />
    </AbsoluteFill>
  );
};

const Scene2: React.FC<{ frame: number }> = ({ frame }) => {
  const walkProgress = (frame / 240) * 800 + 140;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(180deg, #FF7043 0%, #FFE082 60%, #81C784 100%)" }}>
      {/* Sunrise */}
      <div style={{ position: "absolute", top: 320, left: 440, width: 200, height: 200, borderRadius: "50%", backgroundColor: "#FFF59D", boxShadow: "0 0 80px #FF9800" }} />
      {/* Road */}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 550, backgroundColor: "#BCAAA4", borderTop: "10px solid #A5D6A7" }} />
      {/* Milestone */}
      <div style={{ position: "absolute", bottom: 480, right: 220, width: 140, height: 180, backgroundColor: "#ECEFF1", borderRadius: "70px 70px 0 0", border: "5px solid #37474F", textAlign: "center", paddingTop: 30 }}>
        <div style={{ fontSize: 26, fontWeight: 900, color: "#D32F2F" }}>SCHOOL</div>
        <div style={{ fontSize: 34, fontWeight: 900, color: "#263238" }}>5 KM</div>
      </div>
      {/* Bold 5 KM PAIDAL Text */}
      <div style={{ position: "absolute", top: 520, left: 0, right: 0, textAlign: "center" }}>
        <span style={{ fontSize: 72, fontWeight: 900, color: "#D84315", textShadow: "4px 4px 0 #FFF, 8px 8px 0 rgba(0,0,0,0.2)" }}>
          🏃‍♂️ 5 KM PAIDAL
        </span>
      </div>
      {/* Ravi walking with school bag */}
      <StickMan x={walkProgress} y={1140} scale={1.8} walkFrame={frame} armPose="walk" hasBag={true} />
      <SubtitleBox text="रोज़ सुबह वह 5 किलोमीटर पैदल स्कूल जाता था।" />
    </AbsoluteFill>
  );
};

const Scene3: React.FC<{ frame: number }> = ({ frame }) => {
  const glow = 20 + Math.sin(frame * 0.15) * 15;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(180deg, #1A237E 0%, #283593 50%, #303F9F 100%)" }}>
      {/* Ground */}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 500, backgroundColor: "#1B5E20" }} />
      {/* Glowing Magical Tree */}
      <svg style={{ position: "absolute", bottom: 420, right: 120, width: 550, height: 750 }}>
        <circle cx="275" cy="280" r={220 + glow} fill="rgba(255, 215, 0, 0.25)" filter="blur(30px)" />
        <rect x="235" y="380" width="80" height="340" fill="#5D4037" />
        <circle cx="275" cy="270" r="190" fill="#FFD700" stroke="#FFA000" strokeWidth="12" />
        <circle cx="220" cy="220" r="110" fill="#FFE082" />
        <circle cx="330" cy="230" r="110" fill="#FFE082" />
        {/* Magic Sparkles */}
        <circle cx="180" cy="180" r="12" fill="#FFF" />
        <circle cx="360" cy="280" r="10" fill="#FFF" />
        <circle cx="260" cy="140" r="14" fill="#FFF" />
      </svg>
      {/* Ravi in Wonder */}
      <StickMan x={300} y={1160} scale={1.8} walkFrame={0} armPose="wonder" />
      <SubtitleBox text="रास्ते में उसे एक पुराना, चमकता हुआ जादुई पेड़ मिला!" />
    </AbsoluteFill>
  );
};

const Scene4: React.FC<{ frame: number }> = ({ frame }) => {
  const seedFloat = Math.sin(frame * 0.2) * 20;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(180deg, #0D47A1 0%, #1976D2 70%, #2E7D32 100%)" }}>
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 500, backgroundColor: "#2E7D32" }} />
      {/* Tree */}
      <svg style={{ position: "absolute", bottom: 420, right: 80, width: 500, height: 700 }}>
        <rect x="210" y="340" width="80" height="340" fill="#5D4037" />
        <circle cx="250" cy="240" r="170" fill="#FFD700" stroke="#FFA000" strokeWidth="10" />
      </svg>
      {/* Tree Speech Bubble */}
      <div style={{ position: "absolute", top: 480, right: 280, backgroundColor: "#FFF", padding: "26px 40px", borderRadius: "30px", border: "5px solid #FFA000", maxWidth: 500, boxShadow: "0 10px 30px rgba(0,0,0,0.3)" }}>
        <p style={{ margin: 0, fontSize: 36, fontWeight: 900, color: "#D84315", lineHeight: 1.3 }}>
          "रवि, ये जादुई बीज लो! अपने सपने पूरे करो! 🌱✨"
        </p>
      </div>
      {/* Floating Magic Seed traveling toward Ravi */}
      <div style={{ position: "absolute", top: 920 + seedFloat, left: 450, width: 50, height: 50, borderRadius: "50%", backgroundColor: "#FFD700", boxShadow: "0 0 35px #FF6F00" }} />
      {/* Ravi Receiving */}
      <StickMan x={280} y={1160} scale={1.8} walkFrame={0} armPose="receive" hasSeed={true} />
      <SubtitleBox text="पेड़ ने कहा — 'रवि, ये जादुई बीज लो और सपने पूरे करो!'" />
    </AbsoluteFill>
  );
};

const Scene5: React.FC<{ frame: number }> = ({ frame }) => {
  // Tree growing height
  const growProgress = Math.min(1.0, frame / 180);
  const treeScale = 0.2 + growProgress * 1.3;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(180deg, #FFF9C4 0%, #FFE082 50%, #4CAF50 100%)" }}>
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 480, backgroundColor: "#5D4037" }} />
      {/* Golden Tree Growing */}
      <div style={{ position: "absolute", bottom: 440, left: "50%", transform: `translateX(-50%) scale(${treeScale})`, transformOrigin: "bottom center" }}>
        <svg width="600" height="800">
          <circle cx="300" cy="300" r="260" fill="rgba(255, 215, 0, 0.4)" filter="blur(40px)" />
          <rect x="250" y="400" width="100" height="380" fill="#FF8F00" />
          <circle cx="300" cy="280" r="230" fill="#FFD700" stroke="#FFF" strokeWidth="12" />
          <circle cx="230" cy="220" r="140" fill="#FFF176" />
          <circle cx="370" cy="220" r="140" fill="#FFF176" />
        </svg>
      </div>
      {/* Ravi Happy */}
      <StickMan x={220} y={1170} scale={1.8} walkFrame={0} armPose="wonder" isHappy={true} />
      <SubtitleBox text="रवि ने बीज बोया... अगले दिन सोने का पेड़ उगा! 🌟🌱" />
    </AbsoluteFill>
  );
};

const Scene6: React.FC<{ frame: number }> = ({ frame }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#E8F5E9" }}>
      {/* Sky & Tree Canopy */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 350, backgroundColor: "#C8E6C9" }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 600, backgroundColor: "#A5D6A7" }} />
      {/* Blackboard */}
      <div style={{ position: "absolute", top: 480, left: 340, width: 440, height: 280, backgroundColor: "#1B5E20", borderRadius: 16, border: "10px solid #5D4037", textAlign: "center", paddingTop: 40, color: "#FFF", fontSize: 48, fontWeight: 900 }}>
        <div>📖 क ख ग</div>
        <div style={{ fontSize: 32, marginTop: 20, color: "#FFD700" }}>गांव की पाठशाला</div>
      </div>
      {/* Ravi as Teacher */}
      <StickMan x={240} y={1150} scale={1.7} walkFrame={0} armPose="teach" />
      {/* 3 Student Stickmen */}
      <StickMan x={550} y={1220} scale={1.2} walkFrame={0} armPose="down" isHappy={true} />
      <StickMan x={720} y={1220} scale={1.2} walkFrame={0} armPose="down" isHappy={true} />
      <StickMan x={890} y={1220} scale={1.2} walkFrame={0} armPose="down" isHappy={true} />
      <SubtitleBox text="रवि ने उस पेड़ से गाँव के सब बच्चों को पढ़ाया! 📚" />
    </AbsoluteFill>
  );
};

const Scene7: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const pulse = 1.0 + Math.sin(frame * 0.25) * 0.08;
  return (
    <AbsoluteFill style={{ background: "linear-gradient(180deg, #1A237E 0%, #311B92 50%, #4A148C 100%)" }}>
      {/* Celebration Stars / Confetti */}
      <div style={{ position: "absolute", top: 260, left: 0, right: 0, textAlign: "center" }}>
        <h2 style={{ fontSize: 56, fontWeight: 900, color: "#FFD700", textShadow: "0 0 25px rgba(255,215,0,0.8)", margin: "0 0 20px 0" }}>
          MORAL OF THE STORY
        </h2>
        <h1 style={{ fontSize: 72, fontWeight: 900, color: "#FFFFFF", textShadow: "4px 4px 0 #000, 0 0 30px #00FFA3", margin: "0 40px", lineHeight: 1.3 }}>
          "मेहनत कभी बेकार नहीं जाती!" 💪✨
        </h1>
      </div>
      {/* Ravi Cheering */}
      <StickMan x={540} y={1120} scale={2.2} walkFrame={0} armPose="cheer" isHappy={true} />
      {/* FOLLOW KARO Button with Pulsing Animation */}
      <div style={{ position: "absolute", bottom: 220, left: "50%", transform: `translateX(-50%) scale(${pulse})`, zIndex: 60 }}>
        <button style={{ backgroundColor: "#E50914", color: "#FFF", fontSize: 52, fontWeight: 900, padding: "26px 80px", borderRadius: 60, border: "6px solid #FFF", boxShadow: "0 10px 40px rgba(229,9,20,0.6)", cursor: "pointer", display: "flex", alignItems: "center", gap: 20 }}>
          <span>💖 FOLLOW KARO 🔔</span>
        </button>
      </div>
      <SubtitleBox text="Moral: मेहनत कभी बेकार नहीं जाती! Follow Karo 💖" />
    </AbsoluteFill>
  );
};

// Reusable Subtitle Component
const SubtitleBox: React.FC<{ text: string }> = ({ text }) => {
  return (
    <div style={{ position: "absolute", bottom: 100, left: 40, right: 40, textAlign: "center", zIndex: 50 }}>
      <span style={{ backgroundColor: "rgba(0,0,0,0.85)", color: "#FFFFFF", padding: "18px 45px", borderRadius: 30, fontSize: 44, fontWeight: 900, lineHeight: 1.4, display: "inline-block", border: "3px solid #FFD700", boxShadow: "0 6px 20px rgba(0,0,0,0.5)" }}>
        {text}
      </span>
    </div>
  );
};
