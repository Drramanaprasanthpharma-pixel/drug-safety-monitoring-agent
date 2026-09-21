import type { PriorityOrgan } from "../types";
import { ConfTag, Sev } from "./ui";

export function OrganPriority({ organs }: { organs: PriorityOrgan[] }) {
  if (!organs.length) return <p className="muted">No organ-system toxicity was identified for the selected medications.</p>;
  return (
    <div className="stack">
      <p className="hint">{organs[0].percent_label}. Scale is 0–100.</p>
      <div className="bars">
        {organs.map((o) => (
          <details className="bar-row" key={o.organ}>
            <summary>
              <div className="bar-top">
                <span className="bar-name">{o.organ}<Sev level={o.priority} /></span>
                <span className="mono" aria-label={`Relative priority ${o.relative_priority_percent} out of 100`}>{o.relative_priority_percent}<span className="muted">/100</span></span>
              </div>
              <div className="bar-track" aria-hidden="true">
                <div className="bar-fill" data-level={o.priority} style={{ ["--w" as string]: `${o.relative_priority_percent}%` }} />
              </div>
              <span className="hint">Show basis</span>
            </summary>
            <div className="bar-detail">
              <div><strong>Why:</strong> {o.reason}</div>
              {o.toxicity && <div><strong>Toxicity:</strong> {o.toxicity}</div>}
              {o.monitoring_parameters.length > 0 && <div><strong>Monitor:</strong> {o.monitoring_parameters.join(", ")}</div>}
              <div><strong>Frequency:</strong> {o.monitoring_frequency}</div>
              {o.intervention_threshold && <div><strong>Act when:</strong> {o.intervention_threshold}</div>}
              {o.evidence && <div className="row"><span className="muted">{o.evidence.source}</span><ConfTag confidence={o.evidence.confidence} /></div>}
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}
