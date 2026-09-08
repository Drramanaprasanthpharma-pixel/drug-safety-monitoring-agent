from __future__ import annotations
from itertools import combinations
from . import data_loader as dl


def analyze_interactions(drug_ids: list[str]) -> list[dict]:
    """Check every pairwise combination of selected drugs against the
    curated interaction ruleset. Unmatched pairs are omitted rather than
    guessed — the system does not fabricate interaction data for pairs
    it has no rule for.
    """
    results = []
    for a, b in combinations(sorted(set(drug_ids)), 2):
        rule = dl.find_interaction(a, b)
        if not rule:
            continue
        drug_a = dl.get_drug(a)
        drug_b = dl.get_drug(b)
        results.append({
            "drug_a": drug_a["generic_name"],
            "drug_b": drug_b["generic_name"],
            "severity": rule["severity"],
            "mechanism": rule["mechanism"],
            "mechanism_detail": rule["mechanism_detail"],
            "clinical_consequence": rule["clinical_consequence"],
            "recommended_action": rule["recommended_action"],
            "action_detail": rule["action_detail"],
            "evidence": rule["evidence"],
        })
    # Surface the most clinically urgent interactions first.
    order = {"Contraindicated": 0, "Major": 1, "Moderate": 2, "Minor": 3, "Unknown": 4}
    results.sort(key=lambda r: order.get(r["severity"], 5))
    return results
