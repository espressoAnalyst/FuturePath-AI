import json
from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px

DATA = Path("data/raw/nextgig_jobs_2026-06.parquet")
OUT = Path("outputs/metrics")
FIGURES = Path("outputs/figures")

OUT.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA)

skill_counts = Counter()
valid_postings = 0
invalid_skill_fields = 0

for value in df["skills_required"]:
    if pd.isna(value) or not str(value).strip():
        continue

    try:
        parsed = json.loads(value)
        if not isinstance(parsed, list):
            invalid_skill_fields += 1
            continue
    except (json.JSONDecodeError, TypeError):
        invalid_skill_fields += 1
        continue

    # Count each normalized skill once per posting.
    posting_skills = set()
    for skill in parsed:
        if isinstance(skill, str) and skill.strip():
            normalized = " ".join(skill.split()).casefold()
            posting_skills.add(normalized)

    if posting_skills:
        valid_postings += 1
        skill_counts.update(posting_skills)

# Build a reproducible frequency table.
results = pd.DataFrame(
    skill_counts.most_common(),
    columns=["skill_normalized", "posting_count"]
)

results["percent_of_skill_postings"] = (
    results["posting_count"] / valid_postings * 100
).round(2)

results.to_csv(OUT / "skill_frequency.csv", index=False)

top = results.head(20).sort_values("posting_count")

fig = px.bar(
    top,
    x="posting_count",
    y="skill_normalized",
    orientation="h",
    title="Top 20 Skills by Job-Posting Frequency",
    labels={
        "posting_count": "Number of postings listing the skill",
        "skill_normalized": "Skill"
    }
)

fig.update_layout(
    template="plotly_white",
    yaxis_title="",
    xaxis_title="Number of job postings",
    height=700
)

fig.write_html(str(FIGURES / "top_skills.html"))

print("=== SKILL FREQUENCY ANALYSIS ===")
print("Total job postings:", len(df))
print("Postings with at least one parsed skill:", valid_postings)
print("Invalid or non-list skill fields:", invalid_skill_fields)
print("Distinct normalized skills:", len(results))
print("\n=== TOP 20 SKILLS ===")
print(results.head(20).to_string(index=False))
print("\nSaved: outputs/metrics/skill_frequency.csv")
print("Saved: outputs/figures/top_skills.html")
print("\nNote: frequencies describe this dataset, not the entire labor market.")
