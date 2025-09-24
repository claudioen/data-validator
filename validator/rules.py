"""
Rules utilities (placeholder for future growth).

In a real project, you could:
- Validate the YAML schema itself (types of keys, allowed fields).
- Provide reusable rule templates or presets.
- Compile rules to faster callables if performance is key.
"""

ALLOWED_TYPES = {"int", "float", "string", "date"}

def validate_rule_schema(rule: dict) -> bool:
    """
    Very light schema check. Extend as needed.
    """
    if "column" not in rule:
        return False
    t = rule.get("type")
    if t and t not in ALLOWED_TYPES:
        return False
    return True
