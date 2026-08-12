"use client";

import React, { useEffect, useRef } from "react";
import { CrowdAgent } from "@/types/crowd";

interface CrowdAgentLayerProps {
  agents: CrowdAgent[];
  width: number;
  height: number;
  showUserOnly?: boolean;
}

export const CrowdAgentLayer: React.FC<CrowdAgentLayerProps> = ({
  agents,
  width,
  height,
  showUserOnly = false,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameId = useRef<number | null>(null);
  const localAgentsRef = useRef<CrowdAgent[]>([]);

  useEffect(() => {
    localAgentsRef.current = [...agents];
  }, [agents]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let pulseTime = 0;

    const render = () => {
      pulseTime += 0.05;
      ctx.clearRect(0, 0, width, height);

      const currentAgents = localAgentsRef.current;

      for (let i = 0; i < currentAgents.length; i++) {
        const agent = currentAgents[i];

        if (showUserOnly && !agent.isUser) continue;

        // Move agents slightly inside boundaries
        agent.x += agent.vx;
        agent.y += agent.vy;

        // Bounce back if near limits
        if (agent.x <= 40 || agent.x >= width - 40) agent.vx *= -1;
        if (agent.y <= 40 || agent.y >= height - 40) agent.vy *= -1;

        if (agent.isUser) {
          // Render Demo User Alex Sharma with glowing cyan ring
          const glowRadius = 8 + Math.sin(pulseTime) * 3;
          
          // Outer glow
          ctx.beginPath();
          ctx.arc(agent.x, agent.y, glowRadius + 4, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(0, 240, 255, 0.25)";
          ctx.fill();

          ctx.beginPath();
          ctx.arc(agent.x, agent.y, glowRadius, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(0, 240, 255, 0.5)";
          ctx.fill();

          // Inner solid dot
          ctx.beginPath();
          ctx.arc(agent.x, agent.y, 5, 0, Math.PI * 2);
          ctx.fillStyle = "#00f0ff";
          ctx.shadowColor = "#00f0ff";
          ctx.shadowBlur = 12;
          ctx.fill();
          ctx.shadowBlur = 0;
        } else {
          // Regular anonymous crowd particle
          ctx.beginPath();
          ctx.arc(agent.x, agent.y, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(148, 163, 184, 0.6)";
          ctx.fill();
        }
      }

      animFrameId.current = requestAnimationFrame(render);
    };

    animFrameId.current = requestAnimationFrame(render);

    return () => {
      if (animFrameId.current) {
        cancelAnimationFrame(animFrameId.current);
      }
    };
  }, [width, height, showUserOnly]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="absolute inset-0 pointer-events-none z-10"
    />
  );
};
