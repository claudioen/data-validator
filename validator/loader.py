import pandas as pd
import os

def load_data(path: str) -> pd.DataFrame:
    """
    Load dataset from different formats into a Pandas DataFrame.
    Supported: CSV (.csv), JSON (.json), Parquet (.parquet), Excel (.xls/.xlsx).
    The goal is to normalize all inputs to a DataFrame for a single validation path.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        # Adjust separators/encodings here if needed
        return pd.read_csv(path)
    elif ext == ".json":
        # If your JSON is line-delimited (JSONL), use lines=True
        try:
            return pd.read_json(path)
        except ValueError:
            return pd.read_json(path, lines=True)
    elif ext == ".parquet":
        return pd.read_parquet(path)
    elif ext in (".xls", ".xlsx"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"❌ Unsupported file format: {ext}")
