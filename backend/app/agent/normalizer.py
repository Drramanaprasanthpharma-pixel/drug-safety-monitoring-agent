"""
Name normalization (spec sections 4-5): generic names, brand names,
spelling variations, and known drug-class names that are inherently
ambiguous. Deliberately offline and network-free — this runs on every
name in every /api/analyze and /api/drugs/resolve call, including
autocomplete-adjacent paths, so it must stay cheap and must never call
the AI provider itself. It only decides *what the user meant by that
name*; drug_agent.py decides *whether we already have clinical data for
it, or need to retrieve it*.
"""
from __future__ import annotations
import difflib
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

from . import cache as ai_cache
from ..engine import data_loader as dl

ALIASES_PATH = Path(__file__).resolve().parent.parent / "data" / "common_aliases.json"

# A fuzzy match below this ratio isn't considered at all.
CANDIDATE_CUTOFF = 0.80
# A top match at or above this ratio, with a healthy margin over the
# runner-up, is treated as confident enough to resolve without asking.
CONFIDENT_RATIO = 0.90
CONFIDENT_MARGIN = 0.08


@dataclass
class Candidate:
    id: str
    generic_name: str
    drug_class: str = ""


@dataclass
class NormalizationResult:
    status: str  # "resolved" | "ambiguous" | "unresolved"
    drug_id: Optional[str] = None
    confidence: float = 0.0
    possible_matches: list[Candidate] = field(default_factory=list)


@lru_cache(maxsize=1)
def _load_aliases() -> dict:
    with open(ALIASES_PATH, "r") as f:
        return json.load(f)


def _alias_entries() -> dict:
    return {k: v for k, v in _load_aliases().items() if not k.startswith("_")}


def _class_entries() -> dict:
    return _load_aliases().get("_classes", {})


def _candidate_for_alias_id(alias_id: str) -> Candidate:
    entry = _alias_entries()[alias_id]
    return Candidate(id=alias_id, generic_name=entry["generic_name"], drug_class=entry.get("drug_class", ""))


def alias_entry(alias_id: str) -> Optional[dict]:
    """Public accessor for a known-identity alias-table entry (generic_name,
    brand_names, drug_class) by its id. Used by drug_agent.py when the
    identity is already established but no clinical record exists yet, so
    it can build a precise retrieval prompt and seed the cached record's
    alias list from the table's own brand names."""
    return _alias_entries().get(alias_id)


def _name_pool() -> dict[str, str]:
    """lowercased name -> canonical id, combining every source we can check
    without a network call: curated drugs, the alias table (generic +
    brand names), and anything already retrieved and cached from the AI."""
    pool: dict[str, str] = {}

    for drug_id, drug in dl.load_drugs().items():
        pool[drug_id.lower()] = drug_id
        pool[drug["generic_name"].lower()] = drug_id
        for brand in drug.get("brand_names", []):
            pool[brand.lower()] = drug_id

    for alias_id, entry in _alias_entries().items():
        pool.setdefault(alias_id.lower(), alias_id)
        pool.setdefault(entry["generic_name"].lower(), alias_id)
        for brand in entry.get("brand_names", []):
            pool.setdefault(brand.lower(), alias_id)

    for cached_id, cached in ai_cache.all_entries().items():
        pool.setdefault(cached_id.lower(), cached_id)
        for alias in cached.get("aliases", []):
            pool.setdefault(alias.lower(), cached_id)

    return pool


def normalize(name: str) -> NormalizationResult:
    q = name.strip().lower()
    if not q:
        return NormalizationResult(status="unresolved")

    # 1. Explicit drug-class names are ambiguous by definition — never guess
    #    which member the person meant (spec section 11).
    classes = _class_entries()
    if q in classes:
        cls = classes[q]
        return NormalizationResult(
            status="ambiguous",
            possible_matches=[_candidate_for_alias_id(m) for m in cls["members"] if m in _alias_entries()],
        )

    # 2. Exact match against curated data, the alias table, or the AI cache.
    pool = _name_pool()
    if q in pool:
        return NormalizationResult(status="resolved", drug_id=pool[q], confidence=1.0)

    # 3. Fuzzy match for spelling variations (spec section 4).
    names = list(pool.keys())
    scored = sorted(
        ((difflib.SequenceMatcher(None, q, n).ratio(), n) for n in names),
        reverse=True,
    )
    scored = [(r, n) for r, n in scored if r >= CANDIDATE_CUTOFF]
    if not scored:
        return NormalizationResult(status="unresolved")

    top_ratio, top_name = scored[0]
    runner_up_ratio = scored[1][0] if len(scored) > 1 else 0.0
    top_id = pool[top_name]

    # Multiple distinct drugs scored close together with no clear winner —
    # ask, rather than guess between two real medications.
    close_ids = {pool[n] for r, n in scored if top_ratio - r <= CONFIDENT_MARGIN}
    if len(close_ids) > 1 and top_ratio < CONFIDENT_RATIO + 0.05:
        matches = []
        for cid in close_ids:
            drug = dl.get_drug(cid)
            if drug:
                matches.append(Candidate(id=cid, generic_name=drug["generic_name"], drug_class=drug.get("drug_class", "")))
            elif cid in _alias_entries():
                matches.append(_candidate_for_alias_id(cid))
        return NormalizationResult(status="ambiguous", possible_matches=matches)

    if top_ratio >= CONFIDENT_RATIO or (top_ratio - runner_up_ratio) >= CONFIDENT_MARGIN:
        return NormalizationResult(status="resolved", drug_id=top_id, confidence=round(top_ratio, 3))

    return NormalizationResult(status="unresolved")
