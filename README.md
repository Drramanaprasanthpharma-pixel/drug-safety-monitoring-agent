# Drug Safety Monitoring AI Agent

A clinical decision-support dashboard for pharmacist medication safety review. A
pharmacist enters one or more medications (and, optionally, patient context) and
receives a structured safety assessment: organ toxicity prioritization,
drug–drug and drug–disease interactions, monitoring parameters, red flags,
adverse effects, and recommended pharmacist actions — each with an evidence
source and confidence label.

> **This is a clinical decision-support tool, not a replacement for a
> physician/pharmacist or official prescribing information.** Every
> clinically important recommendation displays its evidence source and
> distinguishes established information from AI-generated interpretation.

## What this is — and isn't

This repository is a **working prototype**, not a production clinical system:

- It ships with a **curated dataset of 16 medications** (warfarin,
  amiodarone, digoxin, metformin, vancomycin, lithium, methotrexate,
  carbamazepine, phenytoin, apixaban, atorvastatin, azithromycin,
  amoxicillin, ceftriaxone, amlodipine, rivaroxaban), built from
  established, well-known prescribing information.
- Beyond that curated core, medications are resolved through an **AI-assisted
  retrieval layer** (`backend/app/agent/`) — normalization (brand names,
  salt/combination forms, misspellings, drug-class ambiguity) plus, when an
  AI provider is configured, structured retrieval of a full clinical record
  for anything not already known. See "AI-assisted drug retrieval" below.
- **Neither is connected to a live FDA/EMA feed or a licensed drug database**
  (DrugBank, First Databank, Multum, Micromedex, etc.). AI-retrieved records
  are clearly labeled as such and their evidence confidence is capped
  accordingly (never "High") — they should be checked against current
  prescribing information before acting on them.
- **AI is an augmentation layer. Deterministic clinical safety engines
  remain the primary safety layer.** All interaction severities, organ
  toxicity risk levels, monitoring schedules, red flags, and the risk score
  come from `engine/` reading whichever record (curated or AI-retrieved) was
  resolved — the AI is never asked for, and cannot override, any of those
  judgments. Risk scores and percentages are explicitly labeled as
  *AI-assisted prioritization* (a scoring heuristic, not a language model),
  not validated clinical probabilities.
- To use this for real patients, you would need to replace
  `backend/app/data/*.json` with a licensed, regularly-updated drug and
  interaction database (see `backend/app/db/schema.sql` for the reference
  relational schema that models that data, including the AI-retrieval cache
  tables) — at that point the AI-retrieval layer becomes a fallback for
  whatever the licensed database doesn't cover, rather than the primary path.

## Architecture

```
User Input ("Lipitor", "atorvastatin", "rosuvastatin", ...)
   ↓
Drug search / AI agent     (agent/drug_agent.py — orchestrates the two steps below)
   ↓
Drug normalization         (agent/normalizer.py — offline: curated names, data/common_aliases.json
                             brand/salt/combination aliases, spelling variations, drug-class
                             ambiguity ["insulin" -> which insulin?] — no network call)
   ↓
Drug knowledge retrieval   (agent/drug_agent.py via agent/ai_client.py + agent/prompts.py —
                             only when the name above is a known identity with no clinical
                             record yet; skipped entirely if already curated or cached)
   ↓
Validation                 (agent/schemas.py — Pydantic; invalid/unparseable AI output is
                             retried once, then rejected — never passed on)
   ↓
Cache                      (agent/cache.py — file-backed by default, or Postgres via
                             DATABASE_URL — so the same drug is never re-fetched)
   ↓
Existing deterministic safety engines (unchanged, and unaware this drug came from AI):
   engine/interactions_engine.py, disease_interactions_engine.py, monitoring_engine.py,
   patient_risk_engine.py, red_flag_engine.py, organ_priority_engine.py,
   pharmacist_actions_engine.py, scoring_engine.py — orchestrated by engine/orchestrator.py
   ↓
Risk prioritization        (0–100 relative score, explicitly non-validated)
   ↓
Dashboard                  (React/TypeScript frontend — AI-retrieved evidence is rendered
                             through the same generic evidence list, just labeled and capped
                             differently; see "AI transparency" below)
```

