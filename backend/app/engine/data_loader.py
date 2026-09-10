"""
Loads the curated demo dataset and provides name resolution (generic name,
brand name, or id -> canonical drug id). This stands in for the "Drug
normalization" + "Drug database" steps of the architecture diagram in the
spec. In a production deployment this module would be replaced by calls to
a licensed drug database (e.g., First Databank, Multum, RxNorm + a
commercial interaction database) rather than a static JSON file.
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
    """Resolve a free-text drug name/id to a canonical id, or None if unknown."""
    return _name_index().get(name.strip().lower())


def search_drugs(query: str, limit: int = 10) -> list[dict]:
    """Autocomplete-style search across generic + brand names."""
    q = query.strip().lower()
    drugs = load_drugs()
    if not q:
        results = list(drugs.values())[:limit]
    else:
        results = []
        for drug in drugs.values():
            names = [drug["generic_name"].lower()] + [b.lower() for b in drug.get("brand_names", [])]
            if any(q in n for n in names):
                results.append(drug)
        results = results[:limit]
    return [
        {
            "id": d["id"],
            "generic_name": d["generic_name"],
            "brand_names": d["brand_names"],
            "drug_class": d["drug_class"],
        }
        for d in results
    ]


def get_drug(drug_id: str) -> Optional[dict]:
    return load_drugs().get(drug_id)


def find_interaction(id_a: str, id_b: str) -> Optional[dict]:
    for rule in load_interactions():
        pair = set(rule["pair"])
        if pair == {id_a, id_b}:
            return rule
    return None
