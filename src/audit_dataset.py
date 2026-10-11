import pandas as pd
import json
from pathlib import Path

DATA = Path("data/raw/nextgig_jobs_2026-06.parquet")
OUT = Path("outputs/metrics")
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA)

print("=== DATA QUALITY AUDIT ===")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Exact duplicate rows:", int(df.duplicated().sum()))

print("\n=== MISSING VALUES ===")
missing = df.isna().sum().sort_values(ascending=False)
missing_report = pd.DataFrame({
    "missing_count": missing,
    "missing_percent": (missing / len(df) * 100).round(2)
})
print(missing_report.to_string())
missing_report.to_csv(OUT / "missing_values.csv")

print("\n=== COUNTRY COVERAGE ===")
print("Non-missing country values:", int(df["country"].notna().sum()))
print("Unique country values:", int(df["country"].nunique()))
print(df["country"].value_counts().head(15).to_string())

print("\n=== POSTING DATE COVERAGE ===")
dates = pd.to_datetime(df["date_posted"], errors="coerce", utc=True)
print("Valid posting dates:", int(dates.notna().sum()))
print("Missing or unparseable dates:", int(dates.isna().sum()))
print("Earliest parsed date:", dates.min())
print("Latest parsed date:", dates.max())

print("\n=== SKILLS AND SALARIES ===")
skills = df["skills_required"].fillna("").astype(str).str.strip()
print("Non-empty skills fields:", int(skills.ne("").sum()))
print("Salary minimum available:", int(df["salary_min"].notna().sum()))
print("Salary maximum available:", int(df["salary_max"].notna().sum()))
print("Distinct salary currencies:", int(df["salary_currency"].nunique()))

summary = {
    "rows": len(df),
    "columns": len(df.columns),
    "exact_duplicate_rows": int(df.duplicated().sum()),
    "unique_country_values": int(df["country"].nunique()),
    "valid_posting_dates": int(dates.notna().sum()),
    "earliest_posting_date": str(dates.min()),
    "latest_posting_date": str(dates.max()),
    "nonempty_skills_fields": int(skills.ne("").sum()),
    "salary_min_available": int(df["salary_min"].notna().sum()),
    "salary_max_available": int(df["salary_max"].notna().sum()),
}
with open(OUT / "dataset_audit_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\nAudit files saved in outputs/metrics/")
