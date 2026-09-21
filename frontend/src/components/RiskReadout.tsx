import type { Level, OverallRisk } from "../types";
import { AiTag, DemoTag } from "./ui";

/** Band edges mirror backend scoring_engine._category (Low <40, Moderate 40–64, High 65–84, Critical ≥85). */
const BANDS: { level: Level; from: number; to: number }[] = [
  { level: "Low", from: 0, to: 40 },
  { level: "Moderate", from: 40, to: 65 },
  { level: "High", from: 65, to: 85 },
  { level: "Critical", from: 85, to: 100 },
];

export function RiskReadout({ risk, drugs, demo }: { risk: OverallRisk; drugs: string[]; demo: boolean }) {
  const score = Math.max(0, Math.min(100, risk.priority_score));
  return (
    <section className="panel readout" aria-label="Overall review priority">
      <div>
        <p className="muted small" style={{ marginBottom: 6 }}>Overall review priority</p>
        <div className="readout-cat" data-level={risk.category}>{risk.category}</div>
        <p className="muted" style={{ marginTop: 10 }}>{drugs.join(", ")}</p>
        {demo && <div style={{ marginTop: 10 }}><DemoTag /></div>}
      </div>
      <div>
        <div className="scale" role="img" aria-label={`Priority score ${score} out of 100, category ${risk.category}. Low below 40, Moderate 40 to 64, High 65 to 84, Critical 85 and above.`}>
          <div className="scale-marker" style={{ left: `${score}%` }}>{score}</div>
          <div className="scale-bar">
            {BANDS.map((b) => (
              <div key={b.level} className="scale-seg" data-level={b.level} data-active={risk.category === b.level} style={{ flex: b.to - b.from }} />
            ))}
          </div>
          <div className="scale-labels" aria-hidden="true">
            {BANDS.map((b) => <span key={b.level} style={{ flex: b.to - b.from }}>{b.level}</span>)}
          </div>
        </div>
        <p style={{ marginTop: 16 }}>{risk.explanation}</p>
        <div className="row" style={{ marginTop: 12 }}>
          <AiTag>{risk.score_label}</AiTag>
        </div>
      </div>
    </section>
  );
}
