import { useEffect, type ReactNode } from "react";
import { api, ApiError } from "../api";
import type { DrugDetail } from "../types";
import { Icon } from "../components/icons";
import { EvidenceList } from "../components/ResultSections";
import { EmptyState, ErrorState, LoadingState, Notice, PageHead, Panel, RulesTag, Sev } from "../components/ui";
import { useAsync } from "../lib/hooks";
import { href, navigate } from "../lib/route";
import { useStore } from "../lib/store";

/** Fields rendered by dedicated sections; everything else in the record is shown generically below. */
const KNOWN = new Set([
  "id", "generic_name", "brand_names", "drug_class", "boxed_warning", "contraindications", "renal_dosing", "organ_toxicity",
  "monitoring_parameters", "vital_signs", "adverse_effects", "evidence",
]);
const label = (k: string) => { const s = k.replace(/_/g, " "); return s.charAt(0).toUpperCase() + s.slice(1); };

function Generic({ value, depth = 0 }: { value: unknown; depth?: number }): ReactNode {
  if (value === null || value === undefined || value === "") return <span className="muted">—</span>;
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return <>{String(value)}</>;
  if (Array.isArray(value)) {
    if (value.every((v) => typeof v !== "object" || v === null)) return <ul className="bullets">{value.map((v, i) => <li key={i}>{String(v)}</li>)}</ul>;
    return <div className="stack">{value.map((v, i) => <div key={i} className="callout-ai" style={{ background: "var(--canvas)", borderColor: "var(--line)", color: "inherit" }}><Generic value={v} depth={depth + 1} /></div>)}</div>;
  }
  if (typeof value === "object" && depth < 3) {
    return (
      <dl className="kv">
        {Object.entries(value as Record<string, unknown>).map(([k, v]) => (<div key={k} style={{ display: "contents" }}><dt>{label(k)}</dt><dd><Generic value={v} depth={depth + 1} /></dd></div>))}
      </dl>
    );
  }
  return <span className="mono small">{JSON.stringify(value)}</span>;
}

