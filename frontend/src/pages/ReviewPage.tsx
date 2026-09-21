import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { api, ApiError } from "../api";
import type { AnalysisRequest, AnalysisResponse } from "../types";
import { DrugPicker } from "../components/DrugPicker";
import { Icon } from "../components/icons";
import { emptyPatient, draftToPatient, patientErrors, patientToDraft, PatientForm, type PatientDraft } from "../components/PatientForm";
import { RiskReadout } from "../components/RiskReadout";
import { OrganPriority } from "../components/OrganPriority";
import { ReviewPipeline } from "../components/ReviewPipeline";
import {
  ActionsList, AdverseEffectsSection, DiseaseInteractionList, EvidenceList, InteractionList, MonitoringSection, RedFlagList, RiskFactorList,
} from "../components/ResultSections";
import { ErrorState, LoadingState, Notice, PageHead, Panel, TabPanel, Tabs, type TabDef } from "../components/ui";
import { useStore, type PickedDrug } from "../lib/store";
import { plural } from "../lib/format";

type Status = { kind: "idle" } | { kind: "loading"; count: number } | { kind: "error"; message: string; detail: string } | { kind: "done" };

export function ReviewPage() {
  const { lastReview, setLastReview, draft, setDraft } = useStore();
  const [drugs, setDrugs] = useState<PickedDrug[]>(() => lastReview?.request.drugs.map((d) => ({ key: d, id: d, label: d })) ?? []);
  const [patient, setPatient] = useState<PatientDraft>(() => (lastReview?.request.patient ? patientToDraft(lastReview.request.patient) : emptyPatient()));
  const [showPatient, setShowPatient] = useState(() => !!lastReview?.request.patient);
  const [demo, setDemo] = useState(false);
  const [demoLabel, setDemoLabel] = useState("");
  const [status, setStatus] = useState<Status>(() => (lastReview ? { kind: "done" } : { kind: "idle" }));
  const [result, setResult] = useState<AnalysisResponse | null>(lastReview?.result ?? null);
  const [request, setRequest] = useState<AnalysisRequest | null>(lastReview?.request ?? null);
  const [tab, setTab] = useState("summary");
  const [formError, setFormError] = useState<string | null>(null);
  const resultsRef = useRef<HTMLHeadingElement>(null);
  const runId = useRef(0);
  const handledDraft = useRef<unknown>(null);

  const run = useCallback(async (d: PickedDrug[], p: PatientDraft, isDemo: boolean) => {
    const errs = patientErrors(p);
    if (d.length === 0) { setFormError("Add at least one medication to review."); return; }
    if (errs.length) { setFormError(errs.join(" ")); return; }
    setFormError(null);
    const req: AnalysisRequest = { drugs: d.map((x) => x.id ?? x.label), patient: draftToPatient(p), demo_mode: isDemo };
    const id = ++runId.current;
    setStatus({ kind: "loading", count: d.length });
    setTab("summary");
    try {
      const res = await api.analyze(req);
      if (id !== runId.current) return;
      setResult(res); setRequest(req); setStatus({ kind: "done" });
      setLastReview({ request: req, result: res, at: Date.now() });
      window.setTimeout(() => resultsRef.current?.focus(), 0);
    } catch (e) {
      if (id !== runId.current) return;
      const err = e instanceof ApiError ? e : new ApiError(0, "The review could not be completed.", "Unexpected error");
      setStatus({ kind: "error", message: err.message, detail: err.detail });
    }
  }, [setLastReview]);

  // Hand-off from Overview / Drug pages (prefill, optionally run straight away).
  useEffect(() => {
    if (!draft || handledDraft.current === draft) return;
    handledDraft.current = draft;
    const d = draft;
    setDraft(null);
    setDrugs(d.drugs);
    const p = d.patient ? patientToDraft(d.patient) : emptyPatient();
    setPatient(p); setShowPatient(!!d.patient); setDemo(!!d.demo);
    if (d.demo) api.demo().then((x) => setDemoLabel(x.label)).catch(() => setDemoLabel("Illustrative / Demo Data — not a real patient"));
    if (d.autoRun) void run(d.drugs, p, !!d.demo);
  }, [draft, setDraft, run]);

  const loadDemo = async () => {
    try {
      const x = await api.demo();
      const want = ["warfarin", "amiodarone"];
      const ids = want.every((w) => x.demo_drugs.some((d) => d.id === w)) ? want : x.demo_drugs.slice(0, 2).map((d) => d.id);
      setDrugs(ids.map((id) => ({ key: id, id, label: x.demo_drugs.find((d) => d.id === id)?.generic_name ?? id })));
      setPatient(patientToDraft(x.demo_patient)); setShowPatient(true); setDemo(true); setDemoLabel(x.label); setFormError(null);
    } catch { setFormError("The demo patient could not be loaded. Check that the service is reachable."); }
  };
  const clear = () => {
    runId.current++;
    setDrugs([]); setPatient(emptyPatient()); setShowPatient(false); setDemo(false); setResult(null); setRequest(null);
    setStatus({ kind: "idle" }); setFormError(null); setLastReview(null);
  };
  const edit = <T,>(setter: (v: T) => void) => (v: T) => { setter(v); setDemo(false); };
  const submit = (e: FormEvent) => { e.preventDefault(); void run(drugs, patient, demo); };
  const busy = status.kind === "loading";

  return (
    <div className="stack-lg">
      <PageHead title="Safety review" actions={<button type="button" className="btn" onClick={loadDemo}>Load demo patient</button>}>
        Enter the medications you are reviewing. Patient details are optional and sharpen the assessment.
      </PageHead>

      <form onSubmit={submit} className="stack no-print" aria-label="Safety review inputs" noValidate>
        {demo && <Notice tone="demo" icon="alert"><strong>Demo data.</strong> {demoLabel || "Illustrative / Demo Data — not a real patient"}</Notice>}
        <Panel title="Medications" id="meds">
          <DrugPicker value={drugs} onChange={edit(setDrugs)} hideLabel />
        </Panel>

        <section className="panel" aria-labelledby="ctx-h">
          <header className="panel-head">
            <div>
              <h2 id="ctx-h" style={{ fontSize: 18 }}>Patient context <span className="muted" style={{ fontWeight: 400, fontFamily: "var(--font-ui)", fontSize: 14 }}>(optional)</span></h2>
              <p>Not stored. Only drug names and a “patient context provided” flag are written to the activity log.</p>
            </div>
            <button type="button" className="btn btn-sm" aria-expanded={showPatient} aria-controls="ctx-body" onClick={() => setShowPatient((s) => !s)}>
              {showPatient ? "Hide" : "Add patient details"}
              <Icon name="down" size={16} style={{ transform: showPatient ? "rotate(180deg)" : undefined }} />
            </button>
          </header>
          {showPatient && <div className="panel-body" id="ctx-body"><PatientForm value={patient} onChange={edit(setPatient)} /></div>}
        </section>

        {formError && <Notice tone="bad" icon="alert">{formError}</Notice>}
        <div className="row">
          <button type="submit" className="btn btn-primary" disabled={busy}>
            <Icon name="play" size={16} />{busy ? "Running review…" : "Run safety review"}
          </button>
          <button type="button" className="btn btn-ghost" onClick={clear} disabled={busy}>Clear</button>
        </div>
      </form>

      <div aria-live="polite">
        {status.kind === "loading" && <LoadingState message={`Running the safety rules engine on ${plural(status.count, "medication")}…`} rows={2} />}
        {status.kind === "error" && (
          <div className="panel">
            <ErrorState title="Unable to complete the safety review" message={status.message} detail={status.detail} onRetry={() => void run(drugs, patient, demo)} />
          </div>
        )}
        {status.kind === "done" && result && request && (
          <Results result={result} request={request} headingRef={resultsRef} tab={tab} setTab={setTab} />
        )}
        {status.kind === "idle" && (
          <div className="panel"><div className="state">
            <div className="state-icon"><Icon name="review" size={24} /></div>
            <h2>No review yet</h2>
            <p>Add medications above and run a review to see risk priority, interactions, monitoring and red flags. Or load the demo patient to see an example.</p>
          </div></div>
        )}
      </div>
    </div>
  );
}

