import { useState } from 'react'
import type { AnalysisResponse, DrugSummary, PatientInfo } from './types'
import { analyze, getDemoConfig, ApiError } from './api'
import { DrugSearch } from './components/DrugSearch'
import { PatientForm, emptyPatient } from './components/PatientForm'
import { DashboardCards } from './components/DashboardCards'
import { OverallRiskPanel } from './components/OverallRiskPanel'
import { OrganPriorityPanel } from './components/OrganPriorityPanel'
import { InteractionsPanel } from './components/InteractionsPanel'
import { MonitoringTable, VitalSignsPanel } from './components/MonitoringTable'
import { AdverseEffectsPanel } from './components/AdverseEffectsPanel'
import { RedFlagsPanel } from './components/RedFlagsPanel'
import { DiseaseInteractionsPanel, PatientRiskPanel } from './components/DiseaseInteractionsPanel'
import { PharmacistActionsPanel } from './components/PharmacistActionsPanel'
import { EvidencePanel, MonitoringSchedulePanel } from './components/EvidencePanel'
import { LabTrendPanel } from './components/LabTrendPanel'

export default function App() {
  const [selectedDrugs, setSelectedDrugs] = useState<DrugSummary[]>([])
  const [patientEnabled, setPatientEnabled] = useState(false)
  const [patient, setPatient] = useState<PatientInfo>(emptyPatient)
  const [demoMode, setDemoMode] = useState(false)
  const [result, setResult] = useState<AnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function loadDemo() {
    setError(null)
    try {
      const config = await getDemoConfig()
      setSelectedDrugs(
        config.demo_drugs.slice(0, 2).map((d) => ({ id: d.id, generic_name: d.generic_name, brand_names: [], drug_class: '' }))
      )
      setPatient(config.demo_patient)
      setPatientEnabled(true)
      setDemoMode(true)
      setResult(null)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong reaching the analysis service.')
    }
  }

  async function runAnalysis() {
    if (selectedDrugs.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const res = await analyze(
        selectedDrugs.map((d) => d.id),
        patientEnabled ? patient : null,
        demoMode
      )
      setResult(res)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong reaching the analysis service.')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-ink-100 bg-white">
        <div className="max-w-5xl mx-auto px-6 py-6 flex items-center justify-between">
          <div>
            <p className="text-sm text-teal-600 font-medium mb-1">Clinical decision support</p>
            <h1 className="font-display text-3xl text-ink-950">Drug Safety Monitor</h1>
          </div>
          <button
            type="button"
            onClick={loadDemo}
            className="text-sm font-medium border border-ink-300 px-3 py-2 hover:bg-ink-100"
          >
            Load demo patient
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {demoMode && (
          <div className="mb-6 border border-teal-600/40 bg-teal-100 text-teal-700 text-sm px-4 py-2">
            Illustrative / Demo Data — this is not a real patient. Values are for demonstration only.
          </div>
        )}

        <div className="bg-white border border-ink-100 p-6 mb-8">
          <div className="grid md:grid-cols-2 gap-8">
            <DrugSearch selected={selectedDrugs} onChange={setSelectedDrugs} />
            <PatientForm patient={patient} onChange={setPatient} enabled={patientEnabled} onToggle={setPatientEnabled} />
          </div>
          <div className="mt-6 flex items-center gap-3">
            <button
              type="button"
              onClick={runAnalysis}
              disabled={selectedDrugs.length === 0 || loading}
              className="px-5 py-2.5 bg-ink-950 text-white font-medium disabled:opacity-40"
            >
              {loading ? 'Analyzing…' : 'Analyze safety'}
            </button>
            {error && <p className="text-sm text-signal-high">{error}</p>}
          </div>
        </div>

        {result && (
          <>
            <p className="text-xs text-ink-500 border border-ink-100 bg-ink-100/40 p-3 mb-8">
              {result.disclaimer}
            </p>

            <DashboardCards data={result.dashboard} />

            <div className="mt-8 space-y-8">
              <OverallRiskPanel risk={result.overall_risk} />
              <OrganPriorityPanel organs={result.priority_organs} />
              <InteractionsPanel interactions={result.interactions} />
              <DiseaseInteractionsPanel items={result.disease_interactions} />
              <MonitoringTable rows={result.monitoring} />
              <VitalSignsPanel rows={result.vital_signs} />
              <MonitoringSchedulePanel schedule={result.monitoring_schedule} />
              <AdverseEffectsPanel effects={result.adverse_effects} />
              <RedFlagsPanel flags={result.red_flags} />
              <PatientRiskPanel factors={result.patient_risk_factors} />
              <PharmacistActionsPanel actions={result.pharmacist_actions} />
              <EvidencePanel evidence={result.evidence} />
              <LabTrendPanel />
            </div>

            <p className="text-xs text-ink-500 mt-10 pt-4 border-t rule">
              Audit ID: <span className="font-data">{result.audit_id}</span>
            </p>
          </>
        )}

        {!result && (
          <div className="border border-ink-100 bg-white p-6">
            <LabTrendPanel />
          </div>
        )}
      </main>

      <footer className="max-w-5xl mx-auto px-6 py-8 text-xs text-ink-500">
        This is a clinical decision-support prototype, not a replacement for a physician or pharmacist, and not a
        substitute for official prescribing information. It uses a curated demonstration dataset for a fixed set of
        medications and is not connected to a live regulatory or drug-database feed.
      </footer>
    </div>
  )
}
