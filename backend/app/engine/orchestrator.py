"""
Orchestrates the pipeline described in spec section 19:

  User Input -> Drug normalization -> Drug database -> Interaction database
  -> Clinical guidelines / Regulatory labeling (encoded in the curated data)
  -> Patient-specific analysis -> Safety rules engine -> AI explanation
  -> Risk prioritization -> Dashboard (JSON returned to the frontend)

Every "explanation" string here is template-generated from the structured
facts already computed by the deterministic engines — never freely
generated pharmacology. This keeps the rules engine authoritative per
spec section 20.

Step 1 (drug normalization) is the one place this upgrade changes: a name
the curated dataset and AI cache don't already recognize is no longer an
immediate failure. It's handed to agent.drug_agent, which normalizes it
further (aliases, spelling), and — only if AI retrieval is configured —
attempts to retrieve, validate, and cache a real clinical profile for it
before this function ever sees it. Everything from step 2 onward is
completely unchanged: it still only ever deals with a canonical drug_id
and dl.get_drug(), exactly as before.
"""
from __future__ import annotations
from . import data_loader as dl
from . import interactions_engine, organ_priority_engine, monitoring_engine
from . import disease_interactions_engine, patient_risk_engine, red_flag_engine
from . import scoring_engine, pharmacist_actions_engine, audit
from ..agent.errors import AmbiguousDrugError, UnknownDrugError  # re-exported for existing call sites/tests

__all__ = ["run_analysis", "UnknownDrugError", "AmbiguousDrugError"]


def run_analysis(drug_names: list[str], patient: dict | None, demo_mode: bool = False) -> dict:
    # 1. Drug normalization — local lookup first (no network), then the
    #    agent's alias/fuzzy/AI-retrieval fallback for anything unresolved.
    from ..agent import drug_agent  # local import: avoids a circular import at module load time

    drug_ids = []
    for name in drug_names:
        drug_id = dl.resolve_drug_id(name)
        if not drug_id:
            drug_id = drug_agent.resolve_and_ensure(name)  # raises UnknownDrugError / AmbiguousDrugError
        if drug_id not in drug_ids:
            drug_ids.append(drug_id)

    drugs = [dl.get_drug(d) for d in drug_ids]
    generic_names = [d["generic_name"] for d in drugs]

    # 2. Interaction database
    interactions = interactions_engine.analyze_interactions(drug_ids)

    # 3. Regulatory labeling -> organ toxicity + monitoring + adverse effects
    priority_organs, organ_toxicity_detail = organ_priority_engine.compute_organ_priorities(drug_ids, patient)
    monitoring = monitoring_engine.build_monitoring_table(drug_ids)
    vital_signs = monitoring_engine.build_vital_signs(drug_ids)
    adverse_effects = monitoring_engine.build_adverse_effects(drug_ids)
    monitoring_schedule = monitoring_engine.build_monitoring_schedule(drug_ids)

    # 4. Patient-specific analysis
    diagnoses = (patient or {}).get("diagnoses", [])
    disease_interactions = disease_interactions_engine.analyze_disease_interactions(drug_ids, diagnoses)
    patient_risk_factors = patient_risk_engine.analyze_patient_risk(drug_ids, patient)

    # 5. Safety rules engine -> red flags
    red_flags = red_flag_engine.build_red_flags(interactions, organ_toxicity_detail, adverse_effects, patient_risk_factors)

    # 6. Risk prioritization
    overall_risk = scoring_engine.compute_overall_risk(priority_organs, interactions, red_flags, patient_risk_factors)

    # 7. Pharmacist actions
    pharmacist_actions = pharmacist_actions_engine.build_pharmacist_actions(
        interactions, priority_organs, red_flags, disease_interactions, patient_risk_factors
    )

    # 8. Evidence roll-up
    evidence_pool = []
    for d in drugs:
        evidence_pool.extend(d.get("evidence", []))
    for i in interactions:
        evidence_pool.append(i["evidence"])
    for di in disease_interactions:
        evidence_pool.append(di["evidence"])
    seen = set()
    dedup_evidence = []
    for e in evidence_pool:
        key = (e["source"], e.get("confidence"))
        if key not in seen:
            seen.add(key)
            dedup_evidence.append(e)

    # 9. Dashboard summary cards
    top_organ = priority_organs[0] if priority_organs else None
    dashboard = {
        "overall_safety": overall_risk["category"],
        "overall_risk_category": overall_risk["category"],
        "priority_organ": top_organ["organ"] if top_organ else "None identified",
        "priority_organ_level": top_organ["priority"] if top_organ else "Low",
        "interaction_count": len(interactions),
        "monitoring_param_count": len(monitoring),
        "red_flag_count": len(red_flags),
        "patient_risk_factor_count": len(patient_risk_factors),
    }

    # 10. Audit trail (no identifiable patient data persisted)
    audit_id = audit.record_analysis(
        drug_ids=drug_ids,
        patient_provided=patient is not None,
        evidence_sources=[e["source"] for e in dedup_evidence],
        demo_mode=demo_mode,
    )

    return {
        "drugs_analyzed": generic_names,
        "demo_mode": demo_mode,
        "overall_risk": overall_risk,
        "dashboard": dashboard,
        "priority_organs": priority_organs,
        "organ_toxicity_detail": organ_toxicity_detail,
        "interactions": interactions,
        "disease_interactions": disease_interactions,
        "monitoring": monitoring,
        "vital_signs": vital_signs,
        "adverse_effects": adverse_effects,
        "red_flags": red_flags,
        "patient_risk_factors": patient_risk_factors,
        "pharmacist_actions": pharmacist_actions,
        "monitoring_schedule": monitoring_schedule,
        "evidence": dedup_evidence,
        "audit_id": audit_id,
    }
