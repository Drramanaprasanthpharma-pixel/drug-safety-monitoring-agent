"""
Drug Safety Agent - orchestrates tool calls to analyze drug safety profiles.
"""

from typing import Optional, List
from datetime import datetime
from agent.tools import Drug, DrugSafetyProfile, AdverseEffect
from data.drug_database import LocalDrugDatabase
from data.monitoring_guidelines import MonitoringGuidelines
from utils.reference_manager import ReferenceManager


class DrugSafetyAgent:
    """
    Main agent that orchestrates drug safety analysis.
    Calls appropriate tools in sequence to build a complete safety profile.
    """

    def __init__(self):
        """Initialize the drug safety agent with tool instances."""
        self.drug_database = LocalDrugDatabase()
        self.monitoring_guidelines = MonitoringGuidelines()
        self.reference_manager = ReferenceManager()

    def analyze_drug(self, drug_name: str) -> Optional[DrugSafetyProfile]:
        """
        Analyze a drug and generate a complete safety profile.

        Args:
            drug_name: The name of the drug to analyze.

        Returns:
            DrugSafetyProfile object if successful, None if drug not found.
        """
        if drug_name is None or not str(drug_name).strip():
            return None

        # Step 1: Search for drug information
        drug = self._search_drug(drug_name)
        if drug is None:
            return None

        # Step 2: Analyze adverse effects
        adverse_effects = self._analyze_adverse_effects(drug)

        # Step 3: Get monitoring recommendations
        monitoring_params = self._get_monitoring_recommendations(drug, adverse_effects)

        # Step 4: Identify warning signs
        warning_signs = self._identify_warning_signs(drug, adverse_effects)

        # Step 5: Get key considerations
        key_considerations = self._get_key_considerations(drug)

        # Step 6: Retrieve references
        references = self._retrieve_references(drug_name)

        # Step 7: Compile complete profile
        profile = DrugSafetyProfile(
            drug=drug,
            adverse_effects=adverse_effects,
            monitoring_parameters=monitoring_params,
            warning_signs=warning_signs,
            key_considerations=key_considerations,
            references=references,
            analysis_timestamp=datetime.now().isoformat(),
            uncertainty_notes=self._generate_uncertainty_notes(drug_name),
        )

        return profile

    def _search_drug(self, drug_name: str) -> Optional[Drug]:
        """Tool Call 1: Search for drug information."""
        return self.drug_database.search(drug_name)

    def _analyze_adverse_effects(self, drug: Drug) -> List[AdverseEffect]:
        """Tool Call 2: Analyze adverse effects."""
        adverse_effects = self.drug_database.get_adverse_effects(drug.name)
        return sorted(adverse_effects, key=lambda x: x.risk_level.sort_order)

    def _get_monitoring_recommendations(self, drug: Drug, adverse_effects: List[AdverseEffect]) -> List:
        """Tool Call 3: Get monitoring recommendations."""
        return self.monitoring_guidelines.get_recommendations(
            drug.name, drug.drug_class, adverse_effects
        )

    def _identify_warning_signs(self, drug: Drug, adverse_effects: List[AdverseEffect]) -> List:
        """Identify clinical warning signs based on adverse effects."""
        return self.drug_database.get_warning_signs(drug.name, adverse_effects)

    def _get_key_considerations(self, drug: Drug) -> List[str]:
        """Get drug-specific key considerations."""
        return self.drug_database.get_key_considerations(drug.name)

    def _retrieve_references(self, drug_name: str) -> List:
        """Tool Call 4: Retrieve and validate references."""
        return self.reference_manager.get_references(drug_name)

    def _generate_uncertainty_notes(self, drug_name: str) -> Optional[str]:
        """Generate notes about any uncertainty in the analysis."""
        if not self.drug_database.is_complete(drug_name):
            return "Information for this drug may be incomplete. Please verify against current authoritative sources."
        return None
