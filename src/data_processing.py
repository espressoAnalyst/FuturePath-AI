
from pathlib import Path
import pandas as pd


def audit_csv(file_path):
    """Inspect a CSV dataset and return basic quality statistics."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path, low_memory=False)

    missing = df.isna().sum()

    missing_percent = (
        (missing / len(df) * 100).round(2)
        if len(df)
        else missing
    )

    summary = {
        "file_name": file_path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "total_missing_cells": int(df.isna().sum().sum()),
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / (1024 ** 2), 2
        ),
    }

    column_report = pd.DataFrame({
        "column": df.columns,
        "data_type": df.dtypes.astype(str).values,
        "missing_count": missing.values,
        "missing_percent": missing_percent.values,
        "unique_values": [
            df[column].nunique(dropna=True)
            for column in df.columns
        ],
    })

    return df, summary, column_report
