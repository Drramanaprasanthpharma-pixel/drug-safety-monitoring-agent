import { useId, useState, type KeyboardEvent } from "react";
import { Icon } from "./icons";
import type { PatientInfo } from "../types";

export interface PatientDraft {
  age: string; sex: "" | NonNullable<PatientInfo["sex"]>; weight: string; egfr: string;
  hepatic: "" | NonNullable<PatientInfo["hepatic_impairment"]>; pregnant: boolean;
  diagnoses: string[]; allergies: string[]; meds: string[]; labs: { name: string; value: string }[];
}

export const emptyPatient = (): PatientDraft => ({
  age: "", sex: "", weight: "", egfr: "", hepatic: "", pregnant: false, diagnoses: [], allergies: [], meds: [], labs: [],
});

export function patientToDraft(p: PatientInfo): PatientDraft {
  return {
    age: p.age != null ? String(p.age) : "", sex: p.sex ?? "", weight: p.weight_kg != null ? String(p.weight_kg) : "",
    egfr: p.egfr != null ? String(p.egfr) : "", hepatic: p.hepatic_impairment ?? "", pregnant: !!p.pregnant,
    diagnoses: [...(p.diagnoses ?? [])], allergies: [...(p.allergies ?? [])], meds: [...(p.current_medications ?? [])],
    labs: Object.entries(p.lab_values ?? {}).map(([name, value]) => ({ name, value: String(value) })),
  };
}

const num = (s: string) => (s.trim() === "" || !Number.isFinite(Number(s)) ? null : Number(s));

/** Returns null when nothing was entered, so a drug-only review is sent without patient context. */
export function draftToPatient(d: PatientDraft): PatientInfo | null {
  const lab_values: Record<string, number> = {};
  for (const l of d.labs) { const v = num(l.value); if (l.name.trim() && v !== null) lab_values[l.name.trim().toLowerCase()] = v; }
  const p: PatientInfo = {
    age: num(d.age), sex: d.sex || null, weight_kg: num(d.weight), egfr: num(d.egfr), hepatic_impairment: d.hepatic || null,
    pregnant: d.pregnant ? true : null, diagnoses: d.diagnoses, allergies: d.allergies, current_medications: d.meds, lab_values,
  };
  const any = p.age !== null || p.sex || p.weight_kg !== null || p.egfr !== null || p.hepatic_impairment || p.pregnant ||
    d.diagnoses.length || d.allergies.length || d.meds.length || Object.keys(lab_values).length;
  return any ? p : null;
}

export function patientErrors(d: PatientDraft): string[] {
  const out: string[] = [];
  const chk = (label: string, s: string, lo: number, hi: number, loExclusive = false) => {
    const v = num(s);
    if (s.trim() !== "" && (v === null || (loExclusive ? v <= lo : v < lo) || v > hi)) out.push(`${label} must be between ${loExclusive ? "above " : ""}${lo} and ${hi}.`);
  };
  chk("Age", d.age, 0, 120); chk("Weight", d.weight, 0, 500, true); chk("eGFR", d.egfr, 0, 200);
  return out;
}

function TagInput({ label, values, onChange, placeholder, hint }: {
  label: string; values: string[]; onChange: (v: string[]) => void; placeholder: string; hint?: string;
}) {
  const [text, setText] = useState("");
  const id = useId();
  const commit = () => {
    const t = text.trim().replace(/,$/, "");
    if (t && !values.some((v) => v.toLowerCase() === t.toLowerCase())) onChange([...values, t]);
    setText("");
  };
  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") { if (text.trim()) { e.preventDefault(); commit(); } }
    else if (e.key === "Backspace" && !text && values.length) onChange(values.slice(0, -1));
  };
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input id={id} className="input" value={text} placeholder={placeholder} onChange={(e) => setText(e.target.value)} onKeyDown={onKey} onBlur={commit} aria-describedby={hint ? `${id}-h` : undefined} />
      {hint && <p className="hint" id={`${id}-h`}>{hint}</p>}
      {values.length > 0 && (
        <ul className="chips" aria-label={label}>
          {values.map((v) => (
            <li className="chip" key={v}>{v}<button type="button" aria-label={`Remove ${v}`} onClick={() => onChange(values.filter((x) => x !== v))}><Icon name="x" size={14} /></button></li>
          ))}
        </ul>
      )}
    </div>
  );
}

const LAB_SUGGESTIONS = ["potassium", "creatinine", "inr", "alt", "ast", "bilirubin", "sodium", "hemoglobin", "platelets", "wbc"];

