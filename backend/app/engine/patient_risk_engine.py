from __future__ import annotations
from . import data_loader as dl


def analyze_patient_risk(drug_ids: list[str], patient: dict | None) -> list[dict]:
    """Returns a list of concrete, explainable patient risk factors.
    Nothing here is inferred beyond what the pharmacist entered plus the
    selected drugs' known high-risk-population flags."""
    if not patient:
        return []

    factors: list[dict] = []
    drugs = [dl.get_drug(d) for d in drug_ids if dl.get_drug(d)]

    age = patient.get("age")
    if age is not None and age >= 65:
        factors.append({
            "factor": "Advanced age",
            "detail": f"Patient age {age} — increased sensitivity to adverse drug effects and altered pharmacokinetics is common in older adults.",
            "affected_organ": None,
        })

    egfr = patient.get("egfr")
    if egfr is not None:
        renally_cleared = [d["generic_name"] for d in drugs if any(o["organ"] == "Renal" for o in d.get("organ_toxicity", [])) or "renal" in d.get("renal_dosing", "").lower()]
        if egfr < 60 and renally_cleared:
            severity = "severe" if egfr < 30 else "reduced"
            factors.append({
                "factor": f"{severity.capitalize()} renal function (eGFR {egfr})",
                "detail": f"Affects clearance of: {', '.join(renally_cleared)}. Dose and/or monitoring adjustment may be needed.",
                "affected_organ": "Renal",
            })

    hepatic = patient.get("hepatic_impairment")
    if hepatic and hepatic != "none":
        hepatically_relevant = [d["generic_name"] for d in drugs if any(o["organ"] == "Hepatic" for o in d.get("organ_toxicity", []))]
        if hepatically_relevant:
            factors.append({
                "factor": f"Hepatic impairment ({hepatic})",
                "detail": f"Affects metabolism/toxicity risk of: {', '.join(hepatically_relevant)}.",
                "affected_organ": "Hepatic",
            })

    if patient.get("pregnant"):
        contraindicated_in_pregnancy = [d["generic_name"] for d in drugs if "Pregnancy" in d.get("contraindications", [])]
        if contraindicated_in_pregnancy:
            factors.append({
                "factor": "Pregnancy",
                "detail": f"Contraindicated or high-risk in pregnancy: {', '.join(contraindicated_in_pregnancy)}. Confirm with prescriber before continuing.",
                "affected_organ": None,
            })

    total_med_count = len(patient.get("current_medications", [])) + len(drug_ids)
    if total_med_count >= 5:
        factors.append({
            "factor": "Polypharmacy",
            "detail": f"{total_med_count} total medications identified, increasing interaction and adverse-effect risk.",
            "affected_organ": None,
        })

    allergies = [a.lower() for a in patient.get("allergies", [])]
    for d in drugs:
        names = [d["generic_name"].lower()] + [b.lower() for b in d.get("brand_names", [])]
        if any(a in names for a in allergies):
            factors.append({
                "factor": f"Documented allergy to {d['generic_name']}",
                "detail": "Patient-reported allergy matches a selected medication — verify before dispensing/administering.",
                "affected_organ": None,
            })

    lab_values = patient.get("lab_values", {}) or {}
    if "potassium" in lab_values and lab_values["potassium"] < 3.5:
        digoxin_present = any(d["id"] == "digoxin" for d in drugs)
        if digoxin_present:
            factors.append({
                "factor": f"Hypokalemia (K+ {lab_values['potassium']} mEq/L)",
                "detail": "Potentiates digoxin cardiotoxicity — correct potassium and reassess.",
                "affected_organ": "Cardiovascular",
            })

    return factors