function Results({ result, request, headingRef, tab, setTab }: {
  result: AnalysisResponse; request: AnalysisRequest; headingRef: React.RefObject<HTMLHeadingElement>; tab: string; setTab: (t: string) => void;
}) {
  const r = result;
  const serious = r.interactions.some((i) => i.severity === "Contraindicated" || i.severity === "Major");
  const tabs: TabDef[] = [
    { id: "summary", label: "Summary", count: r.red_flags.length, alert: r.red_flags.length > 0 },
    { id: "interactions", label: "Interactions", count: r.interactions.length + r.disease_interactions.length, alert: serious },
    { id: "monitoring", label: "Monitoring", count: r.monitoring.length },
    { id: "adverse", label: "Adverse effects", count: r.adverse_effects.length },
    { id: "actions", label: "Actions and evidence", count: r.pharmacist_actions.length },
  ];
  return (
    <div className="stack-lg">
      <div className="row-between">
        <h2 ref={headingRef} tabIndex={-1} style={{ outline: "none" }}>Review results</h2>
        <button type="button" className="btn btn-sm no-print" onClick={() => window.print()}><Icon name="printer" size={16} />Print report</button>
      </div>
      {r.demo_mode && <Notice tone="demo" icon="alert"><strong>Demo data.</strong> This review used the illustrative demo patient, not a real person.</Notice>}
      <RiskReadout risk={r.overall_risk} drugs={r.drugs_analyzed} demo={r.demo_mode} />

      <div>
        <Tabs tabs={tabs} value={tab} onChange={setTab} idBase="res" label="Review sections" />

        <TabPanel idBase="res" id="summary" active={tab === "summary"}>
          <div className="grid-main">
            <div className="stack-lg">
              <Panel title="Red flags" subtitle="Items to raise with the prescriber first." id="flags" flush>
                <RedFlagList flags={r.red_flags} />
              </Panel>
              <Panel title="Organ systems to monitor" id="organs"><OrganPriority organs={r.priority_organs} /></Panel>
            </div>
            <div className="stack-lg">
              <Panel title="Suggested actions" id="top-actions" flush actions={r.pharmacist_actions.length > 4 ? <button type="button" className="btn btn-sm btn-ghost" onClick={() => setTab("actions")}>See all {r.pharmacist_actions.length}</button> : undefined}>
                <ActionsList items={r.pharmacist_actions.slice(0, 4)} />
              </Panel>
              <Panel title="How this review was produced" subtitle="Each stage is a deterministic rules-engine step reading the curated dataset." id="pipe">
                <ReviewPipeline result={r} request={request} />
              </Panel>
            </div>
          </div>
        </TabPanel>

        <TabPanel idBase="res" id="interactions" active={tab === "interactions"}>
          <div className="stack-lg">
            <Panel title="Drug–drug interactions" id="ddi" flush><InteractionList items={r.interactions} /></Panel>
            <Panel title="Drug–disease interactions" id="ddz" flush><div style={{ padding: r.disease_interactions.length ? 0 : 20 }}><DiseaseInteractionList items={r.disease_interactions} /></div></Panel>
            <Panel title="Patient risk factors" id="prf" flush><div style={{ padding: r.patient_risk_factors.length ? 0 : 20 }}><RiskFactorList items={r.patient_risk_factors} /></div></Panel>
          </div>
        </TabPanel>

        <TabPanel idBase="res" id="monitoring" active={tab === "monitoring"}>
          <MonitoringSection rows={r.monitoring} vitals={r.vital_signs} schedule={r.monitoring_schedule} drugs={r.drugs_analyzed} />
        </TabPanel>

        <TabPanel idBase="res" id="adverse" active={tab === "adverse"}>
          <AdverseEffectsSection items={r.adverse_effects} organs={r.organ_toxicity_detail} />
        </TabPanel>

        <TabPanel idBase="res" id="actions" active={tab === "actions"}>
          <div className="stack-lg">
            <Panel title="Suggested pharmacist actions" id="all-actions" flush><ActionsList items={r.pharmacist_actions} /></Panel>
            <Panel title="Evidence sources" subtitle="Where each recommendation comes from, with the dataset's confidence label." id="evidence" flush><EvidenceList items={r.evidence} /></Panel>
            <Notice icon="info">Audit reference <span className="mono">{r.audit_id}</span>. Only drug names and a patient-context flag were logged.</Notice>
          </div>
        </TabPanel>
      </div>
      <p className="small muted">{r.disclaimer}</p>
    </div>
  );
}