export function PatientForm({ value, onChange }: { value: PatientDraft; onChange: (v: PatientDraft) => void }) {
  const set = <K extends keyof PatientDraft>(k: K, v: PatientDraft[K]) => onChange({ ...value, [k]: v });
  const uid = useId();
  const dl = `${uid}-labs`;
  return (
    <div className="stack">
      <div className="form-grid">
        <div className="field"><label htmlFor={`${uid}-age`}>Age (years)</label>
          <input id={`${uid}-age`} className="input" type="number" inputMode="numeric" min={0} max={120} value={value.age} onChange={(e) => set("age", e.target.value)} /></div>
        <div className="field"><label htmlFor={`${uid}-sex`}>Sex</label>
          <select id={`${uid}-sex`} className="select" value={value.sex} onChange={(e) => set("sex", e.target.value as PatientDraft["sex"])}>
            <option value="">Not specified</option><option value="female">Female</option><option value="male">Male</option><option value="other">Other</option>
          </select></div>
        <div className="field"><label htmlFor={`${uid}-wt`}>Weight (kg)</label>
          <input id={`${uid}-wt`} className="input" type="number" inputMode="decimal" min={0} max={500} step="0.1" value={value.weight} onChange={(e) => set("weight", e.target.value)} /></div>
        <div className="field"><label htmlFor={`${uid}-egfr`}>eGFR (mL/min/1.73 m²)</label>
          <input id={`${uid}-egfr`} className="input" type="number" inputMode="decimal" min={0} max={200} value={value.egfr} onChange={(e) => set("egfr", e.target.value)} /></div>
        <div className="field span-2"><label htmlFor={`${uid}-hep`}>Hepatic impairment</label>
          <select id={`${uid}-hep`} className="select" value={value.hepatic} onChange={(e) => set("hepatic", e.target.value as PatientDraft["hepatic"])}>
            <option value="">Not specified</option><option value="none">None</option><option value="mild">Mild</option><option value="moderate">Moderate</option><option value="severe">Severe</option>
          </select></div>
        <div className="field span-2"><span className="label">Pregnancy</span>
          <label className="check"><input type="checkbox" checked={value.pregnant} onChange={(e) => set("pregnant", e.target.checked)} />Patient is pregnant</label></div>
        <div className="span-2"><TagInput label="Diagnoses" values={value.diagnoses} onChange={(v) => set("diagnoses", v)} placeholder="e.g. chronic kidney disease, then Enter" hint="Matched to drug–disease rules by keyword." /></div>
        <div className="span-2"><TagInput label="Allergies" values={value.allergies} onChange={(v) => set("allergies", v)} placeholder="e.g. penicillin, then Enter" /></div>
        <div className="span-4"><TagInput label="Other current medications (not being reviewed)" values={value.meds} onChange={(v) => set("meds", v)} placeholder="e.g. lisinopril, then Enter" hint="Counted toward polypharmacy only." /></div>
      </div>
      <div className="field">
        <span className="label">Lab values</span>
        <datalist id={dl}>{LAB_SUGGESTIONS.map((l) => <option key={l} value={l} />)}</datalist>
        <div className="pts">
          {value.labs.map((l, i) => (
            <div className="pt-row" key={i}>
              <div className="field"><label className="sr-only" htmlFor={`${uid}-ln${i}`}>Lab name</label>
                <input id={`${uid}-ln${i}`} className="input" list={dl} placeholder="Lab name (e.g. potassium)" value={l.name} onChange={(e) => set("labs", value.labs.map((x, j) => (j === i ? { ...x, name: e.target.value } : x)))} /></div>
              <div className="field"><label className="sr-only" htmlFor={`${uid}-lv${i}`}>Lab value</label>
                <input id={`${uid}-lv${i}`} className="input" type="number" inputMode="decimal" step="any" placeholder="Value" value={l.value} onChange={(e) => set("labs", value.labs.map((x, j) => (j === i ? { ...x, value: e.target.value } : x)))} /></div>
              <button type="button" className="icon-btn" aria-label={`Remove lab value ${i + 1}`} onClick={() => set("labs", value.labs.filter((_, j) => j !== i))}><Icon name="trash" size={18} /></button>
            </div>
          ))}
        </div>
        <div><button type="button" className="btn btn-sm" onClick={() => set("labs", [...value.labs, { name: "", value: "" }])}><Icon name="plus" size={16} />Add lab value</button></div>
      </div>
    </div>
  );
}
