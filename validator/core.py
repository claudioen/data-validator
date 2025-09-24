import re
from typing import Dict, Any, List
import pandas as pd

# ---- Helpers ---------------------------------------------------------------

def _coerce_series_to_type(s: pd.Series, expected: str) -> pd.Series:
    """
    Try to convert a Series to a given logical type.
    We keep it simple and explicit. If conversion fails, values become NaN.
    """
    if expected == "int":
        return pd.to_numeric(s, errors="coerce").astype("Int64")
    if expected == "float":
        return pd.to_numeric(s, errors="coerce")
    if expected == "string":
        return s.astype("string")
    if expected == "date":
        return pd.to_datetime(s, errors="coerce", utc=False).dt.date
    return s  # unknown type -> no coercion

def _regex_mismatch(val: Any, pattern: re.Pattern) -> bool:
    """Return True if val does not match the regex pattern (and is not null)."""
    if pd.isna(val):
        return False
    return pattern.fullmatch(str(val)) is None

# ---- Core validation -------------------------------------------------------

def validate_data(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply validation rules defined in the YAML config to the DataFrame.

    Config structure example:
    rules:
      - column: age
        type: int
        min: 0
        max: 120
        not_null: true
      - column: email
        regex: "^[^@]+@[^@]+\\.[^@]+$"
      - column: signup_date
        type: date
        min: "2020-01-01"
        max: "2025-01-01"
      - column: user_id
        unique: true
        not_null: true
    """
    errors: List[Dict[str, Any]] = []
    rules: List[Dict[str, Any]] = config.get("rules", [])

    # Work on a copy to avoid side-effects
    df_local = df.copy()

    for rule in rules:
        col = rule.get("column")
        if not col:
            errors.append({"column": "-", "error": "Rule missing 'column' key"})
            continue

        if col not in df_local.columns:
            errors.append({"column": col, "error": "Column not found in dataset"})
            # skip further checks for this column
            continue

        s = df_local[col]

        # 1) Type coercion (optional but very helpful)
        expected_type = rule.get("type")
        if expected_type:
            coerced = _coerce_series_to_type(s, expected_type)
            # Flag type conversion failures (NaN introduced where original wasn't NaN)
            type_fail_mask = coerced.isna() & s.notna()
            for idx in df_local.index[type_fail_mask]:
                errors.append({"row": int(idx), "column": col,
                               "error": f"Type mismatch: expected {expected_type}"})
            s = coerced  # continue checks on coerced data

        # 2) Not null
        if rule.get("not_null"):
            null_idx = s[s.isna()].index
            for idx in null_idx:
                errors.append({"row": int(idx), "column": col, "error": "Null value not allowed"})

        # 3) Unique
        if rule.get("unique"):
            dup_idx = df_local[df_local.duplicated(subset=[col], keep=False)].index
            for idx in dup_idx:
                errors.append({"row": int(idx), "column": col, "error": "Duplicate value found"})

        # 4) Range checks (numeric or date represented as comparable)
        min_v = rule.get("min")
        max_v = rule.get("max")
        if min_v is not None or max_v is not None:
            # Try to compare directly (works for numbers and dates-as-strings after coercion)
            for idx, val in s.items():
                if pd.isna(val):
                    continue
                try:
                    if min_v is not None and val < _maybe_cast(min_v, val):
                        errors.append({"row": int(idx), "column": col,
                                       "error": f"Value {val} below min {min_v}"})
                    if max_v is not None and val > _maybe_cast(max_v, val):
                        errors.append({"row": int(idx), "column": col,
                                       "error": f"Value {val} above max {max_v}"})
                except Exception:
                    errors.append({"row": int(idx), "column": col,
                                   "error": f"Range check failed (incomparable types)"})

        # 5) Regex
        if "regex" in rule:
            pattern = re.compile(rule["regex"])
            for idx, val in s.items():
                if _regex_mismatch(val, pattern):
                    errors.append({"row": int(idx), "column": col, "error": f"Regex mismatch: {val}"})

    # Build summary
    failed_rows = {e["row"] for e in errors if "row" in e}
    return {
        "summary": {
            "rows_checked": int(len(df_local)),
            "rows_failed": int(len(failed_rows)),
            "validation_passed": len(errors) == 0,
        },
        "errors": errors,
    }

def _maybe_cast(boundary, sample_value):
    """
    Cast a boundary value (from YAML string/number) to the sample_value type if needed.
    This keeps comparisons consistent (e.g., date vs string).
    """
    if pd.isna(sample_value):
        return boundary
    # if sample is a date, try to cast boundary to date
    if hasattr(sample_value, "year") and hasattr(sample_value, "month"):
        return pd.to_datetime(boundary, errors="coerce").date()
    # if sample is numeric, cast to float
    if isinstance(sample_value, (int, float)):
        return float(boundary)
    return boundary
