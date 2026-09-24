"""
Shared exception types for the drug resolution pipeline (spec section 11).

Defined in their own module (rather than in orchestrator.py or drug_agent.py)
so both can import them without a circular import: orchestrator.py needs
them to translate agent failures into the pipeline's control flow, and
main.py needs them to translate to HTTP/response messages.

`UnknownDrugError.reason` is a short machine-readable code, not a
sentence — main.py maps each code to the actual user-facing message, so
the wording lives in one place (main.py) rather than being duplicated or
drifting between the exception and its handler:
  "ai_unavailable"   — no AI provider configured, or the provider call failed
  "invalid_response" — the AI responded but its JSON failed schema validation
  None               — normalizer + AI (when available) both concluded the
                        name doesn't correspond to a real medication
"""
from __future__ import annotations


class UnknownDrugError(Exception):
    """Raised when a medication name cannot be confidently identified. The
    system never fabricates a drug record in this case (spec section 11)."""

    def __init__(self, name: str, reason: str | None = None):
        self.name = name
        self.reason = reason
        super().__init__(f"Unrecognized medication: '{name}'" + (f" ({reason})" if reason else ""))


class AmbiguousDrugError(Exception):
    """Raised when a name could plausibly refer to more than one medication
    and the system is not confident enough to silently pick one (spec
    section 5: 'DO NOT silently guess when multiple drugs could match').
    `possible_matches` is a list of plain dicts shaped like
    models.PossibleMatch: {"id": str|None, "generic_name": str, "drug_class": str}."""

    def __init__(self, name: str, possible_matches: list[dict]):
        self.name = name
        self.possible_matches = possible_matches
        super().__init__(f"Ambiguous medication name: '{name}'")
