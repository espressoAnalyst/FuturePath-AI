import pandas as pd

path = "data/raw/nextgig_jobs_2026-06.parquet"
df = pd.read_parquet(path)

for column in ["industry", "function", "occupational_category"]:
    values = df[column].astype("string").str.strip()
    values = values[values.notna() & values.ne("")]

    print(f"\n=== {column.upper()} ===")
    print("Non-empty records:", len(values))
    print("Distinct labels:", values.nunique())
    print("\nMost common labels:")
    print(values.value_counts().head(15).to_string())

print("\n=== COUNTRY LABELS ===")
country = df["country"].astype("string").str.strip()
country = country[country.notna() & country.ne("")]
print("Distinct raw country labels:", country.nunique())
print(country.value_counts().head(25).to_string())

print("\n=== INDIA LABEL CHECK ===")
india_labels = country[
    country.str.contains(r"\bindia\b", case=False, na=False)
]
print("India-containing labels and counts:")
print(india_labels.value_counts().to_string())
