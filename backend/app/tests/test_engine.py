import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.engine import data_loader as dl
from app.engine.orchestrator import run_analysis, UnknownDrugError
from app.engine.lab_trend_engine import analyze_lab_trend

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_drug_search_generic_and_brand():
    r = client.get("/api/drugs", params={"q": "coumadin"})
    assert r.status_code == 200
    ids = [d["id"] for d in r.json()]
    assert "warfarin" in ids


def test_resolve_drug_id_case_insensitive():
    assert dl.resolve_drug_id("WARFARIN") == "warfarin"
    assert dl.resolve_drug_id("Pacerone") == "amiodarone"
    assert dl.resolve_drug_id("not-a-real-drug") is None


def test_unknown_drug_raises():
    with pytest.raises(UnknownDrugError):
        run_analysis(["totally-fake-drug-xyz"], patient=None)


def test_single_drug_analysis_has_no_interactions():
    result = run_analysis(["warfarin"], patient=None)
    assert result["interactions"] == []
    assert result["overall_risk"]["is_validated_score"] is False
    assert "Hematologic" in [o["organ"] for o in result["priority_organs"]]


def test_warfarin_amiodarone_major_interaction_detected():
    result = run_analysis(["warfarin", "amiodarone"], patient=None)
    severities = [i["severity"] for i in result["interactions"]]
    assert "Major" in severities


def test_warfarin_apixaban_contraindicated():
    result = run_analysis(["warfarin", "apixaban"], patient=None)
    assert any(i["severity"] == "Contraindicated" for i in result["interactions"])
    # A contraindicated interaction should always surface as a red flag.
    assert len(result["red_flags"]) > 0


def test_renal_impairment_boosts_kidney_priority_for_renally_cleared_drug():
    patient = {"egfr": 20, "diagnoses": [], "allergies": [], "current_medications": [], "lab_values": {}}
    result = run_analysis(["digoxin"], patient=patient)
    renal = next((o for o in result["priority_organs"] if o["organ"] == "Renal"), None)
    assert renal is not None
    assert renal["relative_priority_percent"] >= 65  # boosted by severe renal impairment


def test_disease_interaction_metformin_ckd():
    patient = {"diagnoses": ["chronic kidney disease"], "allergies": [], "current_medications": [], "lab_values": {}}
    result = run_analysis(["metformin"], patient=patient)
    assert any(d["drug"] == "Metformin" for d in result["disease_interactions"])


def test_percent_fields_are_capped_0_100():
    result = run_analysis(["warfarin", "amiodarone", "digoxin"], patient={
        "egfr": 15, "hepatic_impairment": "severe", "diagnoses": [], "allergies": [],
        "current_medications": [], "lab_values": {"potassium": 2.9},
    })
    for organ in result["priority_organs"]:
        assert 0 <= organ["relative_priority_percent"] <= 100
    assert 0 <= result["overall_risk"]["priority_score"] <= 100


def test_analyze_endpoint_full_response_shape():
    r = client.post("/api/analyze", json={"drugs": ["warfarin", "amiodarone"], "demo_mode": True})
    assert r.status_code == 200
    body = r.json()
    for key in ["overall_risk", "dashboard", "priority_organs", "interactions", "monitoring",
                "red_flags", "pharmacist_actions", "evidence", "audit_id", "disclaimer"]:
        assert key in body


def test_analyze_endpoint_unknown_drug_returns_422():
    r = client.post("/api/analyze", json={"drugs": ["not-a-real-drug"]})
    assert r.status_code == 422


def test_analyze_endpoint_requires_at_least_one_drug():
    r = client.post("/api/analyze", json={"drugs": []})
    assert r.status_code in (400, 422)


def test_lab_trend_increasing_creatinine_flagged():
    result = analyze_lab_trend("creatinine", [
        {"day": 0, "value": 0.9}, {"day": 7, "value": 1.1},
        {"day": 14, "value": 1.4}, {"day": 21, "value": 1.8},
    ])
    assert result["trend"] == "Increasing"
    assert result["clinically_significant_change"] is True
    assert "clinical correlation required" in result["note"]


def test_lab_trend_stable_not_flagged():
    result = analyze_lab_trend("sodium", [{"day": 0, "value": 140}, {"day": 7, "value": 139}])
    assert result["trend"] == "Stable"
    assert result["clinically_significant_change"] is False


def test_lab_trend_insufficient_data():
    result = analyze_lab_trend("creatinine", [{"day": 0, "value": 1.0}])
    assert result["trend"] == "Insufficient data"
