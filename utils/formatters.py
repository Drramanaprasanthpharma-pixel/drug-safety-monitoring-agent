"""
Formatting utilities for displaying drug safety information.
"""

import pandas as pd
from typing import List, Optional
from agent.tools import DrugSafetyProfile, AdverseEffect, MonitoringParameter, WarningSign, Reference


class DrugSafetyFormatter:
    """
    Formats drug safety profiles for display in Streamlit.
    """

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
            if ref.url:
                md_text += f"   - URL: {ref.url}\n"
            if ref.reliability_score:
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
