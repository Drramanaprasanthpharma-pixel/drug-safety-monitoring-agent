"""
Tool interfaces for the Drug Safety Agent.
Defines the contract for various drug information retrieval and analysis tools.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk severity classification."""
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"

    def __lt__(self, other):
        """Allow sorting by risk level."""
        order = {"HIGH": 0, "MODERATE": 1, "LOW": 2}
        return order[self.value] < order[other.value]


class MonitoringType(Enum):
    """Type of monitoring recommendation."""
    BASELINE = "baseline"
    ONGOING = "ongoing"
    PERIODIC = "periodic"


@dataclass
class Drug:
    """Represents a drug entity."""
    name: str
    brand_names: List[str] = field(default_factory=list)
    drug_class: str = ""
    generic_name: str = ""


@dataclass
class AdverseEffect:
    """Represents a single adverse effect."""
    effect_name: str
    organ_system: str
    risk_level: RiskLevel
    incidence: Optional[str] = None
    mechanism: Optional[str] = None
    clinical_importance: Optional[str] = None


@dataclass
class MonitoringParameter:
    """Represents a monitoring parameter."""
    parameter_name: str
    monitoring_type: MonitoringType
    frequency: str
    rationale: str
    related_adverse_effects: List[str] = field(default_factory=list)


@dataclass
class WarningSign:
    """Represents a clinical warning sign."""
    sign_description: str
    adverse_effect: str
    action_required: str
    severity: RiskLevel


@dataclass
class Reference:
    """Represents a reference source."""
    title: str
    source: str
    url: Optional[str] = None
    date_accessed: Optional[str] = None
    reliability_score: Optional[float] = None


@dataclass
class DrugSafetyProfile:
    """Complete drug safety profile combining all analyses."""
    drug: Drug
    adverse_effects: List[AdverseEffect]
    monitoring_parameters: List[MonitoringParameter]
    warning_signs: List[WarningSign]
    key_considerations: List[str]
    references: List[Reference]
    analysis_timestamp: Optional[str] = None
    uncertainty_notes: Optional[str] = None
