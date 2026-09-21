import type {
  AdverseEffects, DiseaseInteraction, Evidence, InteractionResult, MonitoringRow, OrganToxicityDetail, PatientRiskFactor,
  PharmacistAction, RedFlag, VitalSignRow,
} from "../types";
import { Icon } from "./icons";
import { ConfTag, EmptyState, Sev } from "./ui";
import { downloadText, toCsv } from "../lib/csv";

export function RedFlagList({ flags }: { flags: RedFlag[] }) {
  if (!flags.length) return <EmptyState icon="check" title="No red flags raised">The rules engine found no contraindicated or major interactions, life-threatening effects, or compounding patient factors for this list.</EmptyState>;
  return (
    <ul className="list-rows" aria-label="Red flags">
      {flags.map((f, i) => (
        <li key={i} className="flag">
          <h3>{f.trigger}</h3>
          <p className="why">{f.consequence}</p>
          <p className="small">{f.immediate_consideration}</p>
          <p className="esc">{f.escalation}</p>
        </li>
      ))}
    </ul>
  );
}

export function InteractionList({ items }: { items: InteractionResult[] }) {
  if (!items.length) {
    return (
      <EmptyState icon="info" title="No drug–drug interactions matched">
        The service only reports pairs that exist in its curated ruleset and never guesses. No match is not proof that a combination is safe.
      </EmptyState>
    );
  }
  return (
    <div>
      {items.map((i, idx) => (
        <article key={idx} className="item">
          <div className="item-top">
            <h3>{i.drug_a} + {i.drug_b}</h3>
            <Sev level={i.severity} />
          </div>
          <div className="row">{i.mechanism.map((m) => <span className="tag" key={m}>{m}</span>)}</div>
          <p>{i.mechanism_detail}</p>
          <p><strong>Consequence:</strong> {i.clinical_consequence}</p>
          <p><strong>{i.recommended_action}:</strong> {i.action_detail}</p>
          <EvidenceLine e={i.evidence} />
        </article>
      ))}
    </div>
  );
}

export function EvidenceLine({ e }: { e: Evidence }) {
  return (
    <div className="row small muted evidence-line">
      <Icon name="book" size={14} />
      <span>{e.source}{e.reference ? ` — ${e.reference}` : ""}{e.date ? ` (${e.date})` : ""}</span>
      <ConfTag confidence={e.confidence} />
    </div>
  );
}

export function DiseaseInteractionList({ items }: { items: DiseaseInteraction[] }) {
  if (!items.length) return <p className="muted" style={{ padding: "4px 0" }}>No drug–disease matches. Add diagnoses in the patient context to check them.</p>;
  return (
    <div>
      {items.map((d, i) => (
        <article key={i} className="item">
          <h3>{d.drug} in {d.condition}</h3>
          <p>{d.risk}</p>
          <p><strong>Recommendation:</strong> {d.recommendation}</p>
          <EvidenceLine e={d.evidence} />
        </article>
      ))}
    </div>
  );
}

export function RiskFactorList({ items }: { items: PatientRiskFactor[] }) {
  if (!items.length) return <p className="muted">No patient-specific risk factors identified from the context provided.</p>;
  return (
    <div>
      {items.map((f, i) => (
        <article key={i} className="item">
          <div className="item-top"><h3>{f.factor}</h3>{f.affected_organ && <span className="tag">{f.affected_organ}</span>}</div>
          <p>{f.detail}</p>
        </article>
      ))}
    </div>
  );
}

const titleCase = (k: string) => { const s = k.replace(/_/g, " "); return s.charAt(0).toUpperCase() + s.slice(1); };

