from pathlib import Path

import pandas as pd
import plotly.express as px

DATA = Path("data/raw/nextgig_jobs_2026-06.parquet")
OUT = Path("outputs/metrics")
FIGURES = Path("outputs/figures")

OUT.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA)

# Keep original labels; do not guess missing industries.
industry = df["industry"].astype("string").str.strip()
industry = industry[industry.notna() & industry.ne("")]

function = df["function"].astype("string").str.strip()
function = function[function.notna() & function.ne("")]

industry_counts = industry.value_counts().rename_axis(
    "industry_label"
).reset_index(name="posting_count")

industry_counts["percent_of_all_postings"] = (
    industry_counts["posting_count"] / len(df) * 100
).round(3)

function_counts = function.value_counts().rename_axis(
    "function_label"
).reset_index(name="posting_count")

function_counts["percent_of_all_postings"] = (
    function_counts["posting_count"] / len(df) * 100
).round(3)

industry_counts.to_csv(OUT / "industry_frequency.csv", index=False)
function_counts.to_csv(OUT / "function_frequency.csv", index=False)

top = industry_counts.head(15).sort_values("posting_count")

fig = px.bar(
    top,
    x="posting_count",
    y="industry_label",
    orientation="h",
    title="Most Frequent Recorded Industry Labels",
    labels={
        "posting_count": "Number of postings",
        "industry_label": "Recorded industry"
    }
)

fig.update_layout(
    template="plotly_white",
    yaxis_title="",
    xaxis_title="Number of postings",
    height=600
)

fig.write_html(str(FIGURES / "industry_frequency.html"))

print("=== SECTOR ANALYSIS OUTPUT ===")
print("Total postings:", len(df))
print("Postings with industry labels:", len(industry))
print("Industry-label coverage (%):", round(len(industry) / len(df) * 100, 2))
print("Postings with function labels:", len(function))
print("\n=== TOP 15 RECORDED INDUSTRIES ===")
print(industry_counts.head(15).to_string(index=False))
print("\nSaved: outputs/metrics/industry_frequency.csv")
print("Saved: outputs/metrics/function_frequency.csv")
print("Saved: outputs/figures/industry_frequency.html")
