# Drug Safety & Monitoring AI Agent

A research prototype for structured drug-safety monitoring analysis in a browser-based Streamlit interface.

## ⚠️ Clinical Disclaimer

This project is a clinical pharmacy decision-support research prototype and is not a replacement for a pharmacist or physician.

- It does not use patient-identifiable information.
- It does not provide patient-specific treatment decisions.
- It does not provide dosing recommendations unless explicitly added in a future development phase.
- It is intended for research and educational use only.
- All output must be verified against current authoritative references before clinical use.

## What currently works

The current application supports a demonstration-only workflow for the following drugs:

- Vancomycin
- Amphotericin B
- Methotrexate
- Amiodarone

The application provides:

- Drug name and class
- Major clinically relevant adverse effects
- Organ/system mapping
- Monitoring parameters
- Baseline and ongoing monitoring recommendations
- Warning signs
- Risk priority (HIGH, MODERATE, LOW)
- Structured clinical summary output
- Demonstration references clearly labelled as such

## Demonstration data

This project intentionally includes a local demonstration database only.

The application displays the banner:

DEMONSTRATION DATA — NOT FOR CLINICAL DECISION-MAKING

For drugs not in the demonstration database, the app shows:

This drug is not currently available in the demonstration database. Evidence retrieval for additional drugs will be implemented in the next phase.

The prototype does not claim to retrieve live data from FDA, DailyMed, EMA, WHO, or other regulatory sources.

## How to run the application

### Prerequisites

- Python 3.11+ recommended
- pip

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Start the app

```bash
streamlit run app.py
```

The app should launch in the browser on the default Streamlit port.

## Deployment

This repository is a single Streamlit application. It does not contain the
`frontend/`, `backend/`, or serverless API layout described by older project
plans, so it should not be deployed as a Vercel project. Vercel is designed for
static frontends and request-scoped serverless functions, while Streamlit needs
a persistent Python process and WebSocket connection.

The included `Dockerfile` can be deployed to any container host that supports
an HTTP port, such as Cloud Run, Render, Fly.io, or an internal platform:

```bash
docker build -t drug-safety-monitoring-agent .
docker run --rm -p 8501:8501 drug-safety-monitoring-agent
```

Streamlit Community Cloud can also deploy this repository directly by selecting
`app.py` as the application file. No frontend API URL, database, or external API
key is required by the current implementation.

### Environment variables

No environment variables are required to run the current local demonstration
workflow. `LOG_LEVEL` is accepted by `config.py` but is not currently used for
logging. `OPENAI_API_KEY` and `OPENAI_MODEL` are retained as placeholders for a
future integration; the current agent does not call OpenAI or any other external
service, so do not add a key unless that integration is implemented.

## How to run tests

```bash
pytest -q
```

The test suite covers known demonstration drugs, unknown-drug handling, empty-input validation, required output fields, adverse effect structure, monitoring structure, and reference structure.

## Current limitations

- Only four demonstration drugs are supported.
- No live retrieval from authoritative drug databases is implemented.
- All references are clearly labelled as demonstration data.
- This is not a production clinical decision support tool.
- No patient-specific dosing or treatment logic is included.

## Planned future development

Planned next steps include:

- Authoritative source integration interfaces for FDA, DailyMed, EMA, and WHO data
- Drug identification and evidence retrieval from validated sources
- Structured ADR extraction and mapping
- Risk prioritization using evidence-based logic
- Citation tracking and source validation
- Expanded drug coverage beyond the demonstration database

## Project structure

```text
drug-safety-monitoring-agent/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── Dockerfile
├── .dockerignore
├── agent/
│   ├── __init__.py
│   ├── drug_agent.py
│   └── tools.py
├── data/
│   ├── __init__.py
│   ├── drug_database.py
│   └── monitoring_guidelines.py
├── tests/
│   ├── __init__.py
│   └── test_drug_agent.py
├── utils/
│   ├── __init__.py
│   ├── formatters.py
│   └── reference_manager.py
└── CODE_REVIEW_REPORT.md
```

## Security and clinical safeguards

- No hard-coded API keys are used.
- No patient information is accepted or stored.
- No hospital or confidential data is included.
- All external integrations are intentionally stubbed until actual authoritative sources are available.
