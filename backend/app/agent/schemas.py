"""
Pydantic schemas for AI-assisted drug normalization and retrieval
(spec sections 5, 6, 7). These validate every response coming back from an
AI provider before it is allowed anywhere near the deterministic safety
engines. If a response does not validate, it is rejected outright (see
drug_agent.py) — malformed AI output never reaches the engines (section 7).

`AIDrugRecord` intentionally mirrors the shape of the curated entries in
data/drugs.json field-for-field, so a validated instance can be converted
straight into the same internal dict shape the engines already read, with
no changes to engine code (spec section 2, 6).
"""
from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

RiskLevel = Literal["Low", "Moderate", "High", "Critical"]
Confidence = Literal["High", "Moderate", "Limited", "Unknown"]


class AIEvidence(BaseModel):
    source: str
    reference: Optional[str] = None
    date: Optional[str] = None
    confidence: Confidence = "Unknown"


class AIAdverseEffects(BaseModel):
    common: List[str] = Field(default_factory=list)
    serious: List[str] = Field(default_factory=list)
    life_threatening: List[str] = Field(default_factory=list)


class AIOrganToxicity(BaseModel):
    organ: str
    risk_level: RiskLevel
    reason: str
    toxicity: str
    monitoring_parameters: List[str] = Field(default_factory=list)
    frequency: str
    thresholds: str
    source: str


class AIMonitoringParameter(BaseModel):
    parameter: str
    why: str
    baseline: str
    follow_up: str
    alert_threshold: str
    risk: RiskLevel


class AIVitalSign(BaseModel):
    parameter: str
    why: str


class AITherapeuticDrugMonitoring(BaseModel):
    applicable: bool = False
    target_range: Optional[str] = None
    notes: Optional[str] = None


class AIDrugRecord(BaseModel):
    """Mirrors the internal drug-record shape used throughout
    backend/app/data/drugs.json and read by every engine module."""
    generic_name: str
    brand_names: List[str] = Field(default_factory=list)
    drug_class: str
    pharmacology: Optional[str] = None
    boxed_warning: Optional[str] = None
    contraindications: List[str] = Field(default_factory=list)
    adverse_effects: AIAdverseEffects
    organ_toxicity: List[AIOrganToxicity] = Field(default_factory=list)
    monitoring_parameters: List[AIMonitoringParameter] = Field(default_factory=list)
    vital_signs: List[AIVitalSign] = Field(default_factory=list)
    renal_dosing: Optional[str] = None
    hepatic_dosing: Optional[str] = None
    high_risk_populations: List[str] = Field(default_factory=list)
    therapeutic_drug_monitoring: AITherapeuticDrugMonitoring = Field(
        default_factory=AITherapeuticDrugMonitoring
    )
    evidence: List[AIEvidence] = Field(default_factory=list)

    @field_validator("generic_name", "drug_class")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be blank")
        return v.strip()


class PossibleMatch(BaseModel):
    generic_name: str
    drug_class: Optional[str] = None
    reason: Optional[str] = None


class Normalization(BaseModel):
    """Mirrors spec section 5's example normalization output shape."""
    input_name: str
    normalized_name: Optional[str] = None
    generic_name: Optional[str] = None
    drug_class: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class AIEnvelope(BaseModel):
    """Top-level shape the AI provider must return in a single response.
    Combining normalization + retrieval into one call (rather than two
    separate round trips) keeps latency and cost down while still
    producing the distinct normalization object the spec describes."""
    status: Literal["found", "ambiguous_drug", "unknown_drug"]
    normalization: Normalization
    drug: Optional[AIDrugRecord] = None
    possible_matches: List[PossibleMatch] = Field(default_factory=list)

    @field_validator("drug")
    @classmethod
    def _drug_required_when_found(cls, v, info):
        if info.data.get("status") == "found" and v is None:
            raise ValueError("status 'found' requires a populated 'drug' record")
        return v