**Why the deterministic engines never change:** the spec requires that the
rules engine "take precedence over free-form AI output for critical safety
alerts" and that the system "never fabricate drug information." The AI layer
is used only for *retrieval* (normalization + structured drug facts) — it
converts a name into a record shaped exactly like a curated `drugs.json`
entry, then hands off to the same engine code that already existed. No
engine module was changed to accommodate AI-retrieved drugs; they are
indistinguishable to the engines from a curated drug once validated. The one
place this is *not* fully symmetric: interaction/disease-interaction rules
are still keyed to the original 16 curated drugs, so an AI-retrieved drug
will correctly show **no interactions** until a curated rule exists for that
pair — the engine does not guess, matching spec section 9 ("must not invent
an interaction merely because two drug names were supplied").

### AI-assisted drug retrieval

Configured entirely through environment variables (see `.env.example`) —
nothing here is required for the app to run:

| Variable | Purpose |
|---|---|
| `AI_PROVIDER` | `anthropic` or `openai`. Unset (or any other value) = AI retrieval disabled. |
| `AI_API_KEY` | API key for that provider. Never sent to the frontend — all calls are server-side (`agent/ai_client.py`). |
| `AI_MODEL` | Optional; a current default model is used per provider if unset. |
| `DATABASE_URL` | Optional. If set, the retrieval cache lives in Postgres (`drug_search_cache` / `drug_aliases` tables in `db/schema.sql`) instead of a local JSON file. Requires `pip install "psycopg[binary]"` (not installed by default — kept out of `requirements.txt` so the demo has zero extra runtime deps). |

**Pipeline for a name not in the curated dataset**, e.g. `POST /api/analyze
{"drugs": ["Lipitor"]}` or `{"drugs": ["Rosuvastatin"]}`:

1. `agent/normalizer.py` checks, in order and entirely offline: the curated
   dataset, `data/common_aliases.json` (brand names, salt/combination forms,
   known misspellings for medications like Lipitor, Crestor, Zosyn/Piptaz,
   Augmentin, Tylenol, etc.), fuzzy spelling matching, and whether the name
   is an ambiguous drug-class reference (e.g. "insulin", "penicillin" — several
   distinct products exist, so the caller is asked to pick one rather than
   have the system guess).
2. If that resolves to a **known identity with no clinical record yet**
   (e.g. "Lipitor" → atorvastatin is already curated, so this step is
   skipped entirely for it; "Rosuvastatin" is in the alias table but has no
   curated record, so this step runs for it) — or the name isn't recognized
   locally at all — `agent/drug_agent.py` asks the configured AI provider for
   a structured record, using a JSON schema built from `agent/schemas.py`'s
   `AIDrugRecord` model.
3. The response is validated against that schema. An invalid or unparseable
   response is retried once with the validation error fed back; if it still
   fails, or no provider is configured, or the provider call itself fails,
   the request fails with a clear, distinguishable reason (`ai_unavailable`
   vs. `invalid_response` vs. "not a real drug") — it never falls through to
   a partially-populated or fabricated record (spec sections 7, 18).
4. A valid record is cached (`agent/cache.py`) keyed by its canonical id, so
   the AI is called at most once per medication, and registered so
   `engine/data_loader.py`'s existing `get_drug` / `resolve_drug_id` /
   `search_drugs` see it exactly like a curated entry — no engine code knows
   or cares where a record came from.

**AI transparency:** every AI-retrieved record's evidence entries are
labeled `"AI-assisted retrieval — ..."` and their confidence is capped at
`"Moderate"` server-side (never trusting the model's own confidence claim,
and never `"High"`, which is reserved for the curated dataset) — this
happens in `agent/drug_agent.py::_to_internal_record`, not in the prompt, so
it can't be prompted around. The frontend's evidence list renders this with
no special-casing, since it already renders `source`/`confidence`
generically for every drug.

**Endpoints:**

| Endpoint | Purpose |
|---|---|
| `GET /api/drugs?q=...` | Autocomplete — searches curated + already-cached drugs only (no AI call per keystroke). |
| `GET /api/drugs/{id}` | Fetch a specific record by canonical id — also curated + cache only, no AI call as a side effect of a GET. |
| `POST /api/drugs/resolve {"name": "..."}` | Normalizes and, if needed, retrieves-and-caches a drug by free-text name. Returns `status: found \| ambiguous \| unknown` with a `source` of `database` or `ai_retrieval`. |
| `POST /api/drugs/refresh {"drug_id": "..."}` | Forces a fresh AI retrieval for an *already AI-cached* drug, overwriting its cache entry. 400 if the id is curated or was never AI-retrieved. |
| `POST /api/analyze {"drugs": [...]}` | Unchanged shape; now resolves each name through the pipeline above before running the safety engines. Ambiguous/unknown names return 422 with a specific, actionable message (e.g. pointing at `/api/drugs/resolve`) rather than a generic error. |

**Providers implemented:** Anthropic and OpenAI, using only the Python
standard library (`urllib`) — no new runtime dependency. Gemini is not
implemented (selecting it raises a clear error rather than silently no-op'ing).

## Project layout

```
vercel.json                 Vercel Services config — routes /api/* to the backend,
                             everything else to the frontend, on one domain
backend/
  app/
    main.py                 FastAPI app + endpoints
    models.py                Pydantic request/response schemas (the JSON contract)
    data/                    Curated dataset (drugs, interactions, disease rules) +
                             common_aliases.json (brand/salt/misspelling seed for the
                             normalizer) + ai_drug_cache.json (file-backed AI cache,
                             gitignored, created at runtime; unused if DATABASE_URL is set)
    engine/                  Deterministic rules engine (one module per concern) —
                             data_loader.py transparently also sees AI-cached drugs
    agent/                   AI-assisted retrieval layer (see "AI-assisted drug
                             retrieval" above): drug_agent.py (orchestration),
                             normalizer.py (offline alias/fuzzy/ambiguity resolution),
                             ai_client.py (provider-agnostic HTTP calls), schemas.py
                             (Pydantic validation of AI output), prompts.py, cache.py
                             (file or Postgres), errors.py
      audit.py                Demo audit log — writes to /tmp on Vercel (read-only FS),
                               to backend/app/data/ locally
    db/schema.sql             Reference relational schema for a production deployment,
                             including drug_search_cache / drug_aliases for the AI cache
    tests/
      test_engine.py           Unit tests (engine logic + API endpoints)
      test_agent.py            Unit tests for the AI agent layer — normalizer, cache,
                               drug_agent resolve/refresh, and the new endpoints, all
                               using an in-process fake AI client (no network calls)
  requirements.txt           Runtime deps only — this is what Vercel deploys
  requirements-dev.txt       + local dev/test deps (uvicorn, pytest, httpx)
  .python-version            Pins the Python runtime version on Vercel
  .env.example
frontend/
  src/
    App.tsx                  Route table (hash routing) inside the app shell
    pages/                   One file per screen: Overview, Review, Drug library,
                             Drug profile, Lab trends, Activity log, About
    components/              AppShell (sidebar, top bar, search, alerts), review
                             results sections, risk readout, organ bars, pipeline
                             record, shared UI states (empty / loading / error)
    lib/                     store (session-only state), hooks, route, format, csv
    api.ts                    Backend API client — always calls relative `/api/...`
    types.ts                  TypeScript types mirroring the backend schemas
    index.css                 The design system (plain CSS, no CSS framework)
  vite.config.ts             Dev-only proxy: forwards /api → localhost:8000
  package.json
```

## Running it locally

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Verify it's up: `curl http://localhost:8000/api/health` → `{"status":"ok"}`

Interactive API docs: `http://localhost:8000/docs`

Run the test suite:

```bash
python3 -m pytest app/tests/ -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api/*` to
`http://localhost:8000` (configured in `vite.config.ts`), so both servers
need to be running.

Try it: click **Load demo patient** to populate two interacting demo drugs
(warfarin + amiodarone) and an illustrative patient, then **Analyze safety**.
Or search for any of the 16 curated drugs by generic or brand name — or, with
`AI_PROVIDER`/`AI_API_KEY` set, enter any other real medication (e.g.
Rosuvastatin, Pantoprazole, Zosyn, Augmentin, Losartan, Tylenol) on the
Review page and it will be normalized and retrieved on the fly.

### Production build

```bash
cd frontend
npm run build      # outputs static assets to frontend/dist/
npm run preview    # serve the production build locally to sanity-check it
```

Serve `frontend/dist/` from any static host (or from FastAPI itself via
`StaticFiles`) and set `CORS_ALLOWED_ORIGINS` in the backend's `.env` to that
origin.

## Deploying to Vercel

This repo deploys as **one Vercel project** using [Vercel
Services](https://vercel.com/docs/services): the React/TypeScript frontend
and the FastAPI backend build independently and are served from the same
domain, so the frontend's `/api/...` calls stay same-origin in production —
no CORS, no hardcoded backend URL.

### How it's wired

`vercel.json` (repo root) defines two services and two rewrites:

```json
{
  "services": {
    "frontend": { "root": "frontend/", "framework": "vite" },
    "backend": { "root": "backend/", "entrypoint": "app.main:app" }
  },
  "rewrites": [
    { "source": "/api/(.*)", "destination": { "service": "backend" } },
    { "source": "/(.*)", "destination": { "service": "frontend" } }
  ]
}
```

- Requests to `/api/*` (matching the app's existing `@app.get("/api/...")`
  routes) go to the FastAPI service.
- Everything else goes to the built Vite static site.
- Each service builds like a standalone Vercel project from its own `root`:
  the frontend via its `package.json`/`vite.config.ts`, the backend via
  `requirements.txt` + the `app.main:app` entrypoint
  (`backend/app/main.py`, top-level `app = FastAPI()`).

### Exact Vercel project settings

Import the repo at [vercel.com/new](https://vercel.com/new) and deploy with:

| Setting | Value |
|---|---|
| Root Directory | **leave blank / repo root** (do not point it at `backend/` or `frontend/` — `vercel.json` itself defines both service roots) |
| Framework Preset | Other / ignored — `vercel.json`'s `services` block takes over |
| Build Command | leave default (blank) — do not set one at the project level; `services` mode requires build settings to live per-service, and both services here build with zero extra config |
| Install Command | leave default (blank), same reason |
| Output Directory | leave default (blank), same reason |
| Node.js Version | 20.x (or your team default) — used for the frontend service |
| Python Version | 3.12 — pinned via `backend/.python-version` |

If this project previously deployed the old Streamlit prototype, also check
**Project Settings → General** for a leftover custom Build/Install/Output
Directory from that setup and clear it back to blank — those legacy
single-framework overrides can conflict with `services` mode.

### Required environment variables

None are required for the demo to work — `CORS_ALLOWED_ORIGINS` has a
built-in localhost default and isn't consulted in production, since the
frontend and backend share one origin through the rewrites above.

Optional, if you extend the project later (all set in **Project Settings →
Environment Variables**, never hardcoded, never given a `VITE_` prefix since
that would ship them to the browser):

| Variable | Used for |
|---|---|
| `CORS_ALLOWED_ORIGINS` | Only needed if you ever split the backend out to its own domain/project instead of using Services — comma-separated allowed origins |
| `AI_PROVIDER` / `AI_API_KEY` / `AI_MODEL` | Enables AI-assisted retrieval for medications outside the curated dataset — see "AI-assisted drug retrieval" above. Optional; the app works fully offline (curated dataset only) without these |
| `DATABASE_URL` | Optional — moves the AI-retrieval cache from a local file to Postgres. On Vercel's serverless filesystem the file cache lives in `/tmp` and does **not** persist across cold starts, so set this for any real deployment that uses AI retrieval, or every cold start re-fetches previously-seen drugs |
| `DRUG_DB_PROVIDER` / `DRUG_DB_API_KEY` | Reserved for connecting a licensed drug database |

### Local dev vs. production API URLs

- **Dev**: `frontend/src/api.ts` calls relative `/api/...`; `vite.config.ts`
  proxies `/api` to `http://localhost:8000` so `npm run dev` + a locally
  running backend just works.
- **Production (Vercel)**: the same relative `/api/...` calls are resolved
  by the `services` rewrite above, on the same domain — no localhost, no
  separate backend URL, nothing to configure.
- Run everything together locally the same way Vercel runs it in production
  with `vercel dev` (requires the [Vercel
  CLI](https://vercel.com/docs/cli), `npm i -g vercel`).

### Other deployment notes

- **Data**: swap `backend/app/data/*.json` for real queries against a
  licensed drug/interaction database using the schema in
  `backend/app/db/schema.sql` as the target shape. Keep the engine modules'
  function signatures the same and only the `data_loader` module needs to
  change.
- **Auth**: this prototype has no authentication. Add it (OAuth2/OIDC via
  FastAPI's security utilities, or your institution's SSO) before deploying
  anywhere with real patient data, and put the `/api/audit` endpoint behind
  it specifically.
- **PHI**: the audit log (`engine/audit.py`) intentionally never stores
  identifying patient details — only which drugs were analyzed, whether
  patient context was supplied (boolean), and which evidence sources were
  cited. On Vercel it writes to `/tmp` (the only writable path in a
  serverless function), which is ephemeral per instance — treat `/api/audit`
  as a demo/debug view, not a durable log; wire a real database via the
  schema above before relying on it. If you connect this to an EHR, keep the
  same never-store-identifiers approach and store only a pseudonymous
  patient reference, never name/MRN/DOB, per the schema's `patient_ref`
  column.
- **Encryption**: Vercel terminates TLS automatically; if you add a real
  database per the schema above, enable encryption at rest per your
  platform's standard practice.

## Extending the demo dataset

Each drug in `backend/app/data/drugs.json` follows a consistent shape
(pharmacology, contraindications, adverse effects, organ toxicity, monitoring
parameters, dosing considerations, evidence). To add a new drug:

1. Add an entry to `drugs.json` following the existing structure.
2. Add any relevant pairs to `interactions.json` and
   `disease_interactions.json`.
3. Run `python3 -m json.tool backend/app/data/drugs.json > /dev/null` to
   confirm valid JSON, then `pytest` to confirm nothing broke.

The engine code needs no changes — it reads the dataset generically.

## Known limitations (read before treating this as more than a prototype)

- **Interactions and disease-interactions are only ever recognized for pairs
  explicitly listed in `interactions.json` / `disease_interactions.json`** —
  currently built around the 16 curated drugs. A medication resolved purely
  through AI-assisted retrieval will correctly show **no interactions**
  rather than a fabricated one; the system does not ask the AI to identify
  novel interactions (an "AI-assisted interaction note" for pairs with no
  curated rule was considered per the original spec but intentionally not
  built in this pass, to keep the interaction engine's output 100%
  deterministic — see "Files not changed / deferred" below).
- Only Anthropic and OpenAI are implemented as AI providers; selecting
  Gemini raises a clear error rather than silently doing nothing.
- AI-assisted retrieval calls the model once per unresolved medication (with
  one retry on an invalid response) and does not use live web search/RAG
  grounding — it relies on the model's own training data, which is why
  evidence confidence is always capped at "Moderate" and the record is
  explicitly labeled as unverified against a live regulatory feed.
- Organ-priority percentages and the overall risk score are a transparent,
  weighted heuristic (see `engine/scoring_engine.py` and
  `engine/organ_priority_engine.py`), not a validated clinical calculator
  (e.g., not HAS-BLED, not CHA₂DS₂-VASc) — this is unchanged by AI retrieval.
- Disease-interaction matching uses simple keyword matching against
  free-text diagnoses — it is a demo mechanism, not an ICD-10-aware clinical
  engine.
- The file-backed AI cache (`data/ai_drug_cache.json`) is per-instance and
  ephemeral on Vercel (`/tmp`); set `DATABASE_URL` for a real deployment.
- No authentication, rate limiting, or persistent database is included; see
  "Deployment notes" above.
