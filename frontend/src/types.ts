export type SeverityLevel = 'Low' | 'Moderate' | 'High' | 'Critical'
export type InteractionSeverity = 'Contraindicated' | 'Major' | 'Moderate' | 'Minor' | 'Unknown'
export type EvidenceConfidence = 'High' | 'Moderate' | 'Limited' | 'Unknown'

export interface Evidence {
  source: string
  reference?: string | null
  date?: string | null
  confidence: EvidenceConfidence
}

export interface PatientInfo {
  // Optional fields accept null because the backend models them as Optional[...] = None.
  age?: number | null
  sex?: 'male' | 'female' | 'other' | 'unspecified' | null
  weight_kg?: number | null
  pregnant?: boolean | null
  egfr?: number | null
  hepatic_impairment?: 'none' | 'mild' | 'moderate' | 'severe' | null
  diagnoses: string[]
  allergies: string[]
  current_medications: string[]
  lab_values: Record<string, number>
}

export interface OverallRisk {
  category: SeverityLevel
  priority_score: number
  is_validated_score: boolean
  score_label: string
  explanation: string
}

export interface DashboardCards {
  overall_safety: string
  overall_risk_category: SeverityLevel
  priority_organ: string
  priority_organ_level: string
  interaction_count: number
  monitoring_param_count: number
  red_flag_count: number
  patient_risk_factor_count: number
}

export interface PriorityOrgan {
  organ: string
  priority: SeverityLevel
  relative_priority_percent: number
  percent_label: string
  reason: string
  toxicity?: string
  monitoring_parameters: string[]
  monitoring_frequency: string
  intervention_threshold?: string
  evidence?: Evidence
}

export interface OrganToxicityDetail {
  drug: string
  organ: string
  risk_level: SeverityLevel
  reason: string
  toxicity: string
  monitoring_parameters: string[]
  frequency: string
  thresholds: string
  evidence: Evidence
}

export interface InteractionResult {
  drug_a: string
  drug_b: string
  severity: InteractionSeverity
  mechanism: string[]
  mechanism_detail: string
  clinical_consequence: string
  recommended_action: string
  action_detail: string
  evidence: Evidence
}

export interface DiseaseInteraction {
  condition: string
  drug: string
  risk: string
  recommendation: string
  evidence: Evidence
}

export interface MonitoringRow {
  parameter: string
  why: string
  baseline: string
  follow_up: string
  alert_threshold: string
  risk: SeverityLevel
  triggered_by: string[]
}

export interface VitalSignRow {
  parameter: string
  why: string
  triggered_by: string[]
}

export interface AdverseEffects {
  drug: string
  common: string[]
  serious: string[]
  life_threatening: string[]
  boxed_warning?: string | null
}

export interface RedFlag {
  trigger: string
  consequence: string
  immediate_consideration: string
  escalation: string
  source_drug?: string | null
}

export interface PatientRiskFactor {
  factor: string
  detail: string
  affected_organ?: string | null
}

export interface PharmacistAction {
  action: string
  rationale: string
  evidence?: Evidence | null
}

export interface AnalysisResponse {
  drugs_analyzed: string[]
  demo_mode: boolean
  disclaimer: string
  overall_risk: OverallRisk
  dashboard: DashboardCards
  priority_organs: PriorityOrgan[]
  organ_toxicity_detail: OrganToxicityDetail[]
  interactions: InteractionResult[]
  disease_interactions: DiseaseInteraction[]
  monitoring: MonitoringRow[]
  vital_signs: VitalSignRow[]
  adverse_effects: AdverseEffects[]
  red_flags: RedFlag[]
  patient_risk_factors: PatientRiskFactor[]
  pharmacist_actions: PharmacistAction[]
  monitoring_schedule: Record<string, string[]>
  evidence: Evidence[]
  audit_id: string
}

export interface DrugSummary {
  id: string
  generic_name: string
  brand_names: string[]
  drug_class: string
}

export interface LabTrendPoint {
  day: number
  value: number
}

export interface LabTrendAssessment {
  parameter: string
  trend: 'Increasing' | 'Decreasing' | 'Stable' | 'Insufficient data'
  clinically_significant_change: boolean
  note: string
}

/* ------------------------------------------------------------------------
 * Additions used by the PharmaSafe AI interface. Everything above mirrors
 * backend/app/models.py and is unchanged.
 * --------------------------------------------------------------------- */

/** Short aliases used throughout the UI components. */
export type Level = SeverityLevel
export type Confidence = EvidenceConfidence

export interface AnalysisRequest {
  drugs: string[]
  patient?: PatientInfo | null
  demo_mode?: boolean
}

export interface LabTrendRequest {
  parameter: string
  unit?: string | null
  points: LabTrendPoint[]
}

export interface DemoConfig {
  demo_drugs: Array<{ id: string; generic_name: string }>
  demo_patient: PatientInfo
  label: string
}

/** GET /api/drugs/{id}: the full curated record. Known fields are typed; the rest is rendered generically. */
export interface DrugDetail {
  id: string
  generic_name: string
  brand_names?: string[]
  drug_class?: string
  boxed_warning?: string | null
  contraindications?: string[]
  renal_dosing?: string | null
  adverse_effects?: { common: string[]; serious: string[]; life_threatening: string[] }
  organ_toxicity?: Array<{
    organ: string
    risk_level: SeverityLevel
    reason: string
    toxicity: string
    monitoring_parameters: string[]
    frequency: string
    thresholds: string
    source: string
  }>
  monitoring_parameters?: Array<{
    parameter: string
    why: string
    baseline: string
    follow_up: string
    alert_threshold: string
    risk: SeverityLevel
  }>
  vital_signs?: Array<{ parameter: string; why: string }>
  evidence?: Evidence[]
  [key: string]: unknown
}

/** One row of GET /api/audit, normalised by api.ts from the raw JSONL record. */
export interface AuditEntry {
  id: string
  timestamp: string
  drugs: string[]
  /** null when the raw record does not say. */
  patientProvided: boolean | null
  demo: boolean
}
