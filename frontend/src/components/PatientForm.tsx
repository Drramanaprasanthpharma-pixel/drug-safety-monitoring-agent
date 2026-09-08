import { useState } from 'react'
import type { PatientInfo } from '../types'

const EMPTY: PatientInfo = {
  diagnoses: [],
  allergies: [],
  current_medications: [],
  lab_values: {},
}

function listField(value: string): string[] {
  return value
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

export function PatientForm({
  patient,
  onChange,
  enabled,
  onToggle,
}: {
  patient: PatientInfo
  onChange: (p: PatientInfo) => void
  enabled: boolean
  onToggle: (enabled: boolean) => void
}) {
  const [labKey, setLabKey] = useState('')
  const [labValue, setLabValue] = useState('')

  function addLab() {
    if (!labKey.trim() || !labValue.trim()) return
    onChange({ ...patient, lab_values: { ...patient.lab_values, [labKey.trim().toLowerCase()]: parseFloat(labValue) } })
    setLabKey('')
    setLabValue('')
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-ink-700">Patient information (optional)</p>
        <button
          type="button"
          onClick={() => onToggle(!enabled)}
          className="text-sm text-teal-600 hover:text-teal-700 font-medium"
        >
          {enabled ? 'Remove patient context' : 'Add patient context'}
        </button>
      </div>

      {!enabled && (
        <p className="text-sm text-ink-500">
          A drug-only analysis works without this. Add patient details to refine organ priority, red flags, and
          risk scoring.
        </p>
      )}

      {enabled && (
        <div className="grid grid-cols-2 gap-3 border border-ink-100 rounded-sm p-4 bg-white">
          <Field label="Age">
            <input
              type="number"
              min={0}
              max={120}
              value={patient.age ?? ''}
              onChange={(e) => onChange({ ...patient, age: e.target.value ? Number(e.target.value) : undefined })}
              className="input"
            />
          </Field>
          <Field label="Sex">
            <select
              value={patient.sex ?? ''}
              onChange={(e) => onChange({ ...patient, sex: (e.target.value || undefined) as PatientInfo['sex'] })}
              className="input"
            >
              <option value="">Not specified</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
            </select>
          </Field>
          <Field label="Weight (kg)">
            <input
              type="number"
              value={patient.weight_kg ?? ''}
              onChange={(e) => onChange({ ...patient, weight_kg: e.target.value ? Number(e.target.value) : undefined })}
              className="input"
            />
          </Field>
          <Field label="Pregnant">
            <select
              value={patient.pregnant === undefined ? '' : String(patient.pregnant)}
              onChange={(e) => onChange({ ...patient, pregnant: e.target.value === '' ? undefined : e.target.value === 'true' })}
              className="input"
            >
              <option value="">Not specified</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </Field>
          <Field label="eGFR (mL/min/1.73m²)">
            <input
              type="number"
              value={patient.egfr ?? ''}
              onChange={(e) => onChange({ ...patient, egfr: e.target.value ? Number(e.target.value) : undefined })}
              className="input"
            />
          </Field>
          <Field label="Hepatic function">
            <select
              value={patient.hepatic_impairment ?? ''}
              onChange={(e) =>
                onChange({ ...patient, hepatic_impairment: (e.target.value || undefined) as PatientInfo['hepatic_impairment'] })
              }
              className="input"
            >
              <option value="">Not specified</option>
              <option value="none">Normal</option>
              <option value="mild">Mild impairment</option>
              <option value="moderate">Moderate impairment</option>
              <option value="severe">Severe impairment</option>
            </select>
          </Field>
          <Field label="Diagnoses (comma-separated)" full>
            <input
              type="text"
              placeholder="e.g. atrial fibrillation, chronic kidney disease"
              value={patient.diagnoses.join(', ')}
              onChange={(e) => onChange({ ...patient, diagnoses: listField(e.target.value) })}
              className="input"
            />
          </Field>
          <Field label="Allergies (comma-separated)" full>
            <input
              type="text"
              value={patient.allergies.join(', ')}
              onChange={(e) => onChange({ ...patient, allergies: listField(e.target.value) })}
              className="input"
            />
          </Field>
          <Field label="Current medications (comma-separated)" full>
            <input
              type="text"
              value={patient.current_medications.join(', ')}
              onChange={(e) => onChange({ ...patient, current_medications: listField(e.target.value) })}
              className="input"
            />
          </Field>
          <Field label="Relevant lab values" full>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                placeholder="parameter (e.g. potassium)"
                value={labKey}
                onChange={(e) => setLabKey(e.target.value)}
                className="input flex-1"
              />
              <input
                type="number"
                placeholder="value"
                value={labValue}
                onChange={(e) => setLabValue(e.target.value)}
                className="input w-28"
              />
              <button type="button" onClick={addLab} className="px-3 py-2 text-sm font-medium text-teal-700 border border-teal-600 rounded-sm hover:bg-teal-100">
                Add
              </button>
            </div>
            {Object.keys(patient.lab_values).length > 0 && (
              <ul className="flex flex-wrap gap-2">
                {Object.entries(patient.lab_values).map(([k, v]) => (
                  <li key={k} className="font-data text-xs bg-ink-100 rounded-sm px-2 py-1">
                    {k}: {v}
                    <button
                      type="button"
                      className="ml-1.5 text-ink-500 hover:text-signal-high"
                      onClick={() => {
                        const rest = { ...patient.lab_values }
                        delete rest[k]
                        onChange({ ...patient, lab_values: rest })
                      }}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Field>
        </div>
      )}
    </div>
  )
}

function Field({ label, children, full }: { label: string; children: React.ReactNode; full?: boolean }) {
  return (
    <label className={`block text-sm ${full ? 'col-span-2' : ''}`}>
      <span className="block text-ink-500 mb-1">{label}</span>
      {children}
    </label>
  )
}

export { EMPTY as emptyPatient }
