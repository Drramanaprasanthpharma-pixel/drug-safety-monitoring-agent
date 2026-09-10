from __future__ import annotations
from . import data_loader as dl

RISK_ORDER = {"Critical": 0, "High": 1, "Moderate": 2, "Low": 3}


def build_monitoring_table(drug_ids: list[str]) -> list[dict]:
    """Only surfaces monitoring parameters that are actually relevant to the
    selected medication(s) — it does not add tests just because they exist
    (spec section 6)."""
    merged: dict[str, dict] = {}
    for drug_id in drug_ids:
        drug = dl.get_drug(drug_id)
        if not drug:
            continue
        for row in drug.get("monitoring_parameters", []):
            key = row["parameter"]
            if key not in merged:
                merged[key] = {
                    "parameter": row["parameter"],
                    "why": row["why"],
                    "baseline": row["baseline"],
                    "follow_up": row["follow_up"],
                    "alert_threshold": row["alert_threshold"],
                    "risk": row["risk"],
                    "triggered_by": [drug["generic_name"]],
                }
            else:
                merged[key]["triggered_by"].append(drug["generic_name"])
                # Keep the more urgent risk label and merge free-text guidance
                if RISK_ORDER[row["risk"]] < RISK_ORDER[merged[key]["risk"]]:
                    merged[key]["risk"] = row["risk"]
                if drug["generic_name"] not in merged[key]["why"]:
                    merged[key]["why"] += f" Also relevant for {drug['generic_name']}."
    rows = list(merged.values())
    rows.sort(key=lambda r: RISK_ORDER[r["risk"]])
    return rows


def build_vital_signs(drug_ids: list[str]) -> list[dict]:
    merged: dict[str, dict] = {}
    for drug_id in drug_ids:
        drug = dl.get_drug(drug_id)
        if not drug:
            continue
        for row in drug.get("vital_signs", []):
            key = row["parameter"]
            if key not in merged:
                merged[key] = {"parameter": row["parameter"], "why": row["why"], "triggered_by": [drug["generic_name"]]}
            else:
                merged[key]["triggered_by"].append(drug["generic_name"])
    return list(merged.values())


def build_adverse_effects(drug_ids: list[str]) -> list[dict]:
    results = []
    for drug_id in drug_ids:
        drug = dl.get_drug(drug_id)
        if not drug:
            continue
        ae = drug["adverse_effects"]
        results.append({
            "drug": drug["generic_name"],
            "common": ae["common"],
            "serious": ae["serious"],
            "life_threatening": ae["life_threatening"],
            "boxed_warning": drug.get("boxed_warning"),
        })
    return results


def build_monitoring_schedule(drug_ids: list[str]) -> dict[str, list[str]]:
    """Generates a before/early/ongoing schedule using ONLY the monitoring
    parameters and frequencies already present in the curated dataset —
    the engine does not invent new intervals (spec section 14)."""
    before, ongoing = set(), []
    for drug_id in drug_ids:
        drug = dl.get_drug(drug_id)
        if not drug:
            continue
        for row in drug.get("monitoring_parameters", []):
            if row["baseline"] not in ("No", None):
                before.add(row["parameter"])
            ongoing.append(f"{row['parameter']} — {row['follow_up']} ({drug['generic_name']})")
    return {
        "before_treatment": sorted(before) if before else ["No baseline-specific parameters identified for the selected medication(s)."],
        "early_treatment": [
            "Monitor for early adverse effects and interaction-related symptoms.",
            "Reassess after any dose change or addition of an interacting medication.",
        ],
        "ongoing": ongoing if ongoing else [
            "Monitoring frequency should be individualized based on clinical context and applicable guideline/product labeling."
        ],
    }
