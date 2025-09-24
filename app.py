import io
import yaml
import pandas as pd
import streamlit as st

from validator.loader import load_data
from validator.core import validate_data
from validator.report import render_markdown, render_json

st.set_page_config(page_title="Data Validator", page_icon="🤖", layout="wide")

# ---- Sidebar ---------------------------------------------------------------
st.sidebar.title("⚙️ Configuration")

st.sidebar.markdown("Upload a **dataset** and a **YAML config** with rules, then click **Validate**.")

data_file = st.sidebar.file_uploader(
    "Dataset file (CSV / JSON / Parquet / Excel)",
    type=["csv", "json", "parquet", "xls", "xlsx"],
    accept_multiple_files=False
)

config_source = st.sidebar.radio(
    "Config source",
    ["Upload YAML", "Paste YAML"],
    index=0
)

config_bytes = None
config_text = None
default_yaml = """\
rules:
  - column: user_id
    not_null: true
    unique: true
  - column: age
    type: int
    min: 0
    max: 120
  - column: email
    regex: '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'
  - column: signup_date
    type: date
    min: '2020-01-01'
    max: '2025-12-31'
"""

if config_source == "Upload YAML":
    config_file = st.sidebar.file_uploader("YAML rules", type=["yaml", "yml"], accept_multiple_files=False)
    if config_file is not None:
        config_bytes = config_file.read()
else:
    config_text = st.sidebar.text_area("YAML rules", value=default_yaml, height=220)

run_btn = st.sidebar.button("✅ Validate", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Tip: large files? Prefer Parquet for speed.")

# ---- Main area -------------------------------------------------------------
st.title("Data Validator")
st.caption("Lightweight data quality checks for CSV/JSON/Parquet/Excel using YAML rules.")

# Data preview container
data_tab, result_tab = st.tabs(["📄 Data Preview", "📊 Validation Result"])

@st.cache_data(show_spinner=False)
def _load_df_from_upload(uploaded) -> pd.DataFrame:
    """
    Load the uploaded file into a DataFrame.
    We write it to a temporary buffer when needed for loader compatibility.
    """
    # streamlit's UploadedFile has .name and .read(). For parquet/excel we need a bytes buffer.
    name = uploaded.name
    suffix = name.split(".")[-1].lower()

    # CSV and JSON can be read directly by pandas via BytesIO/StringIO.
    # But we already have a universal loader; we emulate a path using buffer.
    # We'll choose a path-like hint via the suffix.
    data = uploaded.read()
    buf = io.BytesIO(data)

    if suffix == "csv":
        return pd.read_csv(buf)
    elif suffix == "json":
        try:
            return pd.read_json(buf)
        except ValueError:
            buf.seek(0)
            return pd.read_json(buf, lines=True)
    elif suffix == "parquet":
        buf.seek(0)
        return pd.read_parquet(buf)
    elif suffix in ("xls", "xlsx"):
        buf.seek(0)
        return pd.read_excel(buf)
    else:
        raise ValueError(f"Unsupported file: {name}")

with data_tab:
    if data_file is not None:
        try:
            df_preview = _load_df_from_upload(data_file)
            st.success(f"Loaded dataset with **{len(df_preview)}** rows and **{len(df_preview.columns)}** columns.")
            st.dataframe(df_preview.head(100), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load dataset: {e}")
    else:
        st.info("Upload a dataset in the sidebar to preview it here.")

with result_tab:
    if run_btn:
        # Parse YAML
        try:
            if config_bytes is not None:
                config = yaml.safe_load(config_bytes.decode("utf-8")) or {}
            else:
                config = yaml.safe_load(config_text) or {}
        except Exception as e:
            st.error(f"Invalid YAML: {e}")
            st.stop()

        # Load DataFrame (from uploaded file preview if available)
        if data_file is None:
            st.warning("Please upload a dataset.")
            st.stop()

        try:
            df = _load_df_from_upload(data_file)
        except Exception as e:
            st.error(f"Failed to load dataset: {e}")
            st.stop()

        # Validate
        with st.spinner("Running validations..."):
            results = validate_data(df, config)

        # Summary
        s = results["summary"]
        cols = st.columns(3)
        cols[0].metric("Rows checked", s["rows_checked"])
        cols[1].metric("Rows failed", s["rows_failed"])
        cols[2].metric("Validation passed", "✅ Yes" if s["validation_passed"] else "❌ No")

        st.markdown("### Errors")
        if results["errors"]:
            err_df = pd.DataFrame(results["errors"])
            st.dataframe(err_df, use_container_width=True, height=380)
        else:
            st.success("No errors 🎉")

        # Downloads
        st.markdown("### Download Reports")
        md_str = render_markdown(results)
        json_str = render_json(results)

        st.download_button(
            label="Download Markdown (.md)",
            data=md_str.encode("utf-8"),
            file_name="validation_report.md",
            mime="text/markdown",
            use_container_width=True
        )

        st.download_button(
            label="Download JSON (.json)",
            data=json_str.encode("utf-8"),
            file_name="validation_report.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.info("Configure and click **Validate** to see results.")
