# Data Validator

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://data-validator-vwlkf7tnfla6ru633gtaxn.streamlit.app)


*A small, practical tool to check the quality of tabular data.*  
Works with **CSV**, **JSON** (incl. JSONL), **Parquet**, and **Excel**.  
Rules live in a simple **YAML** file. Run it from the **CLI** or a **Streamlit** UI and get clean **Markdown** and **JSON** reports.

---

## Why this project

I wanted a lightweight validator I could actually use during day-to-day work and also show in a portfolio. Heavy frameworks are great, but sometimes you just want one file in → a few clear checks → one report out. No database, no orchestration, and a config you can read in one glance.

It’s not limited to “customers.” If your data fits in a table, you can validate it: orders, events, products, logs, anything with columns and rows.

---

## What it does (in short)

The app loads your file into a Pandas DataFrame, applies rules from YAML, and writes two reports:
- `report.md` for humans (easy to read and share)
- `report.json` for automation (pipelines, alerts, dashboards)

Built-in checks cover the common cases: basic types (`int`, `float`, `string`, `date`), numeric/date ranges (`min`/`max`), full-match `regex`, `not_null`, and `unique`.

---

## Quick start

### Install
```bash
# (recommended) create and activate a virtual environment first
pip install -r requirements.txt
```

---

## CLI
```bash
python main.py --input examples/customers.csv --config configs/config.yaml --output report_csv
```
This creates `report_csv.md` and `report_csv.json` at the project root.

---

## Streamlit UI
```bash
streamlit run app.py
```
Open the browser, upload a dataset, paste or upload YAML rules, and click Validate.
You can download the reports from the page.

Tip: for larger files, Parquet is faster than CSV.

---

## Configuration
Rules are defined in YAML. Keep it short and explicit.
```yaml
rules:
  - column: user_id
    not_null: true
    unique: true

  - column: age
    type: int
    min: 0
    max: 120
    not_null: true

  - column: email
    regex: '^[^@\s]+@[^@\s]+\.[^@\s]+$'

  - column: signup_date
    type: date
    min: '2020-01-01'
    max: '2025-12-31'
```
### Keys at a glance
- If a column listed in the rules is missing in the file, the run flags it, useful to catch schema drift early.

---

## Supported inputs
- CSV `.csv`
- JSON `.json` (standard arrays and line-delimited JSONL)
- Parquet `.parquet`
- Excel `.xls` / `.xlsx` (requires `openpyxl`)
All inputs are normalized to a DataFrame before validation.

---

## Repository layout
```bash
validator/      # validation engine, loader, report rendering
configs/        # example YAML rules
examples/       # sample datasets
tests/          # pytest
app.py          # Streamlit UI
main.py         # CLI entrypoint
requirements.txt
README.md

```

---

## Use beyond “customers”
Yes. The validator is domain-agnostic. Point it at your dataset and describe the columns you care about. You can validate orders, transactions, product catalogs, event logs, etc. The same rules format applies.

---

## Testing
```bash
pytest -q
```
Tests focus on the validation engine, so you can evolve the UI without touching the core.

---

## Extend when needed
Keep the core small and grow where it helps:
- new checks (e.g., allowed values, cross-column comparisons) → `validator/core.py`
- more data sources (APIs, databases) → `validator/loader.py`
- alerts or orchestration around the CLI (Slack/email, Airflow)
- a small dashboard to track runs over time

---

## License
MIT — see the `LICENSE` file.
