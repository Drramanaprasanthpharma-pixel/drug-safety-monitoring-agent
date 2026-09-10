from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import os

from .models import (
    AnalysisRequest, AnalysisResponse, DrugSummary,
    LabTrendRequest, LabTrendAssessment,
)
from .engine import data_loader as dl
from .engine.orchestrator import run_analysis, UnknownDrugError
from .engine.lab_trend_engine import analyze_lab_trend
from .engine import audit

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
def search_drugs(q: str = Query("", description="Search text for generic/brand name autocomplete")):
    return dl.search_drugs(q)


@app.get("/api/drugs/{drug_id}")
def get_drug_detail(drug_id: str):
    drug = dl.get_drug(drug_id.lower())
    if not drug:
        raise HTTPException(status_code=404, detail=f"Unknown drug id '{drug_id}'")
    return drug


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
    except UnknownDrugError as e:
        raise HTTPException(
            status_code=422,
            detail=f"{e.name} is not in the current demo drug database. "
                   f"This prototype only recognizes the demo drug list; a production "
                   f"deployment would connect to a licensed drug database.",
        )
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
