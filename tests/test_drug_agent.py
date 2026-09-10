"""Tests for the Drug Safety Agent."""

import pytest

from agent.drug_agent import DrugSafetyAgent
from agent.tools import RiskLevel
from data.drug_database import LocalDrugDatabase
from utils.formatters import DrugSafetyFormatter


class TestDrugLookup:
    """Test drug database lookups."""

    def setup_method(self):
        self.db = LocalDrugDatabase()

    def test_vancomycin_lookup(self):
        drug = self.db.search("vancomycin")
        assert drug is not None
        assert drug.name == "Vancomycin"
        assert drug.drug_class == "Glycopeptide Antibiotic"

    def test_amphotericin_b_lookup(self):
        drug = self.db.search("amphotericin b")
        assert drug is not None
        assert drug.name == "Amphotericin B"
        assert drug.drug_class == "Polyene Antifungal"

    def test_methotrexate_lookup(self):
        drug = self.db.search("methotrexate")
        assert drug is not None
        assert drug.name == "Methotrexate"

    def test_amiodarone_lookup(self):
        drug = self.db.search("amiodarone")
        assert drug is not None
        assert drug.name == "Amiodarone"

    def test_unknown_drug_lookup(self):
        drug = self.db.search("unknown-drug-123")
        assert drug is None

    def test_case_insensitive_lookup(self):
        drug1 = self.db.search("VANCOMYCIN")
        drug2 = self.db.search("vancomycin")
        drug3 = self.db.search("VaNcOmYcIn")
        assert drug1 is not None
        assert drug1.name == drug2.name == drug3.name


class TestAdverseEffects:
    """Test adverse effects analysis."""

    def setup_method(self):
        self.db = LocalDrugDatabase()

    def test_vancomycin_adverse_effects(self):
        ae_list = self.db.get_adverse_effects("vancomycin")
        assert len(ae_list) > 0
        nephrotoxicity = [ae for ae in ae_list if "Nephrotoxicity" in ae.effect_name]
        assert len(nephrotoxicity) > 0
        assert nephrotoxicity[0].risk_level == RiskLevel.HIGH

    def test_adverse_effects_have_organ_system(self):
        ae_list = self.db.get_adverse_effects("amphotericin b")
        for ae in ae_list:
            assert ae.organ_system is not None
            assert len(ae.organ_system) > 0

    def test_adverse_effects_have_risk_level(self):
        ae_list = self.db.get_adverse_effects("methotrexate")
        for ae in ae_list:
            assert ae.risk_level in [RiskLevel.HIGH, RiskLevel.MODERATE, RiskLevel.LOW]


class TestDrugSafetyAgent:
    """Test the main drug safety agent."""

    def setup_method(self):
        self.agent = DrugSafetyAgent()

    def test_analyze_vancomycin(self):
        profile = self.agent.analyze_drug("vancomycin")
        assert profile is not None
        assert profile.drug.name == "Vancomycin"
        assert len(profile.adverse_effects) > 0
        assert len(profile.monitoring_parameters) > 0
        assert len(profile.references) > 0

    def test_analyze_amphotericin_b(self):
        profile = self.agent.analyze_drug("amphotericin b")
        assert profile is not None
        assert profile.drug.name == "Amphotericin B"
        assert len(profile.adverse_effects) > 0

    def test_analyze_methotrexate(self):
        profile = self.agent.analyze_drug("methotrexate")
        assert profile is not None
        assert profile.drug.name == "Methotrexate"
        assert len(profile.adverse_effects) > 0

    def test_analyze_amiodarone(self):
        profile = self.agent.analyze_drug("amiodarone")
        assert profile is not None
        assert profile.drug.name == "Amiodarone"
        assert len(profile.adverse_effects) > 0

    def test_analyze_unknown_drug(self):
        profile = self.agent.analyze_drug("nonexistentdrugname123")
        assert profile is None

    def test_empty_input_returns_none(self):
        assert self.agent.analyze_drug("") is None
        assert self.agent.analyze_drug("   ") is None

    def test_required_output_fields(self):
        profile = self.agent.analyze_drug("vancomycin")
        assert profile is not None
        assert hasattr(profile, "drug")
        assert hasattr(profile, "adverse_effects")
        assert hasattr(profile, "monitoring_parameters")
        assert hasattr(profile, "warning_signs")
        assert hasattr(profile, "key_considerations")
        assert hasattr(profile, "references")
        assert hasattr(profile, "analysis_timestamp")

    def test_adverse_effect_structure(self):
        profile = self.agent.analyze_drug("vancomycin")
        assert profile is not None
        for ae in profile.adverse_effects:
            assert ae.effect_name
            assert ae.organ_system
            assert ae.risk_level in {RiskLevel.HIGH, RiskLevel.MODERATE, RiskLevel.LOW}

    def test_monitoring_structure(self):
        profile = self.agent.analyze_drug("amphotericin b")
        assert profile is not None
        for mp in profile.monitoring_parameters:
            assert mp.parameter_name
            assert mp.frequency
            assert mp.rationale
            assert mp.monitoring_type in {"baseline", "ongoing", "periodic"} or hasattr(mp.monitoring_type, "value")

    def test_reference_structure(self):
        profile = self.agent.analyze_drug("amiodarone")
        assert profile is not None
        assert len(profile.references) > 0
        for ref in profile.references:
            assert ref.title
            assert ref.source
            assert ref.evidence_type in {"DEMONSTRATION", "AUTHORITATIVE"}

    def test_adverse_effects_sorted_by_risk(self):
        profile = self.agent.analyze_drug("vancomycin")
        assert profile is not None
        risk_levels = [ae.risk_level for ae in profile.adverse_effects]
        for i in range(len(risk_levels) - 1):
            assert risk_levels[i] <= risk_levels[i + 1]

    def test_warning_signs_present(self):
        profile = self.agent.analyze_drug("vancomycin")
        assert profile is not None
        assert len(profile.warning_signs) > 0
        for ws in profile.warning_signs:
            assert ws.sign_description is not None
            assert ws.action_required is not None

    def test_summary_links_detailed_effects_to_monitoring_and_warnings(self):
        profile = self.agent.analyze_drug("vancomycin")
        assert profile is not None

        summary = DrugSafetyFormatter.format_summary_table(profile)
        nephrotoxicity = summary[
            summary["Adverse Effect"].str.startswith("Nephrotoxicity")
        ].iloc[0]

        assert nephrotoxicity["Monitoring Parameter"] != "Not specified"
        assert nephrotoxicity["Warning Signs"] != "—"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
