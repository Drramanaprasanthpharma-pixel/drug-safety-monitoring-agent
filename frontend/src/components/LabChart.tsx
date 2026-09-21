import type { LabTrendPoint } from "../types";

/** Plots exactly the points the user entered (no smoothing, no extrapolation). */
export function LabChart({ points, parameter, unit }: { points: LabTrendPoint[]; parameter: string; unit?: string }) {
  const pts = [...points].sort((a, b) => a.day - b.day);
  const W = 460, H = 280, P = { l: 50, r: 18, t: 32, b: 44 };
  const xs = pts.map((p) => p.day), ys = pts.map((p) => p.value);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const rawMin = Math.min(...ys), rawMax = Math.max(...ys);
  const pad = (rawMax - rawMin || Math.abs(rawMax) || 1) * 0.2;
  const y0 = rawMin - pad, y1 = rawMax + pad;
  const sx = (x: number) => P.l + (x1 === x0 ? (W - P.l - P.r) / 2 : ((x - x0) / (x1 - x0)) * (W - P.l - P.r));
  const sy = (y: number) => H - P.b - ((y - y0) / (y1 - y0)) * (H - P.t - P.b);
  const ticks = Array.from({ length: 4 }, (_, i) => y0 + ((y1 - y0) * i) / 3);
  const fmt = (v: number) => (Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 10 ? v.toFixed(1) : v.toFixed(2));
  const summary = `${parameter} over ${x1 - x0} days: ${pts.map((p) => `day ${p.day} ${p.value}`).join(", ")}${unit ? ` ${unit}` : ""}`;

  return (
    <figure style={{ margin: 0 }}>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={summary}>
        {ticks.map((t, i) => (
          <g key={i}>
            <line className="grid" x1={P.l} x2={W - P.r} y1={sy(t)} y2={sy(t)} />
            <text x={P.l - 8} y={sy(t) + 4} textAnchor="end">{fmt(t)}</text>
          </g>
        ))}
        <line className="axis" x1={P.l} x2={W - P.r} y1={H - P.b} y2={H - P.b} />
        {pts.length > 1 && <polyline className="series" points={pts.map((p) => `${sx(p.day)},${sy(p.value)}`).join(" ")} />}
        {pts.map((p, i) => (
          <g key={i}>
            <circle className="pt" cx={sx(p.day)} cy={sy(p.value)} r={5} />
            <text x={sx(p.day)} y={H - P.b + 18} textAnchor="middle">{p.day}</text>
          </g>
        ))}
        <text x={(P.l + W - P.r) / 2} y={H - 4} textAnchor="middle">Day</text>
        {unit && <text x={4} y={13}>{unit}</text>}
      </svg>
    </figure>
  );
}
