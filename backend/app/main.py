from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import os

from .models import (
    AnalysisRequest, AnalysisResponse, DrugSummary,
    LabTrendRequest, LabTrendAssessment,
    DrugResolveRequest, DrugResolveResponse, DrugRefreshRequest,
)
from .engine import data_loader as dl
from .engine.orchestrator import run_analysis, UnknownDrugError, AmbiguousDrugError
from .engine.lab_trend_engine import analyze_lab_trend
from .engine import audit
from .agent import drug_agent

app = FastAPI(
    title="Drug Safety Monitoring AI Agent",
    description=(
        "Clinical decision-support API for pharmacist medication safety review. "
        "This is a decision-support tool, not a replacement for a physician/pharmacist "
        "or official prescribing information."
    ),
    version="0.1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DEMO_DRUG_IDS = [
    "warfarin", "amiodarone", "digoxin", "metformin", "vancomycin",
    "lithium", "methotrexate", "carbamazepine", "phenytoin", "apixaban",
]

DEMO_PATIENT = {
    "age": 78,
    "sex": "female",
    "weight_kg": 62,
    "pregnant": False,
    "egfr": 42,
    "hepatic_impairment": "none",
    "diagnoses": ["atrial fibrillation", "chronic kidney disease", "hypertension"],
    "allergies": ["penicillin"],
    "current_medications": ["lisinopril", "furosemide", "levothyroxine"],
    "lab_values": {"potassium": 3.3, "creatinine": 1.6},
}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/drugs", response_model=list[DrugSummary])
def search_drugs(
    q: str = Query("", description="Search text for generic/brand name autocomplete"),
    limit: int = Query(10, ge=1, le=200, description="Max results (autocomplete uses the default; library-count views may ask for more)"),
):
    return dl.search_drugs(q, limit=limit)


@app.get("/api/drugs/{drug_id}")
def get_drug_detail(drug_id: str):
    drug = dl.get_drug(drug_id.lower())
    if not drug:
        raise HTTPException(status_code=404, detail=f"Unknown drug id '{drug_id}'")
    return drug


@app.post("/api/drugs/resolve", response_model=DrugResolveResponse)
def resolve_drug(request: DrugResolveRequest):
    """Name resolution only — no safety analysis. Lets the frontend show
    'found locally' / 'needs AI lookup' / 'which one did you mean?' /
    'not found' before committing to a full /api/analyze call (spec
    section 14). Never raises: every outcome is a 200 with a status field,
    since 'ambiguous' and 'unknown' are expected, ordinary results here,
    not errors."""
    drug_id = dl.resolve_drug_id(request.name)
    if drug_id:
        return DrugResolveResponse(status="found", drug_id=drug_id, drug=dl.get_drug(drug_id), source="database")
    try:
        drug_id = drug_agent.resolve_and_ensure(request.name)
    except AmbiguousDrugError as e:
        return DrugResolveResponse(status="ambiguous", possible_matches=e.possible_matches)
    except UnknownDrugError as e:
        return DrugResolveResponse(
            status="unknown",
            message={
                "ai_unavailable": "AI-assisted retrieval is not configured, so this name could not be looked up beyond the curated dataset.",
                "invalid_response": "The AI service returned data that failed validation, so nothing was added.",
            }.get(e.reason, "Drug could not be confidently identified."),
        )
    return DrugResolveResponse(status="found", drug_id=drug_id, drug=dl.get_drug(drug_id), source="ai_retrieval")


@app.post("/api/drugs/refresh")
def refresh_drug(request: DrugRefreshRequest):
    """Force re-retrieval of an AI-sourced drug, bypassing the cache
    (spec section 14). Only meaningful for AI-retrieved records — the
    curated dataset isn't something this endpoint touches."""
    try:
        drug_id = drug_agent.refresh(request.drug_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (UnknownDrugError, AmbiguousDrugError):
        raise HTTPException(status_code=422, detail=f"'{request.drug_id}' could not be re-retrieved.")
    return {"status": "refreshed", "drug_id": drug_id, "drug": dl.get_drug(drug_id)}


@app.get("/api/demo")
def get_demo_config():
    return {
        "demo_drugs": [dl.get_drug(d) and {
            "id": d, "generic_name": dl.get_drug(d)["generic_name"],
        } for d in DEMO_DRUG_IDS],
        "demo_patient": DEMO_PATIENT,
        "label": "Illustrative / Demo Data — not a real patient",
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    if not request.drugs:
        raise HTTPException(status_code=400, detail="At least one medication is required.")
    if len(request.drugs) > 15:
        raise HTTPException(status_code=400, detail="Too many medications in a single request (limit 15).")

    patient_dict = request.patient.model_dump() if request.patient else None
    try:
        result = run_analysis(request.drugs, patient_dict, demo_mode=request.demo_mode)
    except AmbiguousDrugError as e:
        options = ", ".join(m["generic_name"] for m in e.possible_matches) or "multiple medications"
        raise HTTPException(
            status_code=422,
            detail=f"'{e.name}' could match more than one medication ({options}). "
                   f"Use POST /api/drugs/resolve first to disambiguate, then retry with the specific name.",
        )
    except UnknownDrugError as e:
        if e.reason == "ai_unavailable":
            message = (
                f"'{e.name}' is not in the curated dataset, and AI-assisted retrieval is not "
                f"configured (set AI_PROVIDER / AI_API_KEY / AI_MODEL) — so it could not be looked up."
            )
        elif e.reason == "invalid_response":
            message = f"'{e.name}' could not be retrieved: the AI service returned data that failed validation."
        else:
            message = f"'{e.name}' could not be confidently identified as a real medication."
        raise HTTPException(status_code=422, detail=message)
    return result


@app.post("/api/lab-trend", response_model=LabTrendAssessment)
def lab_trend(request: LabTrendRequest):
    if len(request.points) < 1:
        raise HTTPException(status_code=400, detail="At least one lab value point is required.")
    points = [p.model_dump() for p in request.points]
    return analyze_lab_trend(request.parameter, points)


@app.get("/api/audit")
def get_audit_log(limit: int = 20):
    """Demo-only endpoint to inspect the audit trail. In production this
    would require authentication/authorization."""
    return audit.read_recent(limit)