export function MonitoringSection({ rows, vitals, schedule, drugs }: {
  rows: MonitoringRow[]; vitals: VitalSignRow[]; schedule: Record<string, string[]>; drugs: string[];
}) {
  const exportCsv = () => {
    const head = ["Parameter", "Priority", "Why", "Baseline", "Follow-up", "Alert threshold", "Triggered by"];
    const body = rows.map((r) => [r.parameter, r.risk, r.why, r.baseline, r.follow_up, r.alert_threshold, r.triggered_by.join("; ")]);
    downloadText(`monitoring-plan-${drugs.join("-").toLowerCase().replace(/[^a-z0-9-]+/g, "")}.csv`, toCsv([head, ...body]));
  };
  return (
    <div className="stack-lg">
      <section className="panel" aria-labelledby="mon-h">
        <header className="panel-head">
          <div><h2 id="mon-h" style={{ fontSize: 18 }}>Monitoring parameters</h2><p>Only parameters relevant to the selected medications are listed.</p></div>
          {rows.length > 0 && <button type="button" className="btn btn-sm no-print" onClick={exportCsv}><Icon name="download" size={16} />Export CSV</button>}
        </header>
        {rows.length === 0 ? (
          <div className="panel-body muted">No monitoring parameters are defined for these medications.</div>
        ) : (
          <div className="table-wrap">
            <table className="rtable stack-mobile">
              <thead><tr><th>Parameter</th><th>Priority</th><th>Why</th><th>Baseline</th><th>Follow-up</th><th>Act when</th></tr></thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.parameter}>
                    <td data-label="Parameter"><strong>{r.parameter}</strong><div className="small muted">{r.triggered_by.join(", ")}</div></td>
                    <td data-label="Priority"><Sev level={r.risk} /></td>
                    <td data-label="Why" style={{ maxWidth: 320 }}>{r.why}</td>
                    <td data-label="Baseline">{r.baseline}</td>
                    <td data-label="Follow-up">{r.follow_up}</td>
                    <td data-label="Act when">{r.alert_threshold}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {Object.keys(schedule).length > 0 && (
        <section aria-labelledby="sched-h">
          <h2 id="sched-h" style={{ fontSize: 18, marginBottom: 12 }}>Monitoring schedule</h2>
          <div className="grid-3">
            {Object.entries(schedule).map(([k, items]) => (
              <div className="panel panel-pad" key={k}>
                <h3 style={{ marginBottom: 8 }}>{titleCase(k)}</h3>
                <ul className="bullets small">{items.map((t, i) => <li key={i}>{t}</li>)}</ul>
              </div>
            ))}
          </div>
        </section>
      )}

      {vitals.length > 0 && (
        <section className="panel" aria-labelledby="vit-h">
          <header className="panel-head"><h2 id="vit-h" style={{ fontSize: 18 }}>Vital signs</h2></header>
          <ul className="list-rows">
            {vitals.map((v) => (
              <li key={v.parameter}><strong>{v.parameter}</strong> <span className="muted">· {v.triggered_by.join(", ")}</span><p className="small muted">{v.why}</p></li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export function AdverseEffectsSection({ items, organs }: { items: AdverseEffects[]; organs: OrganToxicityDetail[] }) {
  return (
    <div className="stack-lg">
      {items.map((a) => (
        <section className="panel" key={a.drug} aria-label={`Adverse effects of ${a.drug}`}>
          <header className="panel-head"><h2 style={{ fontSize: 18 }}>{a.drug}</h2></header>
          <div className="panel-body stack">
            {a.boxed_warning && <div className="boxed"><strong>Boxed warning.</strong> {a.boxed_warning}</div>}
            <div className="ae-grid">
              <div className="ae-col"><h3><Sev level="Low" label="Common" /></h3><ul className="bullets small">{a.common.map((t) => <li key={t}>{t}</li>)}</ul></div>
              <div className="ae-col"><h3><Sev level="High" label="Serious" /></h3><ul className="bullets small">{a.serious.map((t) => <li key={t}>{t}</li>)}</ul></div>
              <div className="ae-col"><h3><Sev level="Critical" label="Life-threatening" /></h3><ul className="bullets small">{a.life_threatening.map((t) => <li key={t}>{t}</li>)}</ul></div>
            </div>
          </div>
        </section>
      ))}
      {organs.length > 0 && (
        <section className="panel" aria-labelledby="org-h">
          <header className="panel-head"><div><h2 id="org-h" style={{ fontSize: 18 }}>Organ toxicity by drug</h2><p>The per-drug facts behind the organ ranking.</p></div></header>
          <div className="table-wrap">
            <table className="rtable stack-mobile">
              <thead><tr><th>Drug</th><th>Organ</th><th>Level</th><th>Toxicity</th><th>Monitor</th><th>Frequency</th></tr></thead>
              <tbody>
                {organs.map((o, i) => (
                  <tr key={i}>
                    <td data-label="Drug"><strong>{o.drug}</strong></td><td data-label="Organ">{o.organ}</td><td data-label="Level"><Sev level={o.risk_level} /></td>
                    <td data-label="Toxicity">{o.toxicity}</td><td data-label="Monitor">{o.monitoring_parameters.join(", ")}</td><td data-label="Frequency">{o.frequency}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}

export function ActionsList({ items }: { items: PharmacistAction[] }) {
  return (
    <ul className="list-rows">
      {items.map((a, i) => (
        <li key={i} className="stack" style={{ gap: 6 }}>
          <h3>{a.action}</h3>
          <p className="small muted">{a.rationale}</p>
          {a.evidence && <EvidenceLine e={a.evidence} />}
        </li>
      ))}
    </ul>
  );
}

export function EvidenceList({ items }: { items: Evidence[] }) {
  if (!items.length) return <p className="muted">No evidence sources were attached to this review.</p>;
  return (
    <ul className="list-rows">
      {items.map((e, i) => (
        <li key={i}>
          <div className="item-top"><strong>{e.source}</strong><ConfTag confidence={e.confidence} /></div>
          <p className="small muted">{[e.reference, e.date].filter(Boolean).join(" · ") || "No further reference recorded"}</p>
        </li>
      ))}
    </ul>
  );
}
