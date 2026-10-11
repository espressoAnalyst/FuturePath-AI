from pathlib import Path
import pandas as pd

folder = Path("data/raw/onet")

for filename in [
    "occupation_data.csv",
    "essential_skills.csv",
    "software_skills.csv",
]:
    path = folder / filename
    print(f"\n{'=' * 60}")
    print("FILE:", filename)

    if not path.exists():
        print("ERROR: File not found.")
        continue

    try:
        df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp1252", low_memory=False)

    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Column names:", df.columns.tolist())
    print("\nFirst 3 rows:")
    print(df.head(3).to_string(index=False))
    print("\nMost-missing columns:")
    print(df.isna().sum().sort_values(ascending=False).head(5).to_string())

    if df.empty:
        print("WARNING: File contains no data rows.")

print("\nFile verification finished.")
