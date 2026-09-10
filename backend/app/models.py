"""
Pydantic schemas for the Drug Safety Monitoring API.

These define the structured JSON contract described in the product spec
(section 21). Every field that carries a clinical judgement also carries
an `is_ai_generated` / `evidence` companion so the frontend can render
the "established fact vs. AI-assisted interpretation" distinction.
"""
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class PatientInfo(BaseModel):
    """All fields optional — a drug-only analysis must work with none of these."""
    age: Optional[int] = Field(None, ge=0, le=120)
    sex: Optional[Literal["male", "female", "other", "unspecified"]] = None
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    pregnant: Optional[bool] = None
    egfr: Optional[float] = Field(None, ge=0, le=200, description="mL/min/1.73m^2")
    hepatic_impairment: Optional[Literal["none", "mild", "moderate", "severe"]] = None
    diagnoses: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    lab_values: dict[str, float] = Field(default_factory=dict, description="e.g. {'potassium': 3.1}")


class AnalysisRequest(BaseModel):
    drugs: List[str] = Field(..., min_length=1, description="Drug IDs or names to analyze")
    patient: Optional[PatientInfo] = None
    demo_mode: bool = False


class LabTrendPoint(BaseModel):
    day: int
    value: float


class LabTrendRequest(BaseModel):
    parameter: str
    unit: Optional[str] = None
    points: List[LabTrendPoint]


# ---------------------------------------------------------------------------
# Response building blocks
# ---------------------------------------------------------------------------

class Evidence(BaseModel):
    source: str
    reference: Optional[str] = None
    date: Optional[str] = None
    confidence: Literal["High", "Moderate", "Limited", "Unknown"] = "Unknown"


class OverallRisk(BaseModel):
    category: Literal["Low", "Moderate", "High", "Critical"]
    priority_score: int = Field(..., ge=0, le=100)
    is_validated_score: bool = False
    score_label: str = "AI-assisted risk prioritization — not a validated clinical score"
    explanation: str


class PriorityOrgan(BaseModel):
    organ: str
    priority: Literal["Low", "Moderate", "High", "Critical"]
    relative_priority_percent: int = Field(..., ge=0, le=100)
    percent_label: str = "Relative monitoring priority generated from identified safety factors — not an incidence rate"
    reason: str
    toxicity: Optional[str] = None
    monitoring_parameters: List[str] = Field(default_factory=list)
    monitoring_frequency: str
    intervention_threshold: Optional[str] = None
    evidence: Optional[Evidence] = None


class InteractionResult(BaseModel):
    drug_a: str
    drug_b: str
    severity: Literal["Contraindicated", "Major", "Moderate", "Minor", "Unknown"]
    mechanism: List[str]
    mechanism_detail: str
    clinical_consequence: str
    recommended_action: Literal[
        "Avoid combination", "Dose adjustment", "Monitor",
        "Separate administration", "Continue with caution"
    ]
    action_detail: str
    evidence: Evidence


class DiseaseInteraction(BaseModel):
    condition: str
    drug: str
    risk: str
    recommendation: str
    evidence: Evidence


class MonitoringRow(BaseModel):
    parameter: str
    why: str
    baseline: str
    follow_up: str
    alert_threshold: str
    risk: Literal["Low", "Moderate", "High", "Critical"]
    triggered_by: List[str] = Field(default_factory=list, description="Which drug(s)/factors this row came from")


class VitalSignRow(BaseModel):
    parameter: str
    why: str
    triggered_by: List[str] = Field(default_factory=list)


class AdverseEffects(BaseModel):
    drug: str
    common: List[str]
    serious: List[str]
    life_threatening: List[str]
    boxed_warning: Optional[str] = None


class RedFlag(BaseModel):
    trigger: str
    consequence: str
    immediate_consideration: str
    escalation: str
    source_drug: Optional[str] = None


class PatientRiskFactor(BaseModel):
    factor: str
    detail: str
    affected_organ: Optional[str] = None


class PharmacistAction(BaseModel):
    action: str
    rationale: str
    evidence: Optional[Evidence] = None


class OrganToxicityDetail(BaseModel):
    drug: str
    organ: str
    risk_level: Literal["Low", "Moderate", "High", "Critical"]
    reason: str
    toxicity: str
    monitoring_parameters: List[str]
    frequency: str
    thresholds: str
    evidence: Evidence


class LabTrendAssessment(BaseModel):
    parameter: str
    trend: Literal["Increasing", "Decreasing", "Stable", "Insufficient data"]
    clinically_significant_change: bool
    note: str = "Potential concern detected — clinical correlation required."


# ---------------------------------------------------------------------------
# Dashboard summary + full response
# ---------------------------------------------------------------------------

class DashboardCards(BaseModel):
    overall_safety: str
    overall_risk_category: Literal["Low", "Moderate", "High", "Critical"]
    priority_organ: str
    priority_organ_level: str
    interaction_count: int
    monitoring_param_count: int
    red_flag_count: int
    patient_risk_factor_count: int


class AnalysisResponse(BaseModel):
    drugs_analyzed: List[str]
    demo_mode: bool = False
    disclaimer: str = (
        "This is a clinical decision-support tool intended to assist, not replace, "
        "clinical pharmacist and physician judgement. It is not a substitute for "
        "official prescribing information. Verify all recommendations against current "
        "labeling, institutional protocols, and clinical guidelines before acting."
    )
    overall_risk: OverallRisk
    dashboard: DashboardCards
    priority_organs: List[PriorityOrgan]
    organ_toxicity_detail: List[OrganToxicityDetail]
    interactions: List[InteractionResult]
    disease_interactions: List[DiseaseInteraction]
    monitoring: List[MonitoringRow]
    vital_signs: List[VitalSignRow]
    adverse_effects: List[AdverseEffects]
    red_flags: List[RedFlag]
    patient_risk_factors: List[PatientRiskFactor]
    pharmacist_actions: List[PharmacistAction]
    monitoring_schedule: dict[str, List[str]]
    evidence: List[Evidence]
    audit_id: str


class DrugSummary(BaseModel):
    id: str
    generic_name: str
    brand_names: List[str]
    drug_class: str
