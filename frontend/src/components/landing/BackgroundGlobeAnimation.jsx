import React, { useEffect, useRef } from 'react';

function randomSpherePoint() {
  const u = Math.random();
  const v = Math.random();
  const theta = 2 * Math.PI * u;
  const phi = Math.acos(2 * v - 1);

  return {
    x: Math.sin(phi) * Math.cos(theta),
    y: Math.cos(phi),
    z: Math.sin(phi) * Math.sin(theta),
  };
}

export default function BackgroundGlobeAnimation({ opacity = 0.15 }) {
  const canvasRef = useRef(null);
  const frameRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 2));
    const points = Array.from({ length: 180 }, () => randomSpherePoint());

    let width = 0;
    let height = 0;
    let radius = 0;
    let cx = 0;
    let cy = 0;
    let rot = 0;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;

      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      cx = width / 2;
      cy = height / 2;
      radius = Math.min(width, height) * 0.38;
    };

    const project = (p) => {
      const cos = Math.cos(rot);
      const sin = Math.sin(rot);

      const rx = p.x * cos - p.z * sin;
      const rz = p.x * sin + p.z * cos;
      const ry = p.y;

      const perspective = 1.55 / (1.55 + rz);

      return {
        x: cx + rx * radius * perspective,
        y: cy + ry * radius * perspective,
        z: rz,
        s: perspective,
      };
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      // Subtle glow background
      const glow = ctx.createRadialGradient(cx, cy, radius * 0.2, cx, cy, radius * 1.1);
      glow.addColorStop(0, `rgba(0, 220, 255, ${opacity * 0.08})`);
      glow.addColorStop(1, 'rgba(0, 220, 255, 0)');
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.1, 0, Math.PI * 2);
      ctx.fill();

      const projected = points.map(project);

      // Draw connections
      for (let i = 0; i < projected.length; i += 1) {
        const a = projected[i];
        for (let j = i + 1; j < projected.length; j += 1) {
          const b = projected[j];

          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < radius * 0.2) {
            const alpha = Math.max(opacity * 0.2, Math.min(opacity * 0.5, (opacity * 0.4) - dist / (radius * 1.2)));
            const depthFade = ((a.z + b.z) / 2 + 1) / 2;

            ctx.strokeStyle = `rgba(34, 211, 238, ${alpha * (0.4 + depthFade * 0.6)})`;
            ctx.lineWidth = 0.6;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }

      projected.sort((a, b) => a.z - b.z);

      // Draw dots
      for (const p of projected) {
        const depth = (p.z + 1) / 2;
        const size = 0.7 + p.s * 1.2;
        const alpha = opacity * (0.25 + depth * 0.35);

        ctx.fillStyle = `rgba(34, 211, 238, ${alpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fill();
      }

      // Draw subtle circle
      ctx.strokeStyle = `rgba(34, 211, 238, ${opacity * 0.3})`;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.stroke();

      rot += 0.0015;
      frameRef.current = requestAnimationFrame(draw);
    };

    resize();
    draw();
    window.addEventListener('resize', resize);

    return () => {
      cancelAnimationFrame(frameRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [opacity]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 h-full w-full pointer-events-none"
    />
  );
}
