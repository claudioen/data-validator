import json
from typing import Dict

def generate_reports(results: Dict, output_prefix: str) -> None:
    """
    Save validation results as JSON and Markdown.
    Keep reports human-friendly and portfolio-friendly.
    """
    with open(f"{output_prefix}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(f"{output_prefix}.md", "w", encoding="utf-8") as f:
        f.write(render_markdown(results))

def render_markdown(results: Dict) -> str:
    """Return a Markdown string for Streamlit (or other UIs)."""
    lines = []
    lines.append("# Data Validation Report\n")
    lines.append(f"- **Rows checked:** {results['summary']['rows_checked']}")
    lines.append(f"- **Rows failed:** {results['summary']['rows_failed']}")
    lines.append(f"- **Validation passed:** {results['summary']['validation_passed']}\n")
    if results["errors"]:
        lines.append("## Errors")
        for e in results["errors"]:
            row = e.get("row", "-")
            col = e.get("column", "-")
            msg = e.get("error", "-")
            lines.append(f"- Row `{row}`, Column `{col}` → {msg}")
    else:
        lines.append("No errors 🎉")
    return "\n".join(lines)

def render_json(results: Dict) -> str:
    """Return a pretty JSON string."""
    return json.dumps(results, indent=2, ensure_ascii=False)
