"""
Tests for the AI-assisted drug agent layer (spec section 19).

None of these tests make a real network call: the AI provider is always
either left unconfigured (to exercise the "AI unavailable" fallback, spec
section 18) or replaced with an in-process fake client that returns
canned JSON (to exercise validation, retry, ambiguous/unknown handling —
spec sections 7, 11 — without needing a real API key). Every test clears
the AI cache first so results from one test can't leak into another, and
restores AI_PROVIDER/AI_API_KEY afterwards so this file's tests can't
change how test_engine.py behaves if the suite runs in one process.
"""
import json

import pytest
from fastapi.testclient import TestClient

from app.agent import cache as ai_cache
from app.agent import drug_agent
from app.agent.errors import AmbiguousDrugError, UnknownDrugError
from app.agent.normalizer import normalize
from app.engine import data_loader as dl
from app.engine.orchestrator import run_analysis
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_state(monkeypatch):
    """Runs around every test in this file: clears the AI cache, ensures
    no real AI provider is configured unless a test opts in, and restores
    drug_agent.get_client afterwards so a fake client from one test can
    never leak into the next."""
    ai_cache.clear_all()
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    yield
    ai_cache.clear_all()


def _configure_ai(monkeypatch, fake_client):
    monkeypatch.setenv("AI_PROVIDER", "anthropic")
    monkeypatch.setenv("AI_API_KEY", "test-key-not-real")
    monkeypatch.setattr(drug_agent, "get_client", lambda: fake_client)


