# Drug Safety & Monitoring AI Agent

A clinical pharmacy decision-support application that helps analyze drug safety profiles, adverse effects, and monitoring requirements.

## ⚠️ Important Disclaimer

**This is a clinical pharmacy decision-support prototype, NOT a replacement for a physician or pharmacist.** All information should be verified against current authoritative references before clinical use.

## Purpose

This application helps:
- Identify major clinically relevant adverse effects for any drug
- Map adverse effects to affected organ systems
- Recommend appropriate monitoring parameters
- Prioritize risks as High/Moderate/Low
- Provide evidence-based warning signs
- Reference authoritative sources

## Features

- **Drug Lookup**: Enter any drug name
- **Adverse Effect Analysis**: Identifies clinically important adverse effects
- **Monitoring Recommendations**: Suggests baseline and ongoing monitoring parameters
- **Risk Prioritization**: Classifies risks by severity
- **Evidence-Based**: References authoritative sources (FDA, DailyMed, EMA, WHO)
- **Clean Output**: Organized tables and structured information

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Internet connection (for API calls and reference retrieval)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Drramanaprasanthpharma-pixel/drug-safety-monitoring-agent.git
   cd drug-safety-monitoring-agent
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create a .env file in the project root
   # (Already included in .gitignore for security)
   
   # Add your OpenAI API key (if using OpenAI):
   OPENAI_API_KEY=your_api_key_here
   
   # Or other API keys as configured
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The application will open in your browser at `http://localhost:8501`

## Usage

1. **Enter a drug name** in the search box
2. **Click "Analyze Drug"** to generate the safety profile
3. **Review the output**, which includes:
   - Drug classification
   - Major adverse effects with risk prioritization
   - Organ/system mapping
   - Monitoring parameters (baseline and ongoing)
   - Warning signs requiring clinical attention
   - Key considerations
   - References and sources

### Example Drugs

Test the application with these examples:
- Vancomycin
- Amphotericin B
- Methotrexate
- Amiodarone

## Project Structure

```
drug-safety-monitoring-agent/
├── app.py                    # Main Streamlit application
├── agent/
│   ├── __init__.py
│   ├── drug_agent.py         # Core agent logic
│   └── tools.py              # Tool definitions (drug search, adverse effects, etc.)
├── data/
│   ├── __init__.py
│   ├── drug_database.py      # Local drug information cache
│   └── monitoring_guidelines.py  # Monitoring parameters and baselines
├── utils/
│   ├── __init__.py
│   ├── reference_manager.py  # Reference retrieval and validation
│   └── formatters.py         # Output formatting utilities
├── config.py                 # Configuration and environment variables
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## File Descriptions

- **app.py**: Main Streamlit interface. Users interact with this file.
- **agent/drug_agent.py**: Core logic orchestrating tool calls and generating analysis
- **agent/tools.py**: Tool interfaces for drug search, adverse effect analysis, monitoring recommendations, reference retrieval
- **data/drug_database.py**: Local clinical database of drugs and their profiles
- **data/monitoring_guidelines.py**: Standard monitoring parameters for different drug classes
- **utils/reference_manager.py**: Manages authoritative source integration
- **utils/formatters.py**: Formats output for display (tables, markdown, etc.)
- **config.py**: Loads environment variables and configuration

## Architecture

The application uses an **agent-based architecture** with tool interfaces:

```
User Input (Drug Name)
    ↓
Drug Agent (orchestrator)
    ├→ drug_information_search()
    │   └ Searches drug name in database and external sources
    ├→ adverse_effect_analysis()
    │   └ Extracts clinically relevant adverse effects
    ├→ monitoring_recommendation()
    │   └ Suggests baseline and ongoing monitoring
    └→ reference_retrieval()
        └ Gathers authoritative source citations
    ↓
Output (Structured Drug Safety Profile)
```

## Safety & Compliance

- ✅ **No patient data**: Application accepts only drug names
- ✅ **No hard-coded secrets**: Uses environment variables for API keys
- ✅ **Source verification**: Distinguishes sourced information from AI interpretation
- ✅ **Uncertainty flagging**: Clearly marks when evidence is insufficient
- ✅ **No fabricated citations**: References are validated before inclusion
- ✅ **Disclaimer-first**: Users see clinical limitation notices prominently

## Integration with Authoritative Sources

The application is designed to integrate with:
- **FDA Orange Book & prescribing information**
- **DailyMed** (National Library of Medicine)
- **EMA** (European Medicines Agency)
- **WHO** guidelines
- **Micromedex** and similar databases (future integrations)

Currently, it uses a local knowledge base and OpenAI's API with structured prompting.

## API Configuration

The application can use:
- **OpenAI API** (for advanced adverse effect analysis)
- **Local knowledge base** (fallback, no API key needed)

Set `OPENAI_API_KEY` in `.env` to enable LLM-powered analysis.

## Testing

Run the test suite:
```bash
pytest tests/
```

Test coverage includes:
- Drug lookup accuracy
- Adverse effect extraction
- Monitoring parameter recommendations
- Reference validation

## Limitations & Future Work

### Current Limitations
- Limited to English language
- Knowledge base updates require manual refresh
- Real-time FDA alerts not yet integrated

### Future Enhancements
- Integration with FDA adverse event reporting database (FAERS)
- Drug interaction checking
- Pregnancy/lactation considerations
- Contraindication screening
- Multi-drug monitoring coordination
- PDF export for clinical records

## Contributing

This is a prototype for demonstration purposes. For production use:
1. Validate against current drug references
2. Implement proper audit logging
3. Add role-based access control
4. Integrate with EHR systems where applicable

## License

[Specify your license here]

## Support & Disclaimer

For questions or issues:
1. Check this README
2. Review example test cases
3. Verify drug information against authoritative sources

**Always verify information against current authoritative clinical references before clinical use.**

## References

- FDA Orange Book: https://www.accessdata.fda.gov/scripts/cder/ob/default.cfm
- DailyMed: https://dailymed.nlm.nih.gov/
- EMA: https://www.ema.europa.eu/
- WHO: https://www.who.int/
