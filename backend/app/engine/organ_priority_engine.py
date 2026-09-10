"""
Organ/system monitoring prioritization.

This is a deterministic scoring model, not a validated clinical risk
calculator. Every score is built from explicit, auditable factors (organ
toxicity risk level from the curated drug data, number of contributing
drugs, and patient-specific modifiers) so the "why was this flagged"
explanation can always be reconstructed from the same inputs. Section 16
of the spec ("Explainable AI") requires this traceability, and section 20
requires the rules engine to take precedence over any free-form narrative.
"""
from __future__ import annotations
from . import data_loader as dl

BASE_POINTS = {"Critical": 100, "High": 80, "Moderate": 55, "Low": 30}
ADDITIONAL_DRUG_BONUS = 10  # per extra drug implicating the same organ
MAX_SCORE = 100


def _level_from_score(score: int) -> str:
    if score >= 85:
        return "Critical"
    if score >= 65:
        return "High"
    if score >= 40:
        return "Moderate"
    return "Low"


def compute_organ_priorities(drug_ids: list[str], patient=None) -> tuple[list[dict], list[dict]]:
    """
    Returns (priority_organs, organ_toxicity_detail):
      - priority_organs: one aggregated entry per organ, ranked, with a
        0-100 "relative monitoring priority" percent (NOT an incidence rate).
      - organ_toxicity_detail: the underlying per-drug, per-organ facts
        that were aggregated (for the detail view / audit trail).
    """
    organ_buckets: dict[str, list[dict]] = {}
    detail_rows: list[dict] = []

    for drug_id in drug_ids:
        drug = dl.get_drug(drug_id)
        if not drug:
            continue
        for entry in drug.get("organ_toxicity", []):
            organ = entry["organ"]
            organ_buckets.setdefault(organ, []).append({**entry, "drug": drug["generic_name"]})
            detail_rows.append({
                "drug": drug["generic_name"],
                "organ": organ,
                "risk_level": entry["risk_level"],
                "reason": entry["reason"],
                "toxicity": entry["toxicity"],
                "monitoring_parameters": entry["monitoring_parameters"],
                "frequency": entry["frequency"],
                "thresholds": entry["thresholds"],
                "evidence": {
                    "source": entry["source"],
                    "reference": "See drug-specific prescribing information",
                    "date": "General labeling knowledge",
                    "confidence": "Moderate",
                },
            })

    priority_organs = []
    for organ, entries in organ_buckets.items():
        base_level = max(entries, key=lambda e: BASE_POINTS[e["risk_level"]])["risk_level"]
        score = BASE_POINTS[base_level]
        contributing_drugs = sorted({e["drug"] for e in entries})
        if len(contributing_drugs) > 1:
            score += ADDITIONAL_DRUG_BONUS * (len(contributing_drugs) - 1)

        reasons = [f"{e['drug']}: {e['reason']}" for e in entries]
        patient_factors = []

        if patient:
            if organ == "Renal" and patient.get("egfr") is not None:
                if patient["egfr"] < 30:
                    score += 25
                    patient_factors.append(f"eGFR {patient['egfr']} mL/min/1.73m² (severe renal impairment)")
                elif patient["egfr"] < 60:
                    score += 15
                    patient_factors.append(f"eGFR {patient['egfr']} mL/min/1.73m² (reduced renal function)")
            if organ == "Hepatic" and patient.get("hepatic_impairment") in ("moderate", "severe"):
                score += 20
                patient_factors.append(f"Reported {patient['hepatic_impairment']} hepatic impairment")
            elif organ == "Hepatic" and patient.get("hepatic_impairment") == "mild":
                score += 10
                patient_factors.append("Reported mild hepatic impairment")
            if organ == "Hematologic" and patient.get("age") and patient["age"] >= 75:
                score += 5
                patient_factors.append(f"Age {patient['age']} (falls/bleeding risk)")
            if organ == "Cardiovascular" and patient.get("lab_values", {}).get("potassium") is not None:
                k = patient["lab_values"]["potassium"]
                if k < 3.5:
                    score += 15
                    patient_factors.append(f"Potassium {k} mEq/L (hypokalemia potentiates cardiac toxicity)")

        score = min(score, MAX_SCORE)
        level = _level_from_score(score)

        # Merge monitoring parameters/frequency/threshold text across contributing drugs
        all_params = sorted({p for e in entries for p in e["monitoring_parameters"]})
        frequencies = sorted({e["frequency"] for e in entries})
        thresholds = sorted({e["thresholds"] for e in entries})
        top_source_entry = max(entries, key=lambda e: BASE_POINTS[e["risk_level"]])

        reason_text = "; ".join(reasons)
        if patient_factors:
            reason_text += " | Patient-specific factors: " + "; ".join(patient_factors)

        priority_organs.append({
            "organ": organ,
            "priority": level,
            "relative_priority_percent": score,
            "reason": reason_text,
            "toxicity": "; ".join(sorted({e["toxicity"] for e in entries})),
            "monitoring_parameters": all_params,
            "monitoring_frequency": " | ".join(frequencies),
            "intervention_threshold": " | ".join(thresholds),
            "evidence": {
                "source": top_source_entry["source"],
                "reference": "See drug-specific prescribing information",
                "date": "General labeling knowledge",
                "confidence": "Moderate",
            },
        })

    priority_organs.sort(key=lambda o: o["relative_priority_percent"], reverse=True)
    return priority_organs, detail_rows
