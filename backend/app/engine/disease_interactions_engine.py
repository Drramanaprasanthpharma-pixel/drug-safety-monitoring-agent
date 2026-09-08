from __future__ import annotations
from . import data_loader as dl


def analyze_disease_interactions(drug_ids: list[str], diagnoses: list[str]) -> list[dict]:
    if not diagnoses:
        return []
    diag_lower = [d.lower() for d in diagnoses]
    rules = dl.load_disease_interactions()
    results = []
    for drug_id in drug_ids:
        drug = dl.get_drug(drug_id)
        if not drug:
            continue
        for rule in rules.get(drug_id, []):
            if any(kw in diag for kw in rule["keywords"] for diag in diag_lower):
                matched_diag = next(
                    (d for d in diagnoses if any(kw in d.lower() for kw in rule["keywords"])),
                    diagnoses[0],
                )
                results.append({
                    "condition": matched_diag,
                    "drug": drug["generic_name"],
                    "risk": rule["risk"],
                    "recommendation": rule["recommendation"],
                    "evidence": {
                        "source": "Curated drug-disease interaction ruleset (FDA labeling-informed)",
                        "reference": "Consult current full prescribing information",
                        "date": "General labeling knowledge",
                        "confidence": rule["confidence"],
                    },
                })
    return results
