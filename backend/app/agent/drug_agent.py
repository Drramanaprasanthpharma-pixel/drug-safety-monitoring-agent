"""
Resolves a free-text medication name that the curated dataset — including
anything already cached from a prior AI retrieval, which data_loader.py
checks transparently — does not recognize, using AI-assisted normalization
and retrieval (spec sections 3-8, 11, 12, 18).

Public entry points (both used by orchestrator.py / main.py):

    resolve_and_ensure(name) -> drug_id
    refresh(drug_id) -> drug_id

Both either return a canonical id that data_loader.get_drug() can now
resolve (because a schema-validated record for it was just cached), or
raise UnknownDrugError / AmbiguousDrugError. Nothing reaches the
deterministic engines that wasn't validated by schemas.AIDrugRecord first
(spec section 7).

Pipeline (spec sections 4-6's normalization vs. retrieval split):
  1. normalizer.normalize(name) — offline, network-free. Recognizes
     curated data, the alias table, anything already cached, spelling
     variations, and drug-class-name ambiguity, without ever calling the AI.
  2. If normalization resolved to a *known identity* that has no clinical
     record yet (e.g. "Lipitor" -> atorvastatin, not yet retrieved), ask
     the AI to describe that exact, already-identified medication —
     skipping the "what drug is this" framing entirely.
  3. If normalization found nothing locally at all, ask the AI to both
     identify and describe the medication in one call.
  4. Validate the AI's response (schemas.AIEnvelope); retry once with the
     validation error fed back; if it still doesn't validate, or no AI
     provider is configured, or the provider call fails, raise
     UnknownDrugError with a short, machine-readable `reason` code (see
     errors.py) — main.py owns the actual user-facing wording for each
     code, so it isn't duplicated here.
"""
from __future__ import annotations
import json
import re

from pydantic import ValidationError

from . import cache, normalizer
from .ai_client import AIUnavailable, get_client
from .errors import AmbiguousDrugError, UnknownDrugError
from .prompts import (
    build_correction_prompt, build_known_identity_prompt, build_user_prompt,
    strip_code_fences, SYSTEM_PROMPT,
)
from .schemas import AIEnvelope
from ..engine import data_loader as dl


def _slugify(generic_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", generic_name.strip().lower()).strip("-")
    return slug or "unknown-drug"


def _unique_id(generic_name: str, *, reserve: str | None = None) -> str:
    """Picks a canonical id for a newly-retrieved drug. `reserve` lets
    refresh() keep reusing the same id across re-retrievals instead of
    minting a new one each time."""
    if reserve:
        return reserve
    base = _slugify(generic_name)
    if dl.get_drug(base) is None:
        return base
    n = 2
    while dl.get_drug(f"{base}-{n}") is not None:
        n += 1
    return f"{base}-{n}"


def _to_internal_record(drug_id: str, ai_record) -> dict:
    """Converts a validated AIDrugRecord into the same plain-dict shape as a
    curated entry in data/drugs.json, with clear AI-provenance labeling
    (spec section 16) and evidence confidence capped at 'Moderate' since
    this was not read from a live regulatory feed."""
    record = ai_record.model_dump()
    record["id"] = drug_id
    capped_evidence = []
    for e in record.get("evidence") or []:
        conf = e.get("confidence") or "Unknown"
        if conf == "High":
            conf = "Moderate"
        source = e.get("source") or "AI-assisted retrieval"
        if "AI-assisted" not in source:
            source = f"AI-assisted retrieval — {source}"
        capped_evidence.append({**e, "confidence": conf, "source": source})
    if not capped_evidence:
        capped_evidence = [{
            "source": "AI-assisted retrieval — not verified against a live regulatory feed",
            "reference": None, "date": None, "confidence": "Limited",
        }]
    record["evidence"] = capped_evidence
    record["ai_generated"] = True
    record["verified"] = False
    return record


def _run_ai(user_prompt: str) -> AIEnvelope:
    """Calls the configured provider, validating (and retrying once, with
    the validation error fed back, on a correctable parse/schema failure)
    until a valid AIEnvelope comes back.

    Raises AIUnavailable (no provider configured, or the provider call
    itself failed — spec section 18) or ValueError (the provider responded
    both times but never produced a schema-valid object — spec section 7).
    Callers translate both into UnknownDrugError with the matching reason
    code; they are kept as distinct exception types here so tests can
    verify each failure mode independently.
    """
    client = get_client()
    user = user_prompt
    last_error = ""
    for _attempt in range(2):
        raw = client.generate_json(SYSTEM_PROMPT, user)  # raises AIUnavailable if not configured / call fails
        try:
            parsed = json.loads(strip_code_fences(raw))
            return AIEnvelope.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)
            user = build_correction_prompt(last_error)
    raise ValueError(last_error)


