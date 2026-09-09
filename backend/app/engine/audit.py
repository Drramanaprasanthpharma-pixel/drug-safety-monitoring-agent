"""
Audit logging.

Per spec section 22 ("Avoid storing identifiable patient information
unnecessarily"), this logs only: a generated audit id, timestamp, which
drugs were analyzed, whether patient context was supplied (boolean only —
never the actual values), and which evidence sources were cited. This is
a demo-grade implementation (local JSONL file); a production deployment
should write to an encrypted, access-controlled audit store.
"""
from __future__ import annotations
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Vercel Functions have a read-only filesystem except for /tmp (which is
# writable but ephemeral per instance). Vercel sets the VERCEL env var
# automatically at runtime, so detect that and switch paths accordingly —
# this keeps the demo audit trail actually working on Vercel instead of
# silently no-op'ing on every write, while local dev keeps using the
# repo-local file as before.
if os.environ.get("VERCEL"):
    AUDIT_LOG_PATH = Path("/tmp") / "audit_log.jsonl"
else:
    AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "audit_log.jsonl"


def record_analysis(drug_ids: list[str], patient_provided: bool, evidence_sources: list[str], demo_mode: bool) -> str:
    audit_id = str(uuid.uuid4())
    entry = {
        "audit_id": audit_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "drugs_analyzed": drug_ids,
        "patient_context_provided": patient_provided,
        "demo_mode": demo_mode,
        "evidence_sources_cited": sorted(set(evidence_sources)),
    }
    try:
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # Audit logging must never block a safety analysis from returning
    return audit_id


def read_recent(limit: int = 20) -> list[dict]:
    if not AUDIT_LOG_PATH.exists():
        return []
    with open(AUDIT_LOG_PATH, "r") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(line) for line in lines]
