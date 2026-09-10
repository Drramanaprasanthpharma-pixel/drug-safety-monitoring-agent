"""
Reference management for drug information sources.
This prototype intentionally uses a demonstration reference catalog rather than
live retrieval from FDA, DailyMed, EMA, WHO, or other external databases.
"""

from typing import List
from datetime import datetime
from agent.tools import Reference


class ReferenceManager:
    """
    Manages references and source labels for the demo prototype.
    Future versions can add authenticated retrieval interfaces for authoritative
    sources, but the current implementation does not claim live API access.
    """

    def __init__(self):
        """Initialize reference manager."""
        self.references_db = self._initialize_references()

    def _initialize_references(self) -> dict:
        """Initialize demonstration reference database."""
        return {
            "vancomycin": [
                Reference(
                    title="Demonstration reference summary: Vancomycin safety considerations",
                    source="Demonstration reference set (prototype only; no live FDA/DailyMed retrieval)",
                    url=None,
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.0,
                    evidence_type="DEMONSTRATION"
                ),
            ],
            "amphotericin b": [
                Reference(
                    title="Demonstration reference summary: Amphotericin B safety considerations",
                    source="Demonstration reference set (prototype only; no live FDA/DailyMed retrieval)",
                    url=None,
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.0,
                    evidence_type="DEMONSTRATION"
                ),
            ],
            "methotrexate": [
                Reference(
                    title="Demonstration reference summary: Methotrexate safety considerations",
                    source="Demonstration reference set (prototype only; no live FDA/DailyMed retrieval)",
                    url=None,
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.0,
                    evidence_type="DEMONSTRATION"
                ),
            ],
            "amiodarone": [
                Reference(
                    title="Demonstration reference summary: Amiodarone safety considerations",
                    source="Demonstration reference set (prototype only; no live FDA/DailyMed retrieval)",
                    url=None,
                    date_accessed=datetime.now().isoformat(),
                    reliability_score=0.0,
                    evidence_type="DEMONSTRATION"
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
        """Get default reference set for unsupported drugs."""
        return [
            Reference(
                title="No live evidence retrieved for this drug",
                source="Demonstration reference set (prototype only; no live FDA/DailyMed retrieval)",
                url=None,
                date_accessed=datetime.now().isoformat(),
                reliability_score=0.0,
                evidence_type="DEMONSTRATION"
            )
        ]

    def validate_reference(self, reference: Reference) -> bool:
        """Return True only for real authoritative sources when actually retrieved."""
        if reference.evidence_type == "DEMONSTRATION":
            return False
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
