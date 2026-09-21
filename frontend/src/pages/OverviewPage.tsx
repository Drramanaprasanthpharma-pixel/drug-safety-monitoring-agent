import { useEffect, useState } from "react";
import { api } from "../api";
import type { AuditEntry, DrugSummary } from "../types";
import { DrugPicker } from "../components/DrugPicker";
import { Icon } from "../components/icons";
import { DemoTag, EmptyState, Panel, Sev } from "../components/ui";
import { href, navigate } from "../lib/route";
import { useStore, type PickedDrug } from "../lib/store";
import { relativeTime } from "../lib/format";

export function OverviewPage() {
  const { lastReview, setDraft } = useStore();
  const [picked, setPicked] = useState<PickedDrug[]>([]);
  const [library, setLibrary] = useState<DrugSummary[] | null>(null);
  const [audit, setAudit] = useState<AuditEntry[] | null | "error">(null);
  const [demoError, setDemoError] = useState(false);

  useEffect(() => {
    let alive = true;
    api.searchDrugs("").then((r) => alive && setLibrary(r)).catch(() => alive && setLibrary([]));
    api.audit(6).then((r) => alive && setAudit(r)).catch(() => alive && setAudit("error"));
    return () => { alive = false; };
  }, []);

  const start = () => { setDraft({ drugs: picked, autoRun: true }); navigate("/review"); };
  const startDemo = async () => {
    setDemoError(false);
    try {
      const demo = await api.demo();
      const want = ["warfarin", "amiodarone"];
      const ids = want.every((w) => demo.demo_drugs.some((d) => d.id === w)) ? want : demo.demo_drugs.slice(0, 2).map((d) => d.id);
      const drugs: PickedDrug[] = ids.map((id) => ({ key: id, id, label: demo.demo_drugs.find((d) => d.id === id)?.generic_name ?? id }));
      setDraft({ drugs, patient: demo.demo_patient, demo: true, autoRun: true });
      navigate("/review");
    } catch { setDemoError(true); }
  };
  const rerun = (e: AuditEntry) => { setDraft({ drugs: e.drugs.map((d) => ({ key: d, id: d, label: d })), autoRun: true }); navigate("/review"); };

  const entries = Array.isArray(audit) ? audit : [];
  const lr = lastReview?.result;

  return (
    <div className="stack-lg">
      <section className="hero" aria-labelledby="hero-h">
        <div>
          <h1 id="hero-h">Check a medication list before it reaches the patient</h1>
          <p style={{ marginTop: 10 }}>
            Add one or more medications, with patient details if you have them, to get organ-toxicity priorities, interactions,
            monitoring parameters and red flags — each traced to its source.
          </p>
        </div>
        <div className="picker">
          <DrugPicker value={picked} onChange={setPicked} label="Medications to review" />
          <div className="row" style={{ marginTop: 16 }}>
            <button type="button" className="btn btn-primary" disabled={picked.length === 0} onClick={start}>
              <Icon name="play" size={16} />Start safety review
            </button>
            <button type="button" className="btn" onClick={startDemo}>Try the demo patient</button>
            {demoError && <span className="small" role="alert" style={{ color: "var(--crit)" }}>The demo could not be loaded.</span>}
          </div>
        </div>
      </section>

      <section className="panel stat-strip" aria-label="At a glance">
        <div className="stat"><div className="v">{library ? library.length : "—"}</div><div className="l">Medications in the curated library</div></div>
        <div className="stat"><div className="v">{Array.isArray(audit) ? audit.length : "—"}</div><div className="l">Recent reviews in the activity log</div></div>
        <div className="stat"><div className="v">{lr ? lr.red_flags.length : "—"}</div><div className="l">{lr ? "Red flags in your last review" : "Run a review to see red flags"}</div></div>
      </section>

      <div className="grid-main">
        <Panel title="Recent reviews" subtitle="From the activity log. Patient details are never stored." id="recent" flush
          actions={<a className="btn btn-sm btn-ghost" href={href("/activity")}>View all</a>}>
          {audit === null ? (
            <div className="panel-body"><span className="skel" style={{ width: "70%" }} /></div>
          ) : audit === "error" ? (
            <div className="panel-body muted">The activity log is unavailable right now.</div>
          ) : entries.length === 0 ? (
            <EmptyState icon="review" title="No reviews logged yet">Start a safety review above and it will appear here.</EmptyState>
          ) : (
            <ul className="list-rows">
              {entries.map((e) => (
                <li key={e.id} className="row-between">
                  <div>
                    <strong>{e.drugs.length ? e.drugs.join(" + ") : e.id}</strong>
                    <div className="row small muted">
                      <span>{relativeTime(e.timestamp)}</span>
                      {e.patientProvided !== null && <span>{e.patientProvided ? "With patient context" : "Drug-only"}</span>}
                      {e.demo && <DemoTag />}
                    </div>
                  </div>
                  {e.drugs.length > 0 && <button type="button" className="btn btn-sm" onClick={() => rerun(e)}>Run again</button>}
                </li>
              ))}
            </ul>
          )}
        </Panel>

        <div className="stack">
          {lr && (
            <Panel title="Your last review" id="last" actions={<Sev level={lr.overall_risk.category} />}>
              <p><strong>{lr.drugs_analyzed.join(", ")}</strong></p>
              <p className="muted small" style={{ margin: "4px 0 12px" }}>{lr.red_flags.length} red flags · {lr.interactions.length} interactions · score {lr.overall_risk.priority_score}/100</p>
              <a className="btn btn-sm" href={href("/review")}>Open review</a>
            </Panel>
          )}
          <Panel title="Drug library" subtitle="Curated reference monographs." id="lib" flush actions={<a className="btn btn-sm btn-ghost" href={href("/drugs")}>Browse</a>}>
            {library === null ? <div className="panel-body"><span className="skel" style={{ width: "60%" }} /></div> : (
              <ul className="list-rows">
                {library.slice(0, 6).map((d) => (
                  <li key={d.id}><a href={href(`/drugs/${encodeURIComponent(d.id)}`)} style={{ fontWeight: 600, textDecoration: "none" }}>{d.generic_name}</a><div className="small muted">{d.drug_class}</div></li>
                ))}
                {library.length === 0 && <li className="muted">The library could not be loaded.</li>}
              </ul>
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}
