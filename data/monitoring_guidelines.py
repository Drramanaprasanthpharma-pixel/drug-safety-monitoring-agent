"""
Monitoring guidelines for drugs.
Provides standard monitoring parameters for different drugs and drug classes.
"""

from typing import List, Optional
from agent.tools import AdverseEffect, MonitoringParameter, MonitoringType


class MonitoringGuidelines:
    """
    Provides monitoring recommendations based on drug and adverse effects.
    """

    def __init__(self):
        """Initialize monitoring guidelines."""
        self.guidelines = self._initialize_guidelines()

    def _initialize_guidelines(self) -> dict:
        """Initialize monitoring guidelines for demonstration drugs."""
        return {
            "vancomycin": {
                "baseline": [
                    MonitoringParameter(
                        parameter_name="Serum Creatinine & Creatinine Clearance",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline renal function to monitor for nephrotoxicity",
                        related_adverse_effects=["Nephrotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Baseline Audiometry (if high-dose or risk factors)",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts (if ototoxicity risk)",
                        rationale="Establish baseline hearing to detect ototoxicity early",
                        related_adverse_effects=["Ototoxicity"]
                    ),
                ],
                "ongoing": [
                    MonitoringParameter(
                        parameter_name="Vancomycin Trough Level",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="After 4-5 doses (or ~48-72 hrs), then before each dose after steady state",
                        rationale="Ensure therapeutic level (15-20 mcg/mL) to maximize efficacy and minimize toxicity",
                        related_adverse_effects=["Nephrotoxicity", "Ototoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Serum Creatinine",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Every 2-3 days initially, then daily or every other day",
                        rationale="Monitor for nephrotoxicity; hold dose if Cr rises >50% or >2 mg/dL",
                        related_adverse_effects=["Nephrotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Clinical Assessment for Red Man Syndrome",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="During each infusion",
                        rationale="Assess for flushing, pruritus, erythema; adjust infusion rate if needed",
                        related_adverse_effects=["Red Man Syndrome"]
                    ),
                    MonitoringParameter(
                        parameter_name="IV Site Assessment",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Daily",
                        rationale="Monitor for phlebitis; rotate sites if using peripheral line",
                        related_adverse_effects=["Phlebitis"]
                    ),
                ]
            },
            "amphotericin b": {
                "baseline": [
                    MonitoringParameter(
                        parameter_name="Comprehensive Metabolic Panel (CMP)",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline creatinine, electrolytes (K+, Mg2+, Ca2+) for comparison",
                        related_adverse_effects=["Nephrotoxicity", "Hypokalemia", "Hypomagnesemia"]
                    ),
                    MonitoringParameter(
                        parameter_name="Liver Function Tests (LFTs)",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline hepatic function",
                        related_adverse_effects=["Hepatotoxicity"]
                    ),
                ],
                "ongoing": [
                    MonitoringParameter(
                        parameter_name="Serum Creatinine & BUN",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Every other day or daily for high-risk patients",
                        rationale="Monitor for nephrotoxicity; primary dose-limiting toxicity",
                        related_adverse_effects=["Nephrotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Serum Potassium (K+)",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Daily or every other day",
                        rationale="Monitor for severe hypokalemia; target K+ >3.5 mEq/L",
                        related_adverse_effects=["Hypokalemia"]
                    ),
                    MonitoringParameter(
                        parameter_name="Serum Magnesium (Mg2+)",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Every other day",
                        rationale="Monitor for hypomagnesemia which worsens hypokalemia",
                        related_adverse_effects=["Hypomagnesemia"]
                    ),
                    MonitoringParameter(
                        parameter_name="LFTs (ALT, AST, Bilirubin, Albumin)",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="2-3 times per week",
                        rationale="Monitor for hepatotoxicity",
                        related_adverse_effects=["Hepatotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Vital Signs & Infusion Reactions",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="During and immediately after infusion",
                        rationale="Assess for fever, chills, rigors; rate severity",
                        related_adverse_effects=["Infusion Reactions"]
                    ),
                ]
            },
            "methotrexate": {
                "baseline": [
                    MonitoringParameter(
                        parameter_name="Complete Blood Count (CBC)",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline WBC, RBC, platelets",
                        related_adverse_effects=["Bone Marrow Suppression"]
                    ),
                    MonitoringParameter(
                        parameter_name="Comprehensive Metabolic Panel (CMP)",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline LFTs, renal function",
                        related_adverse_effects=["Hepatotoxicity", "Nephrotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Albumin & INR",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Assess nutritional status and baseline hepatic synthetic function",
                        related_adverse_effects=["Hepatotoxicity"]
                    ),
                ],
                "ongoing": [
                    MonitoringParameter(
                        parameter_name="CBC (WBC, Hgb, Plt)",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Weekly or every 2 weeks initially; then monthly",
                        rationale="Monitor for myelosuppression; hold if WBC <3,000 or Plt <100,000",
                        related_adverse_effects=["Bone Marrow Suppression"]
                    ),
                    MonitoringParameter(
                        parameter_name="LFTs (ALT, AST, Albumin)",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Monthly",
                        rationale="Monitor for cumulative hepatotoxicity and cirrhosis risk",
                        related_adverse_effects=["Hepatotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Serum Creatinine & BUN",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Monthly",
                        rationale="Monitor renal function; nephrotoxicity can limit dosing",
                        related_adverse_effects=["Nephrotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Folic Acid Supplementation",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Daily (non-methotrexate days)",
                        rationale="Reduce toxicity while maintaining efficacy; 1 mg daily standard",
                        related_adverse_effects=["Bone Marrow Suppression", "Hepatotoxicity", "Mucositis"]
                    ),
                ]
            },
            "amiodarone": {
                "baseline": [
                    MonitoringParameter(
                        parameter_name="12-Lead ECG with QTc Measurement",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline QTc to monitor for proarrhythmia risk",
                        related_adverse_effects=["Proarrhythmia"]
                    ),
                    MonitoringParameter(
                        parameter_name="Pulmonary Function Tests (PFTs) & CXR",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline pulmonary function to detect toxicity",
                        related_adverse_effects=["Pulmonary Toxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="LFTs (ALT, AST, Bilirubin, Albumin)",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline hepatic function",
                        related_adverse_effects=["Hepatotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="TSH & Free T4",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish baseline thyroid function",
                        related_adverse_effects=["Thyroid Dysfunction"]
                    ),
                    MonitoringParameter(
                        parameter_name="Comprehensive Metabolic Panel (K+, Mg2+, Ca2+)",
                        monitoring_type=MonitoringType.BASELINE,
                        frequency="Before therapy starts",
                        rationale="Establish electrolyte baseline; abnormalities increase proarrhythmia risk",
                        related_adverse_effects=["Proarrhythmia"]
                    ),
                ],
                "ongoing": [
                    MonitoringParameter(
                        parameter_name="ECG with QTc",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="If symptoms (syncope, palpitations); or QTc >500 ms at baseline",
                        rationale="Monitor for QT prolongation and proarrhythmia",
                        related_adverse_effects=["Proarrhythmia"]
                    ),
                    MonitoringParameter(
                        parameter_name="LFTs (ALT, AST, Bilirubin)",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Every 6 months",
                        rationale="Monitor for cumulative hepatotoxicity",
                        related_adverse_effects=["Hepatotoxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="TSH",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="Annually",
                        rationale="Screen for hypo- or hyperthyroidism",
                        related_adverse_effects=["Thyroid Dysfunction"]
                    ),
                    MonitoringParameter(
                        parameter_name="CXR & Respiratory Assessment",
                        monitoring_type=MonitoringType.ONGOING,
                        frequency="If new dyspnea, cough, or chest pain (stat); routine: every 6-12 months",
                        rationale="Early detection of pulmonary toxicity",
                        related_adverse_effects=["Pulmonary Toxicity"]
                    ),
                    MonitoringParameter(
                        parameter_name="Ophthalmology Exam",
                        monitoring_type=MonitoringType.PERIODIC,
                        frequency="Annually or if visual symptoms",
                        rationale="Screen for corneal deposits and retinal toxicity",
                        related_adverse_effects=["Ocular Toxicity"]
                    ),
                ]
            },
        }

    def get_recommendations(self, drug_name: str, drug_class: str, adverse_effects: List[AdverseEffect]) -> List[MonitoringParameter]:
        """Get monitoring recommendations for a drug."""
        drug_key = drug_name.lower().strip()
        recommendations = []

        if drug_key in self.guidelines:
            guidelines = self.guidelines[drug_key]
            if "baseline" in guidelines:
                recommendations.extend(guidelines["baseline"])
            if "ongoing" in guidelines:
                recommendations.extend(guidelines["ongoing"])

        return recommendations
