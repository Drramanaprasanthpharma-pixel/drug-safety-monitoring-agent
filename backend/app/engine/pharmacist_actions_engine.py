from __future__ import annotations


def build_pharmacist_actions(interactions: list[dict], priority_organs: list[dict],
                              red_flags: list[dict], disease_interactions: list[dict],
                              patient_risk_factors: list[dict]) -> list[dict]:
    actions = []

    for i in interactions:
        if i["severity"] in ("Contraindicated", "Major"):
            actions.append({
                "action": f"Contact prescriber regarding {i['drug_a']} + {i['drug_b']}",
                "rationale": f"{i['severity']} interaction: {i['clinical_consequence']} — recommended action: {i['recommended_action']}.",
                "evidence": i["evidence"],
            })
        elif i["severity"] == "Moderate":
            actions.append({
                "action": f"Recommend monitoring plan for {i['drug_a']} + {i['drug_b']}",
                "rationale": i["clinical_consequence"],
                "evidence": i["evidence"],
            })

    for organ in priority_organs:
        if organ["priority"] in ("High", "Critical"):
            actions.append({
                "action": f"Recommend {organ['organ'].lower()} monitoring per identified parameters",
                "rationale": organ["reason"],
                "evidence": organ["evidence"],
            })

    for d in disease_interactions:
        actions.append({
            "action": f"Review {d['drug']} appropriateness given {d['condition']}",
            "rationale": d["risk"] + " " + d["recommendation"],
            "evidence": d["evidence"],
        })

    if red_flags:
        actions.append({
            "action": "Document and escalate identified red flags",
            "rationale": f"{len(red_flags)} red flag(s) require prescriber awareness and documentation in the patient record.",
            "evidence": None,
        })

    for factor in patient_risk_factors:
        if "allerg" in factor["factor"].lower():
            actions.append({
                "action": "Verify allergy history before dispensing",
                "rationale": factor["detail"],
                "evidence": None,
            })

    # Always-present baseline actions
    actions.append({
        "action": "Verify indication and dose against current orders",
        "rationale": "Standard medication safety review step for any new or continued therapy.",
        "evidence": None,
    })
    actions.append({
        "action": "Counsel patient on key adverse effects and when to seek care",
        "rationale": "Patient awareness of warning signs supports early detection of toxicity.",
        "evidence": None,
    })
    actions.append({
        "action": "Document pharmacist review in the patient record",
        "rationale": "Supports continuity of care and audit trail of clinical decision-making.",
        "evidence": None,
    })

    return actions
