"""
Local drug information database.
Contains demonstration data for testing and development.
"""

from typing import Optional, List, Dict
from agent.tools import Drug, AdverseEffect, WarningSign, RiskLevel, MonitoringType


class LocalDrugDatabase:
    """
    Local demonstration database of drugs and their safety profiles.
    This is NOT a replacement for authoritative clinical references.
    """

    def __init__(self):
        """Initialize the local drug database."""
        self.drugs = self._initialize_drug_data()

    def _initialize_drug_data(self) -> Dict[str, dict]:
        """Initialize demonstration drug data."""
        return {
            "vancomycin": {
                "name": "Vancomycin",
                "brand_names": ["Vancocin"],
                "drug_class": "Glycopeptide Antibiotic",
                "generic_name": "Vancomycin hydrochloride",
                "adverse_effects": [
                    AdverseEffect(
                        effect_name="Nephrotoxicity (Kidney damage)",
                        organ_system="Renal System",
                        risk_level=RiskLevel.HIGH,
                        incidence="5-25%",
                        mechanism="Direct tubular toxicity, especially with high serum levels",
                        clinical_importance="Can progress to acute kidney injury (AKI)"
                    ),
                    AdverseEffect(
                        effect_name="Ototoxicity (Hearing loss)",
                        organ_system="Auditory System",
                        risk_level=RiskLevel.HIGH,
                        incidence="1-5%",
                        mechanism="Damage to cochlear hair cells",
                        clinical_importance="Can be permanent, risk increases with high trough levels"
                    ),
                    AdverseEffect(
                        effect_name="Red Man Syndrome",
                        organ_system="Integumentary (Skin)",
                        risk_level=RiskLevel.MODERATE,
                        incidence="40-60% without premedication",
                        mechanism="Mast cell degranulation from rapid infusion",
                        clinical_importance="Preventable with premedication and slow infusion"
                    ),
                    AdverseEffect(
                        effect_name="Phlebitis",
                        organ_system="Vascular System",
                        risk_level=RiskLevel.MODERATE,
                        incidence="~30%",
                        mechanism="Irritation of vein from drug pH and osmolality",
                        clinical_importance="Managed with central line or dilution"
                    ),
                    AdverseEffect(
                        effect_name="Drug Fever",
                        organ_system="Systemic",
                        risk_level=RiskLevel.LOW,
                        incidence="<1%",
                        mechanism="Immune-mediated reaction",
                        clinical_importance="Resolves after drug discontinuation"
                    ),
                ],
                "warning_signs": [
                    WarningSign(
                        sign_description="Serum creatinine rise >50% from baseline or >2 mg/dL",
                        adverse_effect="Nephrotoxicity",
                        action_required="Check vancomycin trough level, reduce dose, consider alternative",
                        severity=RiskLevel.HIGH
                    ),
                    WarningSign(
                        sign_description="Tinnitus, hearing loss, or vertigo",
                        adverse_effect="Ototoxicity",
                        action_required="Immediate audiometry, discontinue if confirmed, check trough levels",
                        severity=RiskLevel.HIGH
                    ),
                    WarningSign(
                        sign_description="Erythema, flushing, pruritus during infusion",
                        adverse_effect="Red Man Syndrome",
                        action_required="Slow infusion rate, premedicate with antihistamine, consider corticosteroid",
                        severity=RiskLevel.MODERATE
                    ),
                ],
                "key_considerations": [
                    "Therapeutic drug monitoring (TDM) is ESSENTIAL. Target trough: 15-20 mcg/mL for serious infections",
                    "Risk of nephrotoxicity and ototoxicity increases significantly when combined with aminoglycosides",
                    "Infuse over at least 60 minutes to reduce Red Man Syndrome",
                    "Requires dose adjustment in renal impairment",
                    "Line selection important: peripheral lines increase phlebitis risk"
                ],
                "is_complete": True
            },
            "amphotericin b": {
                "name": "Amphotericin B",
                "brand_names": ["Fungizone", "AmBisome", "Abelcet"],
                "drug_class": "Polyene Antifungal",
                "generic_name": "Amphotericin B",
                "adverse_effects": [
                    AdverseEffect(
                        effect_name="Nephrotoxicity (Kidney damage)",
                        organ_system="Renal System",
                        risk_level=RiskLevel.HIGH,
                        incidence="80% with conventional formulation",
                        mechanism="Direct tubular toxicity and vasoconstriction",
                        clinical_importance="Most common dose-limiting toxicity; prefer lipid formulations"
                    ),
                    AdverseEffect(
                        effect_name="Hypokalemia (Low potassium)",
                        organ_system="Electrolyte/Renal",
                        risk_level=RiskLevel.HIGH,
                        incidence="70-80%",
                        mechanism="Increased renal potassium wasting",
                        clinical_importance="Can cause severe cardiac arrhythmias; requires aggressive supplementation"
                    ),
                    AdverseEffect(
                        effect_name="Hypomagnesemia (Low magnesium)",
                        organ_system="Electrolyte/Renal",
                        risk_level=RiskLevel.MODERATE,
                        incidence="~50%",
                        mechanism="Increased renal magnesium wasting",
                        clinical_importance="Worsens hypokalemia if not corrected"
                    ),
                    AdverseEffect(
                        effect_name="Infusion Reactions (chills, fever, rigors)",
                        organ_system="Systemic",
                        risk_level=RiskLevel.MODERATE,
                        incidence="80% conventional formulation",
                        mechanism="Immune-mediated from fungal cell wall interaction",
                        clinical_importance="Reduced with premedication and lipid formulations"
                    ),
                    AdverseEffect(
                        effect_name="Hepatotoxicity (Liver damage)",
                        organ_system="Hepatic System",
                        risk_level=RiskLevel.MODERATE,
                        incidence="~20%",
                        mechanism="Direct hepatocellular injury",
                        clinical_importance="Monitor LFTs regularly"
                    ),
                ],
                "warning_signs": [
                    WarningSign(
                        sign_description="Serum creatinine >2.0 mg/dL or doubling from baseline",
                        adverse_effect="Nephrotoxicity",
                        action_required="Consider holding dose, hydrate with normal saline, switch to lipid formulation if possible",
                        severity=RiskLevel.HIGH
                    ),
                    WarningSign(
                        sign_description="Muscle weakness, cardiac palpitations, EKG changes (peaked T waves)",
                        adverse_effect="Hypokalemia",
                        action_required="Stat potassium level and ECG, aggressive IV potassium supplementation",
                        severity=RiskLevel.HIGH
                    ),
                    WarningSign(
                        sign_description="Severe rigors, high fever (>39°C), hypotension during infusion",
                        adverse_effect="Infusion Reaction",
                        action_required="Premedicate with acetaminophen, diphenhydramine, consider meperidine; slow infusion",
                        severity=RiskLevel.MODERATE
                    ),
                ],
                "key_considerations": [
                    "Lipid formulations (AmBisome, Abelcet) have SIGNIFICANTLY lower nephrotoxicity than conventional",
                    "Daily IV hydration with normal saline (500-1000 mL) reduces nephrotoxicity",
                    "Electrolyte repletion is ESSENTIAL: aggressive K+ and Mg2+ supplementation required",
                    "Premedication (acetaminophen, diphenhydramine, meperidine) reduces infusion reactions",
                    "Use peripheral line for conventional formulation; lipid formulations can be peripheral"
                ],
                "is_complete": True
            },
            "methotrexate": {
                "name": "Methotrexate",
                "brand_names": ["Rheumatrex", "Trexall"],
                "drug_class": "Antimetabolite / Immunosuppressant",
                "generic_name": "Methotrexate",
                "adverse_effects": [
                    AdverseEffect(
                        effect_name="Bone Marrow Suppression (Myelosuppression)",
                        organ_system="Hematologic System",
                        risk_level=RiskLevel.HIGH,
                        incidence="10-30%",
                        mechanism="Inhibition of DNA synthesis in rapidly dividing cells",
                        clinical_importance="Can cause severe anemia, leukopenia, thrombocytopenia"
                    ),
                    AdverseEffect(
                        effect_name="Hepatotoxicity (Liver cirrhosis/fibrosis)",
                        organ_system="Hepatic System",
                        risk_level=RiskLevel.HIGH,
                        incidence="~3-5% chronic therapy",
                        mechanism="Cumulative toxicity from folate antagonism",
                        clinical_importance="Irreversible; total cumulative dose is key risk factor"
                    ),
                    AdverseEffect(
                        effect_name="Nephrotoxicity (Kidney damage)",
                        organ_system="Renal System",
                        risk_level=RiskLevel.HIGH,
                        incidence="~8%",
                        mechanism="Crystal-induced tubular obstruction, especially high-dose MTX",
                        clinical_importance="Preventable with hydration and urine alkalinization"
                    ),
                    AdverseEffect(
                        effect_name="Mucositis (Mouth ulcers)",
                        organ_system="Gastrointestinal",
                        risk_level=RiskLevel.MODERATE,
                        incidence="30-60%",
                        mechanism="Damage to rapidly dividing mucosal cells",
                        clinical_importance="Can progress to severe ulceration"
                    ),
                    AdverseEffect(
                        effect_name="Immunosuppression",
                        organ_system="Immune System",
                        risk_level=RiskLevel.MODERATE,
                        incidence="~40%",
                        mechanism="Inhibition of T-cell and B-cell function",
                        clinical_importance="Increased risk of infections"
                    ),
                ],
                "warning_signs": [
                    WarningSign(
                        sign_description="WBC <3,000/mcL or platelets <100,000/mcL",
                        adverse_effect="Bone Marrow Suppression",
                        action_required="Hold dose, repeat CBC, consider folinic acid rescue",
                        severity=RiskLevel.HIGH
                    ),
                    WarningSign(
                        sign_description="ALT >3x ULN or albumin <3.5 g/dL",
                        adverse_effect="Hepatotoxicity",
                        action_required="Hold MTX, consider liver biopsy if cumulative dose >100 g/m², evaluate cirrhosis risk",
                        severity=RiskLevel.HIGH
                    ),
                    WarningSign(
                        sign_description="Serum creatinine >1.5 mg/dL or creatinine clearance <60 mL/min",
                        adverse_effect="Nephrotoxicity",
                        action_required="Hold dose, hydrate, urine alkalinization if high-dose MTX",
                        severity=RiskLevel.HIGH
                    ),
                ],
                "key_considerations": [
                    "MANDATORY folic acid supplementation (1 mg daily) to reduce toxicity",
                    "CBC and CMP required before each dose (every 1-2 weeks initially)",
                    "Liver function tests and albumin monitoring essential for cumulative toxicity assessment",
                    "Cumulative lifetime dose should not exceed 100-150 g/m² due to hepatic cirrhosis risk",
                    "Interaction with NSAIDs and other drugs affecting renal clearance increases toxicity",
                    "Requires dose adjustment for renal impairment"
                ],
                "is_complete": True
            },
            "amiodarone": {
                "name": "Amiodarone",
                "brand_names": ["Cordarone", "Nexterone"],
                "drug_class": "Antiarrhythmic (Class III)",
                "generic_name": "Amiodarone hydrochloride",
                "adverse_effects": [
                    AdverseEffect(
                        effect_name="Pulmonary Toxicity (Pneumonitis/Fibrosis)",
                        organ_system="Respiratory System",
                        risk_level=RiskLevel.HIGH,
                        incidence="1-17%",
                        mechanism="Iodine-induced inflammation and fibrosis",
                        clinical_importance="Can be fatal; irreversible in severe cases"
                    ),
                    AdverseEffect(
                        effect_name="Hepatotoxicity (Liver damage)",
                        organ_system="Hepatic System",
                        risk_level=RiskLevel.HIGH,
                        incidence="~25% elevated LFTs, 1% cirrhosis",
                        mechanism="Accumulation of drug and metabolites in hepatocytes",
                        clinical_importance="Can progress to cirrhosis; cumulative dose-dependent"
                    ),
                    AdverseEffect(
                        effect_name="Thyroid Dysfunction (Hypo- or hyperthyroidism)",
                        organ_system="Endocrine System",
                        risk_level=RiskLevel.MODERATE,
                        incidence="~20%",
                        mechanism="High iodine content (75 mg/200 mg tablet) interferes with thyroid function",
                        clinical_importance="Both hypo- and hyperthyroidism can occur"
                    ),
                    AdverseEffect(
                        effect_name="Ocular Toxicity (Corneal deposits, visual disturbance)",
                        organ_system="Ocular System",
                        risk_level=RiskLevel.MODERATE,
                        incidence="~20-30%",
                        mechanism="Deposition of drug in cornea and retina",
                        clinical_importance="Usually reversible upon discontinuation"
                    ),
                    AdverseEffect(
                        effect_name="Proarrhythmia (Torsades de Pointes)",
                        organ_system="Cardiac System",
                        risk_level=RiskLevel.MODERATE,
                        incidence="<1%",
                        mechanism="QT prolongation, drug interactions, electrolyte abnormalities",
                        clinical_importance="Can be life-threatening"
                    ),
                ],
                "warning_signs": [
                    WarningSign(
                        sign_description="New or worsening dyspnea, persistent cough, chest pain, fever",
                        adverse_effect="Pulmonary Toxicity",
                        action_required="Stat CXR, PFTs, consider CT chest; discontinue amiodarone if pneumonitis confirmed",
                        severity=RiskLevel.HIGH
                    ),
                    WarningSign(
                        sign_description="ALT >3x ULN or signs of jaundice/ascites",
                        adverse_effect="Hepatotoxicity",
                        action_required="Hold dose, check hepatitis serologies, consider liver biopsy",
                        severity=RiskLevel.HIGH
                    ),
                    WarningSign(
                        sign_description="Symptoms of hypothyroidism (fatigue, weight gain) or hyperthyroidism (palpitations, tremor)",
                        adverse_effect="Thyroid Dysfunction",
                        action_required="Check TSH and free T4, adjust thyroid replacement or antithyroid drug if needed",
                        severity=RiskLevel.MODERATE
                    ),
                    WarningSign(
                        sign_description="Syncope, palpitations, QTc >500 ms on ECG",
                        adverse_effect="Proarrhythmia",
                        action_required="Stat ECG, check electrolytes (K+, Mg2+, Ca2+), consider dose reduction or discontinuation",
                        severity=RiskLevel.MODERATE
                    ),
                ],
                "key_considerations": [
                    "Amiodarone has EXTREMELY long half-life (26-107 days); effects persist months after discontinuation",
                    "Baseline assessment required: PFTs, CXR, LFTs, TSH, ECG (baseline QTc)",
                    "Regular monitoring during therapy: LFTs every 6 months, TSH annually, ECG if symptoms",
                    "High iodine content (75 mg/tablet) means patients should avoid other iodine sources",
                    "Numerous drug interactions via CYP3A4 and CYP2C9; increases levels of warfarin, digoxin, beta-blockers, statins",
                    "QT prolongation risk, especially with electrolyte abnormalities or other QT-prolonging drugs",
                    "Loading dose required for efficacy; maintenance is lower"
                ],
                "is_complete": True
            },
        }

    def search(self, drug_name: str) -> Optional[Drug]:
        """Search for a drug by name."""
        drug_key = drug_name.lower().strip()
        if drug_key in self.drugs:
            drug_data = self.drugs[drug_key]
            return Drug(
                name=drug_data["name"],
                brand_names=drug_data["brand_names"],
                drug_class=drug_data["drug_class"],
                generic_name=drug_data["generic_name"],
            )
        return None

    def get_adverse_effects(self, drug_name: str) -> List[AdverseEffect]:
        """Get adverse effects for a drug."""
        drug_key = drug_name.lower().strip()
        if drug_key in self.drugs:
            return self.drugs[drug_key]["adverse_effects"]
        return []

    def get_warning_signs(self, drug_name: str, adverse_effects: List[AdverseEffect]) -> List[WarningSign]:
        """Get warning signs for a drug."""
        drug_key = drug_name.lower().strip()
        if drug_key in self.drugs:
            return self.drugs[drug_key]["warning_signs"]
        return []

    def get_key_considerations(self, drug_name: str) -> List[str]:
        """Get key considerations for a drug."""
        drug_key = drug_name.lower().strip()
        if drug_key in self.drugs:
            return self.drugs[drug_key]["key_considerations"]
        return []

    def is_complete(self, drug_name: str) -> bool:
        """Check if drug information is complete."""
        drug_key = drug_name.lower().strip()
        if drug_key in self.drugs:
            return self.drugs[drug_key].get("is_complete", False)
        return False
