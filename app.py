"""
Main Streamlit Application for Drug Safety & Monitoring AI Agent.

This is a clinical pharmacy decision-support prototype.
NOT a replacement for a physician or pharmacist.
"""

import streamlit as st
from agent.drug_agent import DrugSafetyAgent
from utils.formatters import DrugSafetyFormatter
import config

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Title and Disclaimer
# ============================================================================

st.markdown("# 💊 Drug Safety & Monitoring AI Agent")
st.markdown("### Clinical Pharmacy Decision-Support Prototype")

# Display critical disclaimer
with st.container():
    st.warning(
        config.CLINICAL_DISCLAIMER,
        icon="⚠️"
    )

st.markdown("---")

# ============================================================================
# Sidebar Information
# ============================================================================

with st.sidebar:
    st.markdown("## About This Tool")
    st.markdown(
        """
        This application provides:
        - Drug safety profile analysis
        - Adverse effect identification
        - Monitoring recommendations
        - Warning sign identification
        - References to authoritative sources

        **Current Status:** Demonstration version with local database

        **Data Source:** Local knowledge base (demonstration data)
        """
    )
    st.markdown("---")
    st.markdown("## Example Drugs to Test")
    st.markdown(
        """
        - Vancomycin
        - Amphotericin B
        - Methotrexate
        - Amiodarone
        """
    )
    st.markdown("---")
    st.markdown("## Important Links")
    st.markdown(
        """
        - [DailyMed](https://dailymed.nlm.nih.gov/)
        - [FDA Orange Book](https://www.accessdata.fda.gov/scripts/cder/ob/default.cfm)
        - [EMA](https://www.ema.europa.eu/)
        - [WHO](https://www.who.int/)
        """
    )

# ============================================================================
# Main Application Logic
# ============================================================================

# Initialize agent
if "agent" not in st.session_state:
    st.session_state.agent = DrugSafetyAgent()

if "drug_profile" not in st.session_state:
    st.session_state.drug_profile = None

if "drug_name_input" not in st.session_state:
    st.session_state.drug_name_input = ""

# ============================================================================
# User Input Section
# ============================================================================

st.markdown("## Drug Safety Analysis")

col1, col2 = st.columns([3, 1])

with col1:
    drug_name = st.text_input(
        "Enter a drug name:",
        placeholder="e.g., Vancomycin, Amphotericin B, Methotrexate, Amiodarone",
        help="Enter the drug name (brand or generic)"
    )

with col2:
    analyze_button = st.button("🔍 Analyze Drug", use_container_width=True)

# ============================================================================
# Analysis Logic
# ============================================================================

if analyze_button and drug_name:
    with st.spinner("Analyzing drug safety profile..."):
        profile = st.session_state.agent.analyze_drug(drug_name)
        st.session_state.drug_profile = profile

        if profile is None:
            st.error(
                f"❌ Drug not available in the demonstration database.\n\n"
                f"**'{drug_name}'** was not found.\n\n"
                f"Authoritative drug information retrieval (FDA, DailyMed, EMA, WHO) "
                f"will be added in the next development stage.\n\n"
                f"Currently available test drugs: Vancomycin, Amphotericin B, Methotrexate, Amiodarone"
            )
        else:
            st.success(f"✅ Analysis complete for {profile.drug.name}")

# ============================================================================
# Results Display
# ============================================================================

if st.session_state.drug_profile:
    profile = st.session_state.drug_profile

    # Display uncertainty notes if present
    if profile.uncertainty_notes:
        st.info(profile.uncertainty_notes, icon="ℹ️")

    # ========================================================================
    # Tab 1: Drug Information
    # ========================================================================

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Drug Info", "Adverse Effects", "Monitoring", "Warning Signs", "References"]
    )

    with tab1:
        st.markdown("### Drug Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Drug Name (Generic)**")
            st.markdown(f"`{profile.drug.name}`")

            st.markdown("**Drug Class**")
            st.markdown(f"`{profile.drug.drug_class}`")

        with col2:
            st.markdown("**Generic Name**")
            st.markdown(f"`{profile.drug.generic_name}`")

            if profile.drug.brand_names:
                st.markdown("**Brand Names**")
                st.markdown(f"`{', '.join(profile.drug.brand_names)}`")

        st.markdown("---")
        st.markdown("### Key Clinical Considerations")
        considerations_text = DrugSafetyFormatter.format_key_considerations(
            profile.key_considerations
        )
        st.markdown(considerations_text)

    # ========================================================================
    # Tab 2: Adverse Effects
    # ========================================================================

    with tab2:
        st.markdown("### Major Adverse Effects")
        st.markdown(
            "Listed in order of risk severity (HIGH → MODERATE → LOW)"
        )

        if profile.adverse_effects:
            df = DrugSafetyFormatter.format_adverse_effects_table(
                profile.adverse_effects
            )
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

            # Color-coded severity indicators
            st.markdown("---")
            st.markdown("#### Severity Legend")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("🔴 **HIGH** - Critical monitoring required")
            with col2:
                st.markdown("🟠 **MODERATE** - Regular monitoring needed")
            with col3:
                st.markdown("🟢 **LOW** - Standard monitoring sufficient")
        else:
            st.info("No adverse effects recorded.")

    # ========================================================================
    # Tab 3: Monitoring Recommendations
    # ========================================================================

    with tab3:
        st.markdown("### Monitoring Parameters")

        baseline_df, ongoing_df = DrugSafetyFormatter.format_monitoring_table(
            profile.monitoring_parameters
        )

        st.markdown("#### Baseline Monitoring (Before Starting Therapy)")
        if not baseline_df.empty:
            st.dataframe(
                baseline_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No baseline monitoring specified.")

        st.markdown("#### Ongoing Monitoring (During Therapy)")
        if not ongoing_df.empty:
            st.dataframe(
                ongoing_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No ongoing monitoring specified.")

    # ========================================================================
    # Tab 4: Warning Signs
    # ========================================================================

    with tab4:
        st.markdown("### Clinical Warning Signs")
        st.markdown(
            "These signs should trigger immediate clinical attention:"
        )

        if profile.warning_signs:
            df = DrugSafetyFormatter.format_warning_signs_table(
                profile.warning_signs
            )
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No warning signs recorded.")

    # ========================================================================
    # Tab 5: References
    # ========================================================================

    with tab5:
        st.markdown("### References & Sources")
        st.markdown(
            "Information sourced from authoritative clinical databases:"
        )

        if profile.references:
            references_text = DrugSafetyFormatter.format_references_list(
                profile.references
            )
            st.markdown(references_text)
        else:
            st.info("No references available.")

        st.markdown("---")
        st.markdown("#### Data Source Disclaimer")
        st.info(
            "Current version uses a **demonstration local database** for testing purposes. "
            "Integration with live FDA, DailyMed, EMA, and WHO data sources will be added in future releases. "
            "Always verify information against current authoritative clinical references."
        )

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown(
    """
    **Disclaimer & Intended Use:**
    - This tool is a **demonstration prototype** for research and educational purposes only
    - NOT a replacement for a physician or pharmacist
    - All recommendations must be verified against current authoritative clinical sources
    - Do not use for patient-specific treatment decisions
    - This tool should only be used by healthcare professionals with appropriate training

    **Questions or Issues?** Refer to the README.md for setup and usage instructions.
    """
)