def _handle_envelope(name: str, envelope: AIEnvelope, *, reserve_id: str | None = None) -> str:
    if envelope.status == "unknown_drug":
        raise UnknownDrugError(name, None)

    if envelope.status == "ambiguous_drug":
        matches = [m.model_dump() for m in envelope.possible_matches]
        raise AmbiguousDrugError(name, matches)

    # status == "found"
    generic_name = envelope.drug.generic_name
    if not reserve_id:
        # The AI may have correctly identified a medication that IS in the
        # curated dataset, just under a name the offline normalizer didn't
        # catch. Prefer the authoritative curated record over the AI's own
        # description of the same drug (spec section 4: "If found -> use
        # local authoritative data").
        curated_id = dl.resolve_drug_id(generic_name)
        if curated_id and curated_id in dl.load_drugs():
            return curated_id

    drug_id = _unique_id(generic_name, reserve=reserve_id)
    record = _to_internal_record(drug_id, envelope.drug)
    existing_aliases = (cache.get(drug_id) or {}).get("aliases", [])
    cache.save(drug_id, record, aliases=[*existing_aliases, name, generic_name], source="ai_retrieval")
    return drug_id


def resolve_and_ensure(name: str) -> str:
    """Normalizes and, if necessary, retrieves-and-caches a full clinical
    record for `name`, returning a canonical drug id. Never returns a
    placeholder — every return value is immediately usable with
    data_loader.get_drug()."""
    norm = normalizer.normalize(name)

    if norm.status == "ambiguous":
        matches = [
            {"generic_name": m.generic_name, "drug_class": m.drug_class}
            for m in norm.possible_matches
        ]
        raise AmbiguousDrugError(name, matches)

    if norm.status == "resolved":
        if dl.get_drug(norm.drug_id):
            return norm.drug_id
        # The identity is confirmed (curated/alias/spelling match), but no
        # clinical record has been retrieved for it yet — ask the AI to
        # describe this exact, already-identified medication rather than
        # re-asking "what drug is this" (spec sections 4-5 vs 6).
        alias = normalizer.alias_entry(norm.drug_id)
        generic_name = (alias or {}).get("generic_name", norm.drug_id)
        drug_class_hint = (alias or {}).get("drug_class")
        user_prompt = build_known_identity_prompt(generic_name, drug_class_hint)
    else:
        # Nothing local recognizes this name at all — ask the AI to both
        # identify and describe it in one call.
        user_prompt = build_user_prompt(name, alias_hint=None)

    try:
        envelope = _run_ai(user_prompt)
    except AIUnavailable as e:
        raise UnknownDrugError(name, "ai_unavailable") from e
    except ValueError as e:
        raise UnknownDrugError(name, "invalid_response") from e

    return _handle_envelope(name, envelope)


def refresh(drug_id: str) -> str:
    """Forces a fresh AI retrieval for an existing AI-sourced drug id,
    overwriting its cache entry in place (same id, so nothing that already
    references it breaks). Raises ValueError if `drug_id` is not a
    currently AI-cached drug — this endpoint re-fetches something already
    retrieved via AI, it never creates a new entry from an arbitrary name
    (use resolve_and_ensure / POST /api/drugs/resolve for that), and it
    never touches the curated dataset (spec section 14)."""
    entry = cache.get(drug_id)
    if not entry:
        raise ValueError(f"'{drug_id}' is not a currently cached AI-retrieved drug — nothing to refresh.")

    generic_name = entry["drug"]["generic_name"]
    alias = normalizer.alias_entry(drug_id)
    drug_class_hint = (alias or {}).get("drug_class") or entry["drug"].get("drug_class")
    user_prompt = build_known_identity_prompt(generic_name, drug_class_hint)

    try:
        envelope = _run_ai(user_prompt)
    except AIUnavailable as e:
        raise UnknownDrugError(drug_id, "ai_unavailable") from e
    except ValueError as e:
        raise UnknownDrugError(drug_id, "invalid_response") from e

    return _handle_envelope(drug_id, envelope, reserve_id=drug_id)
