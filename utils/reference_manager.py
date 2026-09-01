"""
Reference management for drug information sources.
Handles retrieval and validation of authoritative sources.
"""

from typing import List, Optional
from datetime import datetime
from agent.tools import Reference


class ReferenceManager:
    """
    Manages references and authoritative sources for drug information.
    Currently uses demonstration references.
    Future: integrate with FDA, DailyMed, EMA APIs.
    """

    def __init__(self):
        """Initialize reference manager."""
        self.references_db = self._initialize_references()

    def _initialize_references(self) -> dict:
        """Initialize demonstration reference database."""
        return {
            "vancomycin": [
                Reference(
                    title="Vancomycin Prescribing Information - FDA",
                    source="FDA Orange Book",
                    url="https://www.fda.gov/drugs/drug-safety-and-availability/fda-approved-drugs",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.95
                ),
                Reference(
                    title="Vancomycin - DailyMed",
                    source="DailyMed (NLM)",
                    url="https://dailymed.nlm.nih.gov/",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.95
                ),
                Reference(
                    title="ASHP Therapeutic Guidelines: Vancomycin Dosing & Monitoring",
                    source="ASHP (American Society of Health-System Pharmacists)",
                    url="https://www.ashp.org/",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.90
                ),
            ],
            "amphotericin b": [
                Reference(
                    title="Amphotericin B Prescribing Information - FDA",
                    source="FDA Orange Book",
                    url="https://www.fda.gov/drugs/drug-safety-and-availability/fda-approved-drugs",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.95
                ),
                Reference(
                    title="Amphotericin B - DailyMed",
                    source="DailyMed (NLM)",
                    url="https://dailymed.nlm.nih.gov/",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.95
                ),
                Reference(
                    title="IDSA Guidelines for Amphotericin B Use",
                    source="IDSA (Infectious Diseases Society of America)",
                    url="https://www.idsociety.org/",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.92
                ),
            ],
            "methotrexate": [
                Reference(
                    title="Methotrexate Prescribing Information - FDA",
                    source="FDA Orange Book",
                    url="https://www.fda.gov/drugs/drug-safety-and-availability/fda-approved-drugs",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.95
                ),
                Reference(
                    title="Methotrexate - DailyMed",
                    source="DailyMed (NLM)",
                    url="https://dailymed.nlm.nih.gov/",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.95
                ),
                Reference(
                    title="ACR Guidelines for Methotrexate Use in Rheumatoid Arthritis",
                    source="ACR (American College of Rheumatology)",
                    url="https://www.rheumatology.org/",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.90
                ),
            ],
            "amiodarone": [
                Reference(
                    title="Amiodarone Prescribing Information - FDA",
                    source="FDA Orange Book",
                    url="https://www.fda.gov/drugs/drug-safety-and-availability/fda-approved-drugs",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.95
                ),
                Reference(
                    title="Amiodarone - DailyMed",
                    source="DailyMed (NLM)",
                    url="https://dailymed.nlm.nih.gov/",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.95
                ),
                Reference(
                    title="ACC/AHA Guidelines for Arrhythmia Management",
                    source="ACC/AHA (American College of Cardiology/American Heart Association)",
                    url="https://www.acc.org/",
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.92
                ),
            ],
        }

    def get_references(self, drug_name: str) -> List[Reference]:
        """Get references for a drug."""
        drug_key = drug_name.lower().strip()
        if drug_key in self.references_db:
            return self.references_db[drug_key]
        return self._get_default_references()

    def _get_default_references(self) -> List[Reference]:
        """Get default references when drug not found."""
        return [
            Reference(
                title="DailyMed - National Library of Medicine",
                source="DailyMed (NLM)",
                url="https://dailymed.nlm.nih.gov/",
                date_accessed=datetime.now().isoformat(),
                reliability_score=0.95
            ),
            Reference(
                title="FDA Orange Book",
                source="FDA",
                url="https://www.fda.gov/drugs/drug-safety-and-availability/fda-approved-drugs",
                date_accessed=datetime.now().isoformat(),
                reliability_score=0.95
            ),
        ]

    def validate_reference(self, reference: Reference) -> bool:
        """Validate that a reference is from an authoritative source."""
        authoritative_sources = {
            "FDA",
            "DailyMed",
            "EMA",
            "WHO",
            "ASHP",
            "IDSA",
            "ACR",
            "ACC/AHA",
        }
        return any(source in reference.source for source in authoritative_sources)
