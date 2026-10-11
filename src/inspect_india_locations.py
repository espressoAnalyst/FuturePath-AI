import pandas as pd

path = "data/raw/nextgig_jobs_2026-06.parquet"
df = pd.read_parquet(path)

print("\n--- LOCATION-RELATED COLUMNS ---")
cols = [
    c for c in df.columns
    if any(word in c.lower() for word in
           ["country", "location", "city", "state", "region"])
]
print(cols)

for col in cols:
    print(f"\n--- {col}: top recorded values ---")
    print(df[col].dropna().astype(str).value_counts().head(15))

country_col = next(
    (c for c in df.columns if c.lower() == "country"), None
)

if country_col:
    india_mask = (
        df[country_col].astype(str).str.strip().str.lower()
        .isin(["india", "in"])
    )
    india = df[india_mask]

    print("\n--- INDIA COVERAGE ---")
    print("Matching rows:", len(india))

    for col in cols:
        print(f"\n--- India rows: {col} ---")
        print(india[col].dropna().astype(str).value_counts().head(20))
else:
    print("\nNo exact 'country' column found; inspect the columns above.")
