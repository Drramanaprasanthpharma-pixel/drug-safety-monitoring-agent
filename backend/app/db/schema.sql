-- =============================================================================
-- Drug Safety Monitoring AI Agent — reference database schema
--
-- The demo prototype in this repository reads from the curated JSON files in
-- backend/app/data/ and does not require a database to run. This schema is
-- provided as the reference design for a production deployment backed by a
-- licensed drug/interaction database (e.g., First Databank, Multum, Micromedex)
-- and persistent audit storage.
--
-- Notes on patient data (spec section 22):
--   - No table here stores directly identifying patient information
--     (name, MRN, DOB). If you integrate with an EHR, store only a
--     pseudonymous patient_ref and keep the identity mapping in the EHR
--     system of record, not in this database.
--   - All patient-context columns are nullable — a drug-only analysis
--     must not require a patient row at all.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Drug data model
-- ---------------------------------------------------------------------------
CREATE TABLE drugs (
    drug_id             TEXT PRIMARY KEY,          -- canonical id, e.g. 'warfarin'
    generic_name        TEXT NOT NULL,
    drug_class          TEXT NOT NULL,
    pharmacology        TEXT,
    boxed_warning       TEXT,
    renal_dosing        TEXT,
    hepatic_dosing      TEXT,
    source              TEXT NOT NULL,             -- e.g. 'FDA label', 'RxNorm'
    source_last_synced  TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE drug_brand_names (
    id          BIGSERIAL PRIMARY KEY,
    drug_id     TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    brand_name  TEXT NOT NULL,
    UNIQUE (drug_id, brand_name)
);

CREATE TABLE drug_contraindications (
    id              BIGSERIAL PRIMARY KEY,
    drug_id         TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    contraindication TEXT NOT NULL
);

CREATE TABLE drug_adverse_effects (
    id        BIGSERIAL PRIMARY KEY,
    drug_id   TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    severity  TEXT NOT NULL CHECK (severity IN ('common', 'serious', 'life_threatening')),
    effect    TEXT NOT NULL
);

CREATE TABLE drug_organ_toxicity (
    id                      BIGSERIAL PRIMARY KEY,
    drug_id                 TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    organ                   TEXT NOT NULL,
    risk_level              TEXT NOT NULL CHECK (risk_level IN ('Low', 'Moderate', 'High', 'Critical')),
    reason                  TEXT NOT NULL,
    toxicity                TEXT NOT NULL,
    monitoring_frequency    TEXT NOT NULL,
    intervention_threshold  TEXT,
    evidence_source         TEXT NOT NULL,
    evidence_confidence     TEXT NOT NULL CHECK (evidence_confidence IN ('High', 'Moderate', 'Limited', 'Unknown'))
);

CREATE TABLE drug_organ_toxicity_monitoring_params (
    id                  BIGSERIAL PRIMARY KEY,
    organ_toxicity_id   BIGINT NOT NULL REFERENCES drug_organ_toxicity(id) ON DELETE CASCADE,
    parameter           TEXT NOT NULL
);

CREATE TABLE drug_monitoring_parameters (
    id              BIGSERIAL PRIMARY KEY,
    drug_id         TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    parameter       TEXT NOT NULL,
    why             TEXT NOT NULL,
    baseline        TEXT NOT NULL,
    follow_up       TEXT NOT NULL,
    alert_threshold TEXT NOT NULL,
    risk            TEXT NOT NULL CHECK (risk IN ('Low', 'Moderate', 'High', 'Critical'))
);

CREATE TABLE drug_vital_signs (
    id       BIGSERIAL PRIMARY KEY,
    drug_id  TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    parameter TEXT NOT NULL,
    why      TEXT NOT NULL
);

CREATE TABLE drug_high_risk_populations (
    id       BIGSERIAL PRIMARY KEY,
    drug_id  TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    population TEXT NOT NULL
);

CREATE TABLE drug_evidence (
    id          BIGSERIAL PRIMARY KEY,
    drug_id     TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    source      TEXT NOT NULL,
    reference   TEXT,
    evidence_date TEXT,
    confidence  TEXT NOT NULL CHECK (confidence IN ('High', 'Moderate', 'Limited', 'Unknown'))
);

-- ---------------------------------------------------------------------------
-- Interaction data model
-- ---------------------------------------------------------------------------
CREATE TABLE drug_interactions (
    id                  BIGSERIAL PRIMARY KEY,
    drug_a_id           TEXT NOT NULL REFERENCES drugs(drug_id),
    drug_b_id           TEXT NOT NULL REFERENCES drugs(drug_id),
    severity            TEXT NOT NULL CHECK (severity IN ('Contraindicated', 'Major', 'Moderate', 'Minor', 'Unknown')),
    mechanism           TEXT[] NOT NULL,
    mechanism_detail    TEXT NOT NULL,
    clinical_consequence TEXT NOT NULL,
    recommended_action  TEXT NOT NULL CHECK (recommended_action IN
        ('Avoid combination', 'Dose adjustment', 'Monitor', 'Separate administration', 'Continue with caution')),
    action_detail       TEXT NOT NULL,
    evidence_source     TEXT NOT NULL,
    evidence_confidence TEXT NOT NULL CHECK (evidence_confidence IN ('High', 'Moderate', 'Limited', 'Unknown')),
    CONSTRAINT unordered_pair UNIQUE (drug_a_id, drug_b_id),
    CONSTRAINT no_self_interaction CHECK (drug_a_id <> drug_b_id)
);
CREATE INDEX idx_interactions_drug_a ON drug_interactions(drug_a_id);
CREATE INDEX idx_interactions_drug_b ON drug_interactions(drug_b_id);

CREATE TABLE drug_disease_interactions (
    id              BIGSERIAL PRIMARY KEY,
    drug_id         TEXT NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    disease_keyword TEXT NOT NULL,
    risk            TEXT NOT NULL,
    recommendation  TEXT NOT NULL,
    evidence_confidence TEXT NOT NULL CHECK (evidence_confidence IN ('High', 'Moderate', 'Limited', 'Unknown'))
);

-- ---------------------------------------------------------------------------
-- Analysis + audit trail (no identifying patient data)
-- ---------------------------------------------------------------------------
CREATE TABLE analyses (
    audit_id                UUID PRIMARY KEY,
    requested_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    drugs_analyzed           TEXT[] NOT NULL,
    patient_context_provided BOOLEAN NOT NULL DEFAULT FALSE,
    patient_ref              TEXT,           -- optional pseudonymous reference only; never a name/MRN/DOB
    demo_mode                BOOLEAN NOT NULL DEFAULT FALSE,
    overall_risk_category    TEXT,
    overall_risk_score       SMALLINT,
    evidence_sources_cited   TEXT[]
);
CREATE INDEX idx_analyses_requested_at ON analyses(requested_at);

CREATE TABLE analysis_red_flags (
    id          BIGSERIAL PRIMARY KEY,
    audit_id    UUID NOT NULL REFERENCES analyses(audit_id) ON DELETE CASCADE,
    trigger_text TEXT NOT NULL,
    consequence TEXT NOT NULL,
    escalation  TEXT NOT NULL
);

CREATE TABLE analysis_pharmacist_actions (
    id          BIGSERIAL PRIMARY KEY,
    audit_id    UUID NOT NULL REFERENCES analyses(audit_id) ON DELETE CASCADE,
    action      TEXT NOT NULL,
    rationale   TEXT NOT NULL,
    completed   BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    completed_by_ref TEXT   -- pseudonymous pharmacist/user reference
);

-- ---------------------------------------------------------------------------
-- AI-assisted drug retrieval (backend/app/agent/) — optional persistent cache
--
-- Used only if DATABASE_URL is set (see backend/.env.example); otherwise the
-- app caches the same data in a local JSON file (backend/app/agent/cache.py).
-- Never a source of clinical truth by itself: drug_json.— meta.verified is
-- always false for a row here, since it came from AI retrieval rather than
-- a licensed database or a curated/human-reviewed monograph.
-- ---------------------------------------------------------------------------
CREATE TABLE drug_search_cache (
    drug_id         TEXT PRIMARY KEY,          -- canonical id, e.g. 'atorvastatin'
    input_aliases   TEXT[] NOT NULL DEFAULT '{}',  -- every name (typo'd, brand, etc.) that resolved here
    drug_json       JSONB NOT NULL,            -- full record in the same shape as the drugs table above
    source          TEXT NOT NULL DEFAULT 'ai_retrieval',
    cached_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_drug_search_cache_aliases ON drug_search_cache USING GIN (input_aliases);

-- Name-only alias/brand table backing offline normalization
-- (backend/app/agent/normalizer.py, seeded from backend/app/data/common_aliases.json).
-- Kept separate from drug_brand_names above because entries here may exist
-- before any full clinical record does — normalization can recognize
-- "Lipitor" -> "atorvastatin" long before atorvastatin has been retrieved.
CREATE TABLE drug_aliases (
    id          BIGSERIAL PRIMARY KEY,
    drug_id     TEXT NOT NULL,   -- not a foreign key: may reference a drug not yet in `drugs`
    alias       TEXT NOT NULL,
    alias_type  TEXT NOT NULL CHECK (alias_type IN ('generic', 'brand', 'class_member')),
    UNIQUE (drug_id, alias)
);
CREATE INDEX idx_drug_aliases_alias ON drug_aliases(lower(alias));
