import { useState, type FormEvent } from "react";
import { api, ApiError } from "../api";
import type { LabTrendAssessment, LabTrendPoint } from "../types";
import { Icon } from "../components/icons";
import { LabChart } from "../components/LabChart";
import { ErrorState, LoadingState, Notice, PageHead, Panel, RulesTag, Sev } from "../components/ui";

/** Parameters the trend engine knows a “concerning direction” for. */
const PARAMS: { id: string; label: string; unit: string }[] = [
  { id: "creatinine", label: "Creatinine", unit: "mg/dL" }, { id: "egfr", label: "eGFR", unit: "mL/min/1.73 m²" },
  { id: "potassium", label: "Potassium", unit: "mEq/L" }, { id: "sodium", label: "Sodium", unit: "mEq/L" },
  { id: "inr", label: "INR", unit: "" }, { id: "alt", label: "ALT", unit: "U/L" }, { id: "ast", label: "AST", unit: "U/L" },
  { id: "bilirubin", label: "Bilirubin", unit: "mg/dL" }, { id: "hemoglobin", label: "Hemoglobin", unit: "g/dL" },
  { id: "platelets", label: "Platelets", unit: "×10³/µL" }, { id: "wbc", label: "WBC", unit: "×10³/µL" },
];
type Row = { day: string; value: string };
const EXAMPLE: Row[] = [{ day: "0", value: "0.9" }, { day: "7", value: "1.1" }, { day: "14", value: "1.4" }, { day: "21", value: "1.8" }];

export function LabTrendsPage() {
  const [param, setParam] = useState("creatinine");
  const [rows, setRows] = useState<Row[]>([{ day: "", value: "" }, { day: "", value: "" }]);
  const [state, setState] = useState<{ kind: "idle" } | { kind: "loading" } | { kind: "error"; message: string; detail: string } | { kind: "done"; res: LabTrendAssessment; pts: LabTrendPoint[]; param: string }>({ kind: "idle" });
  const [formError, setFormError] = useState<string | null>(null);
  const unit = PARAMS.find((p) => p.id === param)?.unit ?? "";

  const parse = (): LabTrendPoint[] | null => {
    const pts: LabTrendPoint[] = [];
    for (const r of rows) {
      if (r.day.trim() === "" && r.value.trim() === "") continue;
      const day = Number(r.day), value = Number(r.value);
      if (r.day.trim() === "" || r.value.trim() === "" || !Number.isInteger(day) || day < 0 || !Number.isFinite(value)) return null;
      pts.push({ day, value });
    }
    return pts;
  };

  const run = async (e?: FormEvent) => {
    e?.preventDefault();
    const pts = parse();
    if (!pts) { setFormError("Each row needs a whole-number day (0 or more) and a numeric value."); return; }
    if (pts.length === 0) { setFormError("Enter at least one measurement."); return; }
    setFormError(null); setState({ kind: "loading" });
    try {
      const res = await api.labTrend({ parameter: param, unit: unit || null, points: pts });
      setState({ kind: "done", res, pts, param });
    } catch (err) {
      const a = err instanceof ApiError ? err : new ApiError(0, "The trend could not be assessed.", "Unexpected error");
      setState({ kind: "error", message: a.message, detail: a.detail });
    }
  };
  const setRow = (i: number, patch: Partial<Row>) => setRows(rows.map((r, j) => (j === i ? { ...r, ...patch } : r)));

  return (
    <div className="stack-lg">
      <PageHead title="Lab trends" actions={<button type="button" className="btn" onClick={() => { setParam("creatinine"); setRows(EXAMPLE); setFormError(null); }}>Fill example values</button>}>
        Enter serial measurements to check whether the direction and size of change is a concern for that parameter.
      </PageHead>

      <div className="grid-main">
        <form className="panel" onSubmit={run} noValidate aria-label="Lab trend inputs">
          <div className="panel-head"><h2 style={{ fontSize: 18 }}>Measurements</h2></div>
          <div className="panel-body stack">
            <div className="field">
              <label htmlFor="lt-param">Parameter</label>
              <select id="lt-param" className="select" value={param} onChange={(e) => setParam(e.target.value)}>
                {PARAMS.map((p) => <option key={p.id} value={p.id}>{p.label}{p.unit ? ` (${p.unit})` : ""}</option>)}
              </select>
            </div>
            <div className="pts">
              {rows.map((r, i) => (
                <div className="pt-row" key={i}>
                  <div className="field"><label htmlFor={`lt-d${i}`}>{i === 0 ? "Day" : <span className="sr-only">Day</span>}</label>
                    <input id={`lt-d${i}`} className="input" type="number" inputMode="numeric" min={0} step={1} placeholder="Day" value={r.day} onChange={(e) => setRow(i, { day: e.target.value })} /></div>
                  <div className="field"><label htmlFor={`lt-v${i}`}>{i === 0 ? `Value${unit ? ` (${unit})` : ""}` : <span className="sr-only">Value</span>}</label>
                    <input id={`lt-v${i}`} className="input" type="number" inputMode="decimal" step="any" placeholder="Value" value={r.value} onChange={(e) => setRow(i, { value: e.target.value })} /></div>
                  <button type="button" className="icon-btn" aria-label={`Remove measurement ${i + 1}`} disabled={rows.length <= 1} onClick={() => setRows(rows.filter((_, j) => j !== i))}><Icon name="trash" size={18} /></button>
                </div>
              ))}
            </div>
            <div className="row">
              <button type="button" className="btn btn-sm" onClick={() => setRows([...rows, { day: "", value: "" }])}><Icon name="plus" size={16} />Add measurement</button>
            </div>
            {formError && <Notice tone="bad" icon="alert">{formError}</Notice>}
            <div><button type="submit" className="btn btn-primary" disabled={state.kind === "loading"}><Icon name="trend" size={16} />Assess trend</button></div>
          </div>
        </form>

        <div aria-live="polite">
          {state.kind === "idle" && <div className="panel"><div className="state"><div className="state-icon"><Icon name="trend" size={24} /></div><h2>No trend assessed yet</h2><p>Add at least two measurements to see the direction of change and whether it needs clinical attention.</p></div></div>}
          {state.kind === "loading" && <LoadingState message="Assessing the trend…" rows={1} />}
          {state.kind === "error" && <div className="panel"><ErrorState title="Unable to assess this trend" message={state.message} detail={state.detail} onRetry={() => void run()} homeLink={false} /></div>}
          {state.kind === "done" && (
            <Panel title="Assessment" id="lt-res" actions={<RulesTag />}>
              <div className="stack">
                <div className="row-between">
                  <div><p className="muted small">Trend</p><p style={{ font: "600 26px/1.2 var(--font-serif)" }}>{state.res.trend}</p></div>
                  <Sev level={state.res.clinically_significant_change ? "High" : "Low"} label={state.res.clinically_significant_change ? "Clinically significant change" : "No concerning change"} />
                </div>
                <p>{state.res.note}</p>
                {state.pts.length > 0 && <LabChart points={state.pts} parameter={PARAMS.find((p) => p.id === state.param)?.label ?? state.param} unit={PARAMS.find((p) => p.id === state.param)?.unit} />}
                <p className="hint">Coarse heuristic: a change of 20% or more in the concerning direction is flagged. It is not a parameter-specific clinical threshold — correlate clinically.</p>
              </div>
            </Panel>
          )}
        </div>
      </div>
    </div>
  );
}
