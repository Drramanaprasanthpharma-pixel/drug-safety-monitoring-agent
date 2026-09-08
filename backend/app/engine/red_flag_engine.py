from __future__ import annotations

# Maps a life-threatening adverse effect phrase to escalation guidance.
# Kept intentionally generic ("seek urgent clinical evaluation") rather than
# prescribing specific emergency treatment steps, per spec section 11.
LIFE_THREATENING_ESCALATION = {
    "default": "Escalate to the prescriber/treating clinician promptly; do not wait for the next scheduled visit.",
}


def build_red_flags(interactions: list[dict], organ_toxicity_detail: list[dict],
                     adverse_effects: list[dict], patient_risk_factors: list[dict]) -> list[dict]:
    red_flags = []

    for interaction in interactions:
        if interaction["severity"] in ("Contraindicated", "Major"):
            red_flags.append({
                "trigger": f"{interaction['drug_a']} + {interaction['drug_b']} — {interaction['severity']} interaction",
                "consequence": interaction["clinical_consequence"],
                "immediate_consideration": interaction["action_detail"],
                "escalation": "Contact prescriber before continuing both agents as currently ordered." if interaction["severity"] == "Contraindicated"
                              else "Flag for prescriber review and confirm a monitoring/dose-adjustment plan is in place.",
                "source_drug": f"{interaction['drug_a']} + {interaction['drug_b']}",
            })

    for ae in adverse_effects:
        for effect in ae["life_threatening"]:
            red_flags.append({
                "trigger": f"{ae['drug']}: potential for {effect}",
                "consequence": effect,
                "immediate_consideration": "Assess for early signs/symptoms at each encounter; this is a known life-threatening effect of this medication.",
                "escalation": LIFE_THREATENING_ESCALATION["default"],
                "source_drug": ae["drug"],
            })

    # Patient-specific risk factors that compound a known high-risk organ system
    for factor in patient_risk_factors:
        if factor.get("affected_organ") and any(
            row["organ"] == factor["affected_organ"] and row["risk_level"] in ("High", "Critical")
            for row in organ_toxicity_detail
        ):
            red_flags.append({
                "trigger": factor["factor"],
                "consequence": factor["detail"],
                "immediate_consideration": f"This risk factor compounds an already high-priority {factor['affected_organ'].lower()} toxicity concern for the selected medication(s).",
                "escalation": "Review with prescriber before continuing current regimen unchanged.",
                "source_drug": None,
            })

    return red_flags
