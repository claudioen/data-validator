import argparse
import yaml
from validator.loader import load_data
from validator.core import validate_data
from validator.report import generate_reports

def main():
    """
    Simple CLI for the data validator.
    Example:
      python main.py --input examples/customers.csv --config configs/config.yaml --output report
    """
    parser = argparse.ArgumentParser(description="Lightweight Data Validation Tool")
    parser.add_argument("--input", required=True, help="Path to dataset (CSV, JSON, Parquet, Excel)")
    parser.add_argument("--config", required=True, help="Path to YAML config with validation rules")
    parser.add_argument("--output", default="validation_report", help="Output file prefix (no extension)")
    args = parser.parse_args()

    # Load config
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # Load data as Pandas DataFrame
    df = load_data(args.input)

    # Run validations
    results = validate_data(df, config)

    # Write reports (JSON + Markdown)
    generate_reports(results, args.output)

    print(f"✅ Validation completed. Reports saved as {args.output}.json and {args.output}.md")

if __name__ == "__main__":
    main()
