"""
Persistent cache for AI-assisted drug retrieval (spec section 12).

Default backing store: a local JSON file (backend/app/data/ai_drug_cache.json
locally; /tmp on Vercel, the only writable path in a serverless function —
same pattern as engine/audit.py). If DATABASE_URL is set AND psycopg is
installed, the drug_search_cache table from db/schema.sql is used instead —
this is entirely optional (spec section 13: "if Supabase/PostgreSQL is
already configured, integrate with it rather than introducing another
database unnecessarily"; this repo has neither by default, so the file
cache is what actually runs unless someone wires a Postgres instance).

Every function here degrades to a no-op/miss on any failure rather than
raising — a cache problem must never block a safety analysis from
returning (same philosophy as engine/audit.py).

Entry shape (used by both backends): {"drug": <internal drug dict>,
"aliases": [<lowercased strings>], "source": "ai_retrieval", "cached_at": iso8601}
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

if os.environ.get("VERCEL"):
    CACHE_PATH = Path("/tmp") / "ai_drug_cache.json"
else:
    CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "ai_drug_cache.json"

DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()


def _pg_connect():
    if not DATABASE_URL:
        return None
    try:
        import psycopg  # optional dependency; see requirements.txt
    except ImportError:
        return None
    try:
        return psycopg.connect(DATABASE_URL)
    except Exception:
        return None


def _load_file() -> dict:
    try:
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _save_file(data: dict) -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE_PATH.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        tmp.replace(CACHE_PATH)
    except OSError:
        pass


def all_entries() -> dict:
    """Every cached entry, keyed by canonical drug id."""
    conn = _pg_connect()
    if conn:
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT drug_id, input_aliases, drug_json, source, cached_at FROM drug_search_cache"
                    )
                    rows = cur.fetchall()
            return {
                r[0]: {
                    "drug": r[2] if isinstance(r[2], dict) else json.loads(r[2]),
                    "aliases": list(r[1] or []),
                    "source": r[3],
                    "cached_at": str(r[4]),
                }
                for r in rows
            }
        except Exception:
            pass
        finally:
            conn.close()
    return _load_file()


def get(drug_id: str) -> Optional[dict]:
    return all_entries().get(drug_id)


def save(drug_id: str, drug: dict, aliases: list[str], source: str = "ai_retrieval") -> None:
    clean_aliases = sorted({a.strip().lower() for a in aliases if a and a.strip()})
    conn = _pg_connect()
    if conn:
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO drug_search_cache (drug_id, input_aliases, drug_json, source, cached_at) "
                        "VALUES (%s, %s, %s, %s, %s) "
                        "ON CONFLICT (drug_id) DO UPDATE SET input_aliases = EXCLUDED.input_aliases, "
                        "drug_json = EXCLUDED.drug_json, source = EXCLUDED.source, cached_at = EXCLUDED.cached_at",
                        (drug_id, clean_aliases, json.dumps(drug), source, datetime.now(timezone.utc)),
                    )
            return
        except Exception:
            pass
        finally:
            conn.close()
    data = _load_file()
    data[drug_id] = {
        "drug": drug,
        "aliases": clean_aliases,
        "source": source,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_file(data)


def add_alias(drug_id: str, alias: str) -> None:
    """Records one more spelling/name that resolves to an already-cached
    drug, without re-fetching or re-validating its clinical data."""
    entry = get(drug_id)
    if not entry:
        return
    aliases = set(entry.get("aliases", []))
    aliases.add(alias.strip().lower())
    save(drug_id, entry["drug"], list(aliases), entry.get("source", "ai_retrieval"))


def delete(drug_id: str) -> None:
    conn = _pg_connect()
    if conn:
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM drug_search_cache WHERE drug_id = %s", (drug_id,))
            return
        except Exception:
            pass
        finally:
            conn.close()
    data = _load_file()
    data.pop(drug_id, None)
    _save_file(data)


def clear_all() -> None:
    """Test/dev helper — not exposed via any API endpoint."""
    conn = _pg_connect()
    if conn:
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM drug_search_cache")
            return
        except Exception:
            pass
        finally:
            conn.close()
    _save_file({})