class FakeClient:
    """Returns each item of `responses` in order on successive calls to
    generate_json, regardless of which drug is being asked about — good
    enough for these tests, which only ever resolve one name per fake."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def configured(self):
        return True

    def generate_json(self, system, user):
        self.calls += 1
        if not self._responses:
            raise AssertionError("FakeClient called more times than it had scripted responses")
        return self._responses.pop(0)


def _found_envelope(generic_name: str, **overrides) -> str:
    drug = {
        "generic_name": generic_name,
        "brand_names": [],
        "drug_class": "Test class",
        "pharmacology": None,
        "boxed_warning": None,
        "contraindications": [],
        "adverse_effects": {"common": [], "serious": [], "life_threatening": []},
        "organ_toxicity": [],
        "monitoring_parameters": [],
        "vital_signs": [],
        "renal_dosing": None,
        "hepatic_dosing": None,
        "high_risk_populations": [],
        "therapeutic_drug_monitoring": {"applicable": False, "target_range": None, "notes": None},
        "evidence": [{"source": "Test label", "reference": None, "date": None, "confidence": "High"}],
    }
    drug.update(overrides)
    return json.dumps({
        "status": "found",
        "normalization": {"input_name": generic_name, "generic_name": generic_name, "confidence": 0.95},
        "possible_matches": [],
        "drug": drug,
    })


# --- normalizer: offline, no AI involved --------------------------------

def test_normalizer_resolves_curated_drug_directly():
    r = normalize("Warfarin")
    assert r.status == "resolved" and r.drug_id == "warfarin"


def test_normalizer_resolves_brand_name():
    r = normalize("Lipitor")
    assert r.status == "resolved" and r.drug_id == "atorvastatin"


def test_normalizer_resolves_spelling_variation():
    r = normalize("amoxicilin")
    assert r.status == "resolved" and r.drug_id == "amoxicillin"


def test_normalizer_flags_drug_class_as_ambiguous():
    r = normalize("insulin")
    assert r.status == "ambiguous"
    assert {m.generic_name for m in r.possible_matches} >= {"Insulin glargine", "Insulin lispro"}


def test_normalizer_unresolved_for_gibberish():
    r = normalize("xyznotarealdrug123")
    assert r.status == "unresolved"


# --- drug_agent.resolve_and_ensure: AI not configured --------------------

def test_unknown_gibberish_without_ai_configured():
    with pytest.raises(UnknownDrugError) as exc:
        drug_agent.resolve_and_ensure("totally-fake-drug-xyz")
    assert exc.value.reason == "ai_unavailable"


def test_known_identity_without_clinical_record_needs_ai():
    # "Rosuvastatin" is in the alias table (so its *identity* is known) but
    # has no curated clinical record — retrieving one requires AI.
    with pytest.raises(UnknownDrugError) as exc:
        drug_agent.resolve_and_ensure("Rosuvastatin")
    assert exc.value.reason == "ai_unavailable"


def test_class_name_is_ambiguous_even_without_ai():
    with pytest.raises(AmbiguousDrugError) as exc:
        drug_agent.resolve_and_ensure("insulin")
    assert len(exc.value.possible_matches) >= 2


# --- drug_agent.resolve_and_ensure: AI configured (fake client) ----------

def test_ai_retrieval_found_and_cached(monkeypatch):
    _configure_ai(monkeypatch, FakeClient([_found_envelope("Rosuvastatin", brand_names=["Crestor"])]))
    drug_id = drug_agent.resolve_and_ensure("Rosuvastatin")
    assert drug_id == "rosuvastatin"
    drug = dl.get_drug(drug_id)
    assert drug["generic_name"] == "Rosuvastatin"
    assert drug["evidence"][0]["confidence"] == "Moderate"  # capped down from "High"
    assert "AI-assisted retrieval" in drug["evidence"][0]["source"]


def test_ai_result_is_cached_and_not_refetched(monkeypatch):
    fake = FakeClient([_found_envelope("Rosuvastatin")])
    _configure_ai(monkeypatch, fake)
    drug_agent.resolve_and_ensure("Rosuvastatin")
    assert fake.calls == 1
    # Second lookup, even under a different spelling, must hit the cache —
    # if it called the AI again, the FakeClient would raise (no responses left).
    drug_id_again = drug_agent.resolve_and_ensure("rosuvastatin")
    assert drug_id_again == "rosuvastatin"
    assert fake.calls == 1


def test_ai_retries_once_on_invalid_json_then_succeeds(monkeypatch):
    fake = FakeClient(["not even json {{{", _found_envelope("Rosuvastatin")])
    _configure_ai(monkeypatch, fake)
    drug_id = drug_agent.resolve_and_ensure("Rosuvastatin")
    assert drug_id == "rosuvastatin"
    assert fake.calls == 2


def test_ai_invalid_response_after_retry_raises_unknown(monkeypatch):
    fake = FakeClient(["not json", "still not json"])
    _configure_ai(monkeypatch, fake)
    with pytest.raises(UnknownDrugError) as exc:
        drug_agent.resolve_and_ensure("Rosuvastatin")
    assert exc.value.reason == "invalid_response"
    assert fake.calls == 2


def test_ai_ambiguous_drug_status(monkeypatch):
    envelope = json.dumps({
        "status": "ambiguous_drug",
        "normalization": {"input_name": "some statin", "confidence": 0.3},
        "possible_matches": [
            {"generic_name": "Atorvastatin", "drug_class": "Statin"},
            {"generic_name": "Simvastatin", "drug_class": "Statin"},
        ],
        "drug": None,
    })
    _configure_ai(monkeypatch, FakeClient([envelope]))
    with pytest.raises(AmbiguousDrugError) as exc:
        drug_agent.resolve_and_ensure("a brand new totally novel statin name")
    assert {m["generic_name"] for m in exc.value.possible_matches} == {"Atorvastatin", "Simvastatin"}


def test_ai_unknown_drug_status(monkeypatch):
    envelope = json.dumps({
        "status": "unknown_drug",
        "normalization": {"input_name": "x", "confidence": 0.0},
        "possible_matches": [],
        "drug": None,
    })
    _configure_ai(monkeypatch, FakeClient([envelope]))
    with pytest.raises(UnknownDrugError) as exc:
        drug_agent.resolve_and_ensure("totally fake gibberish medication")
    assert exc.value.reason is None


def test_ai_result_matching_curated_drug_prefers_curated_record(monkeypatch):
    # If the AI (mis)identifies a name as a drug that's actually already
    # curated, the authoritative curated record wins (spec section 4).
    _configure_ai(monkeypatch, FakeClient([_found_envelope("Warfarin")]))
    drug_id = drug_agent.resolve_and_ensure("some odd way of saying warfarin")
    assert drug_id == "warfarin"


# --- drug_agent.refresh ---------------------------------------------------

def test_refresh_updates_an_existing_ai_cached_drug(monkeypatch):
    _configure_ai(monkeypatch, FakeClient([_found_envelope("Rosuvastatin", brand_names=["Crestor"])]))
    drug_agent.resolve_and_ensure("Rosuvastatin")

    _configure_ai(monkeypatch, FakeClient([_found_envelope("Rosuvastatin", brand_names=["Crestor", "Ezallor"])]))
    new_id = drug_agent.refresh("rosuvastatin")
    assert new_id == "rosuvastatin"
    assert dl.get_drug("rosuvastatin")["brand_names"] == ["Crestor", "Ezallor"]


def test_refresh_on_non_cached_drug_raises_value_error():
    with pytest.raises(ValueError):
        drug_agent.refresh("not-a-cached-drug")


# --- orchestrator integration ---------------------------------------------

def test_run_analysis_retrieves_and_analyzes_an_ai_sourced_drug(monkeypatch):
    _configure_ai(monkeypatch, FakeClient([_found_envelope(
        "Rosuvastatin",
        organ_toxicity=[{
            "organ": "Musculoskeletal", "risk_level": "Moderate", "reason": "Statin class effect",
            "toxicity": "Myopathy", "monitoring_parameters": ["CK if symptomatic"], "frequency": "As needed",
            "thresholds": "Muscle pain with weakness", "source": "Test",
        }],
    )]))
    result = run_analysis(["Rosuvastatin"], patient=None)
    assert result["drugs_analyzed"] == ["Rosuvastatin"]
    assert "Musculoskeletal" in [o["organ"] for o in result["priority_organs"]]


def test_run_analysis_raises_ambiguous_for_class_name():
    with pytest.raises(AmbiguousDrugError):
        run_analysis(["insulin"], patient=None)


# --- HTTP API --------------------------------------------------------------

def test_api_resolve_found_locally():
    r = client.post("/api/drugs/resolve", json={"name": "Lipitor"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "found"
    assert body["drug_id"] == "atorvastatin"
    assert body["source"] == "database"


def test_api_resolve_ambiguous():
    r = client.post("/api/drugs/resolve", json={"name": "insulin"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ambiguous"
    assert len(body["possible_matches"]) >= 2


def test_api_resolve_unknown_without_ai():
    r = client.post("/api/drugs/resolve", json={"name": "Rosuvastatin"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "unknown"
    assert "AI-assisted retrieval" in body["message"]


def test_api_resolve_ai_retrieval(monkeypatch):
    _configure_ai(monkeypatch, FakeClient([_found_envelope("Rosuvastatin")]))
    r = client.post("/api/drugs/resolve", json={"name": "Rosuvastatin"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "found"
    assert body["source"] == "ai_retrieval"
    assert body["drug"]["generic_name"] == "Rosuvastatin"


def test_api_analyze_ambiguous_returns_422():
    r = client.post("/api/analyze", json={"drugs": ["insulin"]})
    assert r.status_code == 422
    assert "more than one medication" in r.json()["detail"]


def test_api_analyze_unknown_without_ai_returns_422():
    r = client.post("/api/analyze", json={"drugs": ["Rosuvastatin"]})
    assert r.status_code == 422
    assert "AI-assisted retrieval is not configured" in r.json()["detail"]


def test_api_analyze_with_ai_configured_succeeds(monkeypatch):
    _configure_ai(monkeypatch, FakeClient([_found_envelope("Rosuvastatin")]))
    r = client.post("/api/analyze", json={"drugs": ["Rosuvastatin"]})
    assert r.status_code == 200
    assert r.json()["drugs_analyzed"] == ["Rosuvastatin"]


def test_api_refresh_rejects_curated_drug():
    r = client.post("/api/drugs/refresh", json={"drug_id": "atorvastatin"})
    assert r.status_code == 400


def test_api_refresh_rejects_never_cached_id():
    r = client.post("/api/drugs/refresh", json={"drug_id": "not-a-real-cached-id"})
    assert r.status_code == 400


def test_api_refresh_succeeds_for_ai_cached_drug(monkeypatch):
    _configure_ai(monkeypatch, FakeClient([_found_envelope("Rosuvastatin", brand_names=["Crestor"])]))
    client.post("/api/drugs/resolve", json={"name": "Rosuvastatin"})

    _configure_ai(monkeypatch, FakeClient([_found_envelope("Rosuvastatin", brand_names=["Crestor", "Ezallor"])]))
    r = client.post("/api/drugs/refresh", json={"drug_id": "rosuvastatin"})
    assert r.status_code == 200
    assert r.json()["drug"]["brand_names"] == ["Crestor", "Ezallor"]


# --- cache.py: file-backed persistence (DATABASE_URL unset in this suite) -

def test_cache_round_trip_and_delete():
    ai_cache.save("cache-test-drug", {"id": "cache-test-drug", "generic_name": "Cache Test Drug"},
                  aliases=["Cache Test Drug", "ctd"], source="ai_retrieval")
    entry = ai_cache.get("cache-test-drug")
    assert entry is not None
    assert entry["drug"]["generic_name"] == "Cache Test Drug"
    assert "ctd" in entry["aliases"]

    ai_cache.add_alias("cache-test-drug", "another-name")
    assert "another-name" in ai_cache.get("cache-test-drug")["aliases"]

    ai_cache.delete("cache-test-drug")
    assert ai_cache.get("cache-test-drug") is None


def test_data_loader_sees_cached_drug_transparently():
    ai_cache.save("cache-test-drug-2", {
        "id": "cache-test-drug-2", "generic_name": "Cache Test Drug Two", "brand_names": ["CTD2"],
        "drug_class": "Test", "adverse_effects": {"common": [], "serious": [], "life_threatening": []},
    }, aliases=["cache test drug two"], source="ai_retrieval")

    assert dl.resolve_drug_id("cache test drug two") == "cache-test-drug-2"
    assert dl.get_drug("cache-test-drug-2")["generic_name"] == "Cache Test Drug Two"
    ids = [d["id"] for d in dl.search_drugs("Cache Test Drug Two")]
    assert "cache-test-drug-2" in ids
