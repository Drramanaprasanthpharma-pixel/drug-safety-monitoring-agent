"""
Formatting utilities for displaying drug safety information.
"""

import pandas as pd
import re
from typing import List, Optional
from agent.tools import DrugSafetyProfile, AdverseEffect, MonitoringParameter, WarningSign, Reference


class DrugSafetyFormatter:
    """
    Formats drug safety profiles for display in Streamlit.
    """

    @staticmethod
    def _effect_matches(effect_name: str, related_name: str) -> bool:
        """Match labels when one adds detail or differs only by pluralization."""
        effect = re.sub(r"\s*\([^)]*\)", "", effect_name).strip().casefold()
        related = re.sub(r"\s*\([^)]*\)", "", related_name).strip().casefold()
        return effect.startswith(related) or related.startswith(effect)

    @staticmethod
    def format_adverse_effects_table(adverse_effects: List[AdverseEffect]) -> pd.DataFrame:
        """
        Format adverse effects as a pandas DataFrame for table display.
        """
        data = []
        for ae in adverse_effects:
            data.append({
                "Priority": ae.risk_level.value,
                "Adverse Effect": ae.effect_name,
                "Organ/System": ae.organ_system,
                "Incidence": ae.incidence or "Not specified",
                "Clinical Importance": ae.clinical_importance or "—",
            })
        return pd.DataFrame(data)

    @staticmethod
    def format_monitoring_table(monitoring_params: List[MonitoringParameter]) -> pd.DataFrame:
        """
        Format monitoring parameters as a pandas DataFrame.
        """
        baseline = []
        ongoing = []

        for mp in monitoring_params:
            row = {
                "Parameter": mp.parameter_name,
                "Type": mp.monitoring_type.value.capitalize(),
                "Frequency": mp.frequency,
                "Rationale": mp.rationale,
            }
            if mp.monitoring_type.value == "baseline":
                baseline.append(row)
            else:
                ongoing.append(row)

        return pd.DataFrame(baseline), pd.DataFrame(ongoing)

    @staticmethod
    def format_warning_signs_table(warning_signs: List[WarningSign]) -> pd.DataFrame:
        """
        Format warning signs as a pandas DataFrame.
        """
        data = []
        for ws in warning_signs:
            data.append({
                "Severity": ws.severity.value,
                "Warning Sign": ws.sign_description,
                "Related Effect": ws.adverse_effect,
                "Action Required": ws.action_required,
            })
        return pd.DataFrame(data)

    @staticmethod
    def format_references_list(references: List[Reference]) -> str:
        """
        Format references as a markdown list.
        """
        if not references:
            return "No references available."

        md_text = ""
        for i, ref in enumerate(references, 1):
            md_text += f"\n{i}. **{ref.title}**\n"
            md_text += f"   - Source: {ref.source}\n"
            md_text += f"   - Evidence type: {ref.evidence_type}\n"
            if ref.url:
                md_text += f"   - URL: {ref.url}\n"
            if ref.reliability_score is not None:
                md_text += f"   - Reliability: {int(ref.reliability_score * 100)}%\n"
        return md_text

    @staticmethod
    def format_key_considerations(considerations: List[str]) -> str:
        """
        Format key considerations as markdown.
        """
        if not considerations:
            return "No key considerations."

        md_text = ""
        for consideration in considerations:
            md_text += f"- {consideration}\n"
        return md_text

    @staticmethod
    def format_summary_table(profile: DrugSafetyProfile) -> pd.DataFrame:
        """Create a summary table matching the required clinical output columns."""
        rows = []
        for ae in profile.adverse_effects:
            monitoring_param = "Not specified"
            baseline = "—"
            ongoing = "—"
            for mp in profile.monitoring_parameters:
                if any(
                    DrugSafetyFormatter._effect_matches(ae.effect_name, name)
                    for name in mp.related_adverse_effects
                ):
                    monitoring_param = mp.parameter_name
                    if mp.monitoring_type.value == "baseline":
                        baseline = mp.frequency
                    else:
                        ongoing = mp.frequency
            warning_signs = "; ".join(
                ws.sign_description for ws in profile.warning_signs
                if DrugSafetyFormatter._effect_matches(ae.effect_name, ws.adverse_effect)
            ) or "—"
            evidence_source = (
                profile.references[0].source if profile.references else "Demonstration reference set"
            )
            rows.append({
                "Priority": ae.risk_level.value,
                "Adverse Effect": ae.effect_name,
                "Organ/System": ae.organ_system,
                "Monitoring Parameter": monitoring_param,
                "Baseline": baseline,
                "Ongoing": ongoing,
                "Warning Signs": warning_signs,
                "Evidence Source": evidence_source,
            })
        return pd.DataFrame(rows)
