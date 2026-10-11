from pathlib import Path
import pandas as pd

path = Path("data/raw/nextgig_jobs_2026-06.parquet")
df = pd.read_parquet(path)

print("Total postings:", len(df))

for column in ["normalized_title", "title"]:
    if column not in df.columns:
        continue

    print(f"\n=== MATCHING JOB TITLES: {column} ===")

    mask = df[column].astype("string").str.contains(
        r"analyst|business intelligence|operations research",
        case=False,
        na=False,
        regex=True,
    )

    matches = df.loc[mask, column].value_counts().head(35)
    print(matches.to_string() if not matches.empty else "No matching titles.")

print("\n=== SAMPLE SKILL RECORDS ===")
column = "skills_required"
valid = df[column].notna() & df[column].astype(str).str.strip().ne("")

print(df.loc[valid, ["title", "normalized_title", column]]
      .head(5).to_string(index=False))

print("\nInspection complete.")
