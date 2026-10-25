import React from "react";

export type StickManProps = {
  x: number;
  y: number;
  scale?: number;
  walkFrame?: number;
  armPose?: "down" | "walk" | "wonder" | "receive" | "plant" | "teach" | "cheer";
  hasBag?: boolean;
  hasSeed?: boolean;
  color?: string;
  isHappy?: boolean;
};

export const StickMan: React.FC<StickManProps> = ({
  x,
  y,
  scale = 1.0,
  walkFrame = 0,
  armPose = "walk",
  hasBag = false,
  hasSeed = false,
  color = "#222222",
  isHappy = false,
}) => {
  // Walking cycle: 30 frames per full 2-step cycle (alternates every 15 frames)
  const cycle = (walkFrame % 30) / 30; // 0 to 1
  const legAngle = Math.sin(cycle * Math.PI * 2) * 28; // -28 to +28 degrees

  const headRadius = 26;
  const bodyLength = 95;
  const legLength = 90;
  const armLength = 70;

  // Neck / shoulders position
  const neckY = headRadius * 2;
  const hipY = neckY + bodyLength;

  // Leg positions based on legAngle
  const rad1 = (legAngle * Math.PI) / 180;
  const rad2 = (-legAngle * Math.PI) / 180;

  const leg1EndX = Math.sin(rad1) * legLength;
  const leg1EndY = hipY + Math.cos(rad1) * legLength;

  const leg2EndX = Math.sin(rad2) * legLength;
  const leg2EndY = hipY + Math.cos(rad2) * legLength;

  // Arm positions based on armPose
  let arm1EndX = -30, arm1EndY = neckY + 50;
  let arm2EndX = 30, arm2EndY = neckY + 50;

  if (armPose === "walk") {
    const armAngle = -legAngle * 0.9;
    const aRad1 = (armAngle * Math.PI) / 180;
    const aRad2 = (-armAngle * Math.PI) / 180;
    arm1EndX = Math.sin(aRad1) * armLength;
    arm1EndY = neckY + 20 + Math.cos(aRad1) * armLength;
    arm2EndX = Math.sin(aRad2) * armLength;
    arm2EndY = neckY + 20 + Math.cos(aRad2) * armLength;
  } else if (armPose === "wonder") {
    arm1EndX = -45; arm1EndY = neckY - 20;
    arm2EndX = 45; arm2EndY = neckY - 20;
  } else if (armPose === "receive") {
    arm1EndX = 25; arm1EndY = neckY + 15;
    arm2EndX = 55; arm2EndY = neckY + 15;
  } else if (armPose === "plant") {
    arm1EndX = -20; arm1EndY = hipY + 10;
    arm2EndX = 20; arm2EndY = hipY + 10;
  } else if (armPose === "teach") {
    arm1EndX = -20; arm1EndY = neckY + 40;
    arm2EndX = 65; arm2EndY = neckY - 30; // pointing up at board
  } else if (armPose === "cheer") {
    arm1EndX = -45; arm1EndY = neckY - 45;
    arm2EndX = 45; arm2EndY = neckY - 45;
  }

  return (
    <svg
      style={{
        position: "absolute",
        left: x - 100 * scale,
        top: y - 100 * scale,
        width: 200 * scale,
        height: 320 * scale,
        overflow: "visible",
      }}
      viewBox="-100 0 200 320"
    >
      {/* Head */}
      <circle cx="0" cy={headRadius} r={headRadius} fill="none" stroke={color} strokeWidth="6" />

      {/* Eyes & Smile */}
      <circle cx="-8" cy={headRadius - 4} r="3" fill={color} />
      <circle cx="8" cy={headRadius - 4} r="3" fill={color} />
      {isHappy ? (
        <path d={`M -10 ${headRadius + 8} Q 0 ${headRadius + 18} 10 ${headRadius + 8}`} fill="none" stroke={color} strokeWidth="3" />
      ) : (
        <line x1="-8" y1={headRadius + 10} x2="8" y2={headRadius + 10} stroke={color} strokeWidth="3" />
      )}

      {/* Backpack if school */}
      {hasBag && (
        <rect x="-28" y={neckY + 15} width="22" height="45" rx="6" fill="#E65100" stroke="#BF360C" strokeWidth="3" />
      )}

      {/* Body Spine */}
      <line x1="0" y1={neckY} x2="0" y2={hipY} stroke={color} strokeWidth="7" strokeLinecap="round" />

      {/* Left Arm */}
      <line x1="0" y1={neckY + 15} x2={arm1EndX} y2={arm1EndY} stroke={color} strokeWidth="6" strokeLinecap="round" />

      {/* Right Arm */}
      <line x1="0" y1={neckY + 15} x2={arm2EndX} y2={arm2EndY} stroke={color} strokeWidth="6" strokeLinecap="round" />

      {/* Magic Seed in hand */}
      {hasSeed && (
        <circle cx={arm2EndX + 8} cy={arm2EndY - 4} r="9" fill="#FFD700" stroke="#FF8F00" strokeWidth="2" />
      )}

      {/* Left Leg */}
      <line x1="0" y1={hipY} x2={leg1EndX} y2={leg1EndY} stroke={color} strokeWidth="7" strokeLinecap="round" />

      {/* Right Leg */}
      <line x1="0" y1={hipY} x2={leg2EndX} y2={leg2EndY} stroke={color} strokeWidth="7" strokeLinecap="round" />
    </svg>
  );
};
