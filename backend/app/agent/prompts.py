"""
Prompt construction for AI-assisted drug normalization and retrieval.

Kept in its own module so the prompt text — the actual clinical-safety
contract given to the model — is easy to find, review, and tighten without
digging through control-flow code.
"""
from __future__ import annotations
import json

SCHEMA_HINT = """
Return ONLY a single JSON object (no prose, no markdown code fences) with
exactly this shape:

{
  "status": "found" | "ambiguous_drug" | "unknown_drug",
  "normalization": {
    "input_name": "<the name exactly as given to you>",
    "normalized_name": "<generic name you resolved it to, or null>",
    "generic_name": "<same as normalized_name, or null>",
    "drug_class": "<pharmacologic class, or null>",
    "confidence": <number 0.0-1.0>
  },
  "possible_matches": [
    {"generic_name": "...", "drug_class": "...", "reason": "why this could be the intended match"}
  ],
  "drug": null | {
    "generic_name": "...",
    "brand_names": ["..."],
    "drug_class": "...",
    "pharmacology": "...",
    "boxed_warning": "..." | null,
    "contraindications": ["..."],
    "adverse_effects": {"common": ["..."], "serious": ["..."], "life_threatening": ["..."]},
    "organ_toxicity": [
      {"organ": "...", "risk_level": "Low"|"Moderate"|"High"|"Critical", "reason": "...",
       "toxicity": "...", "monitoring_parameters": ["..."], "frequency": "...",
       "thresholds": "...", "source": "..."}
    ],
    "monitoring_parameters": [
      {"parameter": "...", "why": "...", "baseline": "Yes"|"No"|"Consider"|"n/a",
       "follow_up": "...", "alert_threshold": "...", "risk": "Low"|"Moderate"|"High"|"Critical"}
    ],
    "vital_signs": [{"parameter": "...", "why": "..."}],
    "renal_dosing": "..." | null,
    "hepatic_dosing": "..." | null,
    "high_risk_populations": ["..."],
    "therapeutic_drug_monitoring": {"applicable": true|false, "target_range": "..." | null, "notes": "..." | null},
    "evidence": [{"source": "...", "reference": "..." | null, "date": "..." | null,
                  "confidence": "High"|"Moderate"|"Limited"|"Unknown"}]
  }
}

Rules:
- "possible_matches" is used only when status is "ambiguous_drug"; otherwise return an empty array.
- "drug" MUST be null unless status is "found".
- Use status "ambiguous_drug" when the name could plausibly refer to more
  than one distinct medication and you are not confident which one is
  meant. Do not silently guess.
- Use status "unknown_drug" when the input does not correspond to any real
  medication you can identify with reasonable confidence. Do not invent a
  plausible-sounding drug.
- When status is "found", every field in "drug" must reflect only
  information you are reasonably confident is accurate for that medication.
  Do not invent specific numeric thresholds, lab values, or citations you
  are not confident about — use general, well-established clinical
  knowledge and mark the evidence confidence as "Moderate" or "Limited"
  rather than "High" unless you are recalling well-established prescribing
  information (labeling-level facts most clinicians would recognize).
- Never invent a drug interaction, dose, or contraindication that is not
  well-established. If uncertain about a specific field, use a general,
  clinically cautious statement rather than a fabricated specific.
""".strip()

SYSTEM_PROMPT = """
You are a clinical drug information normalization and retrieval assistant
supporting a pharmacist medication-safety review tool. You do not make
clinical decisions and your output is never shown to a patient directly —
it is validated by software and then passed through separate deterministic
safety-rules engines (interaction checking, organ toxicity scoring,
monitoring schedules, red flags) before a pharmacist ever sees it. Those
engines, not you, are responsible for risk scoring and flagging — your job
is narrower: identify what medication is meant, and if you can, describe
its established pharmacology, contraindications, adverse effects, organ
toxicity, and monitoring in a structured way.

You must never fabricate: do not invent a medication that does not exist,
do not invent specific dosing/lab thresholds you're not confident about,
and do not invent citations. If you are not sure, say so via the
"unknown_drug" or "ambiguous_drug" status, or by using general/cautious
language rather than a fabricated specific fact.
""".strip() + "\n\n" + SCHEMA_HINT


def build_user_prompt(name: str, alias_hint: str | None) -> str:
    hint = (
        f"\nA lookup table suggests this name commonly refers to the generic "
        f"medication '{alias_hint}'. Use this as a strong hint, but verify it "
        f"makes sense before relying on it.\n"
        if alias_hint
        else ""
    )
    return (
        f"Identify and describe the medication referred to by this name, as "
        f"entered by a pharmacist: \"{name}\"\n{hint}\n"
        f"Respond with the JSON object described in your instructions, and "
        f"nothing else."
    )


def build_known_identity_prompt(generic_name: str, drug_class_hint: str | None) -> str:
    """Used when the offline alias table already told us exactly which
    medication is meant (spec section 4/5), but no clinical record exists
    for it yet. Skips the identify-what-this-is framing entirely so the AI
    spends its attention on retrieval quality, not on re-deciding identity
    it was already given with confidence."""
    hint = f" (pharmacologic class: {drug_class_hint})" if drug_class_hint else ""
    return (
        f"The medication's identity is already confirmed: generic name "
        f"\"{generic_name}\"{hint}. Describe its established pharmacology, "
        f"contraindications, adverse effects, organ toxicity, and monitoring "
        f"in the required JSON shape, with status \"found\" and this exact "
        f"generic name. Only use \"unknown_drug\" if you have no reliable "
        f"clinical information at all about this substance.\n\n"
        f"Respond with the JSON object described in your instructions, and "
        f"nothing else."
    )


def build_correction_prompt(previous_error: str) -> str:
    return (
        "Your previous response could not be parsed or did not match the "
        f"required schema. The validation error was:\n{previous_error}\n\n"
        "Return a corrected response: ONLY the JSON object described in your "
        "instructions, with no markdown code fences and no additional text."
    )


def strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1] if "\n" in t else t
        if t.endswith("```"):
            t = t[: -3]
        t = t.strip()
        if t.lower().startswith("json"):
            t = t[4:].strip()
    return t
