"""
Loads the curated demo dataset and provides name resolution (generic name,
brand name, or id -> canonical drug id). This stands in for the "Drug
normalization" + "Drug database" steps of the architecture diagram in the
spec. In a production deployment this module would be replaced by calls to
a licensed drug database (e.g., First Databank, Multum, RxNorm + a
commercial interaction database) rather than a static JSON file.

This module still knows nothing about the AI beyond one thing: after
agent/drug_agent.py retrieves and validates a drug, it lands in the same
cache this module reads from (agent/cache.py) — so every function here
transparently also sees anything already resolved that way, with no
network calls of its own. `agent` is imported lazily inside the functions
that need it, purely to keep this module's own import graph exactly as
light as it was before this upgrade.
"""
from __future__ import annotations
import json
from pathlib import Path
from functools import lru_cache
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=1)
def load_drugs() -> dict:
    with open(DATA_DIR / "drugs.json", "r") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_interactions() -> list:
    with open(DATA_DIR / "interactions.json", "r") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_disease_interactions() -> dict:
    with open(DATA_DIR / "disease_interactions.json", "r") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _name_index() -> dict:
    """Maps lowercased generic/brand names -> canonical drug id."""
    index = {}
    for drug_id, drug in load_drugs().items():
        index[drug_id.lower()] = drug_id
        index[drug["generic_name"].lower()] = drug_id
        for brand in drug.get("brand_names", []):
            index[brand.lower()] = drug_id
    return index


def resolve_drug_id(name: str) -> Optional[str]:
    """Resolve a free-text drug name/id to a canonical id, or None if unknown
    to both the curated dataset and anything already cached from a prior
    AI retrieval. Does not itself call the AI — see agent.drug_agent for
    the fallback that runs when this returns None."""
    q = name.strip().lower()
    local = _name_index().get(q)
    if local:
        return local
    from ..agent import cache as ai_cache  # local import: keep this module's own import graph unchanged
    for cached_id, entry in ai_cache.all_entries().items():
        if q == cached_id.lower() or q in entry.get("aliases", []):
            return cached_id
    return None


def search_drugs(query: str, limit: int = 10) -> list[dict]:
    """Autocomplete-style search across generic + brand names, including
    any medications already retrieved via AI in a previous request (never
    triggers a new AI call itself)."""
    from ..agent import cache as ai_cache

    q = query.strip().lower()
    drugs = load_drugs()
    cached = {cid: entry["drug"] for cid, entry in ai_cache.all_entries().items() if cid not in drugs}

    def matches(d: dict) -> bool:
        if not q:
            return True
        names = [d["generic_name"].lower()] + [b.lower() for b in d.get("brand_names", [])]
        return any(q in n for n in names)

    results = [(d, "database") for d in drugs.values() if matches(d)]
    results += [(d, "ai_retrieval") for d in cached.values() if matches(d)]
    results = results[:limit]
    return [
        {
            "id": d["id"],
            "generic_name": d["generic_name"],
            "brand_names": d["brand_names"],
            "drug_class": d["drug_class"],
            "source": source,
        }
        for d, source in results
    ]


def get_drug(drug_id: str) -> Optional[dict]:
    local = load_drugs().get(drug_id)
    if local:
        return local
    from ..agent import cache as ai_cache
    cached = ai_cache.get(drug_id)
    return cached["drug"] if cached else None


def find_interaction(id_a: str, id_b: str) -> Optional[dict]:
    for rule in load_interactions():
        pair = set(rule["pair"])
        if pair == {id_a, id_b}:
            return rule
    return None
