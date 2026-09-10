from __future__ import annotations

# Parameters where an INCREASING trend is the concerning direction vs. DECREASING.
INCREASING_IS_CONCERNING = {"creatinine", "ast", "alt", "bilirubin", "potassium", "inr"}
DECREASING_IS_CONCERNING = {"hemoglobin", "platelets", "wbc", "egfr", "sodium"}

# Minimum relative change (fraction) considered "clinically significant" for
# a generic trend flag. This is a coarse heuristic for demo purposes, not a
# substitute for parameter-specific clinical thresholds.
SIGNIFICANT_RELATIVE_CHANGE = 0.20


def analyze_lab_trend(parameter: str, points: list[dict]) -> dict:
    if len(points) < 2:
        return {
            "parameter": parameter,
            "trend": "Insufficient data",
            "clinically_significant_change": False,
            "note": "At least two data points are needed to assess a trend.",
        }

    sorted_points = sorted(points, key=lambda p: p["day"])
    first, last = sorted_points[0]["value"], sorted_points[-1]["value"]

    if first == 0:
        rel_change = float("inf") if last != 0 else 0.0
    else:
        rel_change = (last - first) / abs(first)

    if last > first * 1.02:
        trend = "Increasing"
    elif last < first * 0.98:
        trend = "Decreasing"
    else:
        trend = "Stable"

    param_lower = parameter.lower()
    concerning = (
        (trend == "Increasing" and param_lower in INCREASING_IS_CONCERNING)
        or (trend == "Decreasing" and param_lower in DECREASING_IS_CONCERNING)
    )
    significant = abs(rel_change) >= SIGNIFICANT_RELATIVE_CHANGE and concerning

    note = "Potential concern detected — clinical correlation required." if significant else \
           "No clinically significant concerning trend detected based on the values provided; continue routine monitoring."

    return {
        "parameter": parameter,
        "trend": trend,
        "clinically_significant_change": significant,
        "note": note,
    }