export function DrugProfilePage({ id, onLoaded }: { id: string; onLoaded: (name: string) => void }) {
  const { setDraft } = useStore();
  const { data, error, loading, retry } = useAsync<DrugDetail>(() => api.drug(id), [id]);
  useEffect(() => { if (data) onLoaded(data.generic_name); return () => onLoaded(""); }, [data, onLoaded]);

  if (loading) return <LoadingState message="Loading drug profile…" rows={3} />;
  if (error != null || !data) {
    const notFound = error instanceof ApiError && error.status === 404;
    return (
      <div className="panel">
        {notFound
          ? <EmptyState icon="search" title="This drug is not in the library" action={<a className="btn" href={href("/drugs")}>Browse the drug library</a>}>“{id}” isn’t in the curated dataset. Only the listed medications can be reviewed.</EmptyState>
          : <ErrorState title="Unable to load this drug profile" message={error instanceof ApiError ? error.message : "The profile could not be loaded."} detail={error instanceof ApiError ? error.detail : undefined} onRetry={retry} />}
      </div>
    );
  }

  const d = data;
  const other = Object.entries(d).filter(([k, v]) => !KNOWN.has(k) && v !== null && v !== undefined && v !== "" && !(Array.isArray(v) && v.length === 0));
  const ae = d.adverse_effects;

  return (
    <div className="stack-lg">
      <PageHead
        title={d.generic_name}
        actions={
          <>
            <button type="button" className="btn btn-primary" onClick={() => { setDraft({ drugs: [{ key: d.id, id: d.id, label: d.generic_name }], autoRun: true }); navigate("/review"); }}><Icon name="play" size={16} />Start safety review</button>
            <button type="button" className="btn no-print" onClick={() => window.print()}><Icon name="printer" size={16} />Print</button>
          </>
        }
      >
        {d.drug_class}{d.brand_names?.length ? ` · Brand names: ${d.brand_names.join(", ")}` : ""}
      </PageHead>
      <div className="row"><RulesTag /><span className="small muted">Reference data from the curated dataset — verify against current prescribing information.</span></div>

      {d.boxed_warning && <Notice tone="bad" icon="alert"><strong>Boxed warning.</strong> {d.boxed_warning}</Notice>}

      <div className="grid-main">
        <div className="stack-lg">
          {ae && (
            <Panel title="Adverse effects" id="ae">
              <div className="ae-grid">
                <div className="ae-col"><h3><Sev level="Low" label="Common" /></h3><ul className="bullets small">{ae.common.map((t) => <li key={t}>{t}</li>)}</ul></div>
                <div className="ae-col"><h3><Sev level="High" label="Serious" /></h3><ul className="bullets small">{ae.serious.map((t) => <li key={t}>{t}</li>)}</ul></div>
                <div className="ae-col"><h3><Sev level="Critical" label="Life-threatening" /></h3><ul className="bullets small">{ae.life_threatening.map((t) => <li key={t}>{t}</li>)}</ul></div>
              </div>
            </Panel>
          )}
          {d.organ_toxicity && d.organ_toxicity.length > 0 && (
            <Panel title="Organ toxicity" id="ot" flush>
              <ul className="list-rows">
                {d.organ_toxicity.map((o, i) => (
                  <li key={i} className="stack" style={{ gap: 6 }}>
                    <div className="item-top"><h3>{o.organ}</h3><Sev level={o.risk_level} /></div>
                    <p>{o.toxicity} — <span className="muted">{o.reason}</span></p>
                    <p className="small muted">Monitor {o.monitoring_parameters.join(", ")} · {o.frequency} · Act when: {o.thresholds}</p>
                    <p className="small muted">Source: {o.source}</p>
                  </li>
                ))}
              </ul>
            </Panel>
          )}
          {d.monitoring_parameters && d.monitoring_parameters.length > 0 && (
            <Panel title="Monitoring parameters" id="mp" flush>
              <div className="table-wrap">
                <table className="rtable stack-mobile">
                  <thead><tr><th>Parameter</th><th>Priority</th><th>Baseline</th><th>Follow-up</th><th>Act when</th></tr></thead>
                  <tbody>
                    {d.monitoring_parameters.map((m) => (
                      <tr key={m.parameter}>
                        <td data-label="Parameter"><strong>{m.parameter}</strong><div className="small muted">{m.why}</div></td>
                        <td data-label="Priority"><Sev level={m.risk} /></td><td data-label="Baseline">{m.baseline}</td><td data-label="Follow-up">{m.follow_up}</td><td data-label="Act when">{m.alert_threshold}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>
          )}
          {other.map(([k, v]) => (<Panel key={k} title={label(k)} id={`o-${k}`}><Generic value={v} /></Panel>))}
        </div>

        <div className="stack-lg">
          {(d.contraindications?.length || d.renal_dosing) && (
            <Panel title="Use and dosing cautions" id="cx">
              <div className="stack">
                {d.contraindications && d.contraindications.length > 0 && <div><h3 style={{ marginBottom: 6 }}>Contraindications</h3><ul className="bullets">{d.contraindications.map((c) => <li key={c}>{c}</li>)}</ul></div>}
                {d.renal_dosing && <div><h3 style={{ marginBottom: 6 }}>Renal dosing</h3><p>{d.renal_dosing}</p></div>}
              </div>
            </Panel>
          )}
          {d.vital_signs && d.vital_signs.length > 0 && (
            <Panel title="Vital signs to watch" id="vs" flush>
              <ul className="list-rows">{d.vital_signs.map((v) => <li key={v.parameter}><strong>{v.parameter}</strong><p className="small muted">{v.why}</p></li>)}</ul>
            </Panel>
          )}
          {d.evidence && <Panel title="Evidence sources" id="ev" flush><EvidenceList items={d.evidence} /></Panel>}
        </div>
      </div>
    </div>
  );
}
