"""
Configuration module for Drug Safety & Monitoring AI Agent.
Loads environment variables and manages application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# API Configuration
# ============================================================================

# OpenAI API Key (for LLM-powered adverse effect analysis)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# OpenAI Model to use
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# ============================================================================
# Application Settings
# ============================================================================

# Application title and description
APP_TITLE = "Drug Safety & Monitoring AI Agent"
APP_DESCRIPTION = "Clinical pharmacy decision-support for drug safety analysis"

# Maximum drug name length for input validation
MAX_DRUG_NAME_LENGTH = 200

# Enable/disable various features
ENABLE_LLM_ANALYSIS = OPENAI_API_KEY != ""  # Only enable if API key exists
ENABLE_LOCAL_DATABASE = True
ENABLE_REFERENCE_VALIDATION = True

# ============================================================================
# Risk Categories
# ============================================================================

RISK_PRIORITIES = {
    "HIGH": {"color": "#FF4444", "level": 1},
    "MODERATE": {"color": "#FFB84D", "level": 2},
    "LOW": {"color": "#4CAF50", "level": 3},
}

# ============================================================================
# Monitoring Categories
# ============================================================================

MONITORING_TYPES = {
    "baseline": "Tests/measurements at baseline (start of therapy)",
    "ongoing": "Regular monitoring during therapy",
    "periodic": "Periodic reassessment",
}

# ============================================================================
# Output Settings
# ============================================================================

# Format for displaying drug information
OUTPUT_FORMAT = "table"  # Options: "table", "json", "markdown"

# Number of top adverse effects to display
MAX_ADVERSE_EFFECTS_DISPLAY = 10

# ============================================================================
# Disclaimer Messages
# ============================================================================

CLINICAL_DISCLAIMER = """
⚠️ **IMPORTANT CLINICAL DISCLAIMER**

This application is a **decision-support prototype**, NOT a replacement for a physician or pharmacist.

- All information should be verified against current authoritative references
- Use only for educational and informational purposes
- Do not make patient-specific clinical decisions based solely on this tool
- When in doubt, consult with qualified healthcare professionals
- Always review current drug prescribing information and guidelines
"""

# ============================================================================
# Logging
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
