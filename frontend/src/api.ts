import type { AnalysisResponse, DrugSummary, LabTrendAssessment, LabTrendPoint, PatientInfo } from './types'

const BASE = '/api'

class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? detail
    } catch {
      /* ignore parse failure */
    }
    throw new ApiError(detail, res.status)
  }
  return res.json() as Promise<T>
}

export async function searchDrugs(query: string): Promise<DrugSummary[]> {
  const res = await fetch(`${BASE}/drugs?q=${encodeURIComponent(query)}`)
  return handle(res)
}

export async function getDemoConfig(): Promise<{ demo_drugs: { id: string; generic_name: string }[]; demo_patient: PatientInfo; label: string }> {
  const res = await fetch(`${BASE}/demo`)
  return handle(res)
}

export async function analyze(drugs: string[], patient: PatientInfo | null, demoMode: boolean): Promise<AnalysisResponse> {
  const res = await fetch(`${BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ drugs, patient, demo_mode: demoMode }),
  })
  return handle(res)
}

export async function analyzeLabTrend(parameter: string, points: LabTrendPoint[]): Promise<LabTrendAssessment> {
  const res = await fetch(`${BASE}/lab-trend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ parameter, points }),
  })
  return handle(res)
}

export { ApiError }
