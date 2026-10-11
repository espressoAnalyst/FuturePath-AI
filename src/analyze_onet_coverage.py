from pathlib import Path
import json
import pandas as pd

RAW = Path("data/raw/onet")
OUT = Path("outputs/metrics/onet")
REPORTS = Path("research/dataset_reports/onet")

OUT.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

files = {
    "occupations": "occupation_data.csv",
    "essential_skills": "essential_skills.csv",
    "software_skills": "software_skills.csv",
}

data = {
    name: pd.read_csv(RAW / filename, encoding="utf-8-sig", low_memory=False)
    for name, filename in files.items()
}

occupations = data["occupations"]
essential = data["essential_skills"]
software = data["software_skills"]

code_col = "O*NET-SOC Code"

occupation_codes = set(occupations[code_col].dropna().astype(str))
essential_codes = set(essential[code_col].dropna().astype(str))
software_codes = set(software[code_col].dropna().astype(str))

summary = {
    "source": "O*NET Database",
    "files": {},
    "relationships": {
        "unique_occupation_codes": len(occupation_codes),
        "codes_in_essential_skills": len(essential_codes),
        "essential_codes_matching_occupation_data": len(
            essential_codes & occupation_codes
        ),
        "codes_in_software_skills": len(software_codes),
        "software_codes_matching_occupation_data": len(
            software_codes & occupation_codes
        ),
    },
}

for name, df in data.items():
    summary["files"][name] = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
    }

# Summarize essential skills using Importance ratings only.
importance = essential[
    essential["Scale ID"].astype(str).str.strip().eq("IM")
].copy()

importance["Data Value"] = pd.to_numeric(
    importance["Data Value"], errors="coerce"
)

essential_summary = (
    importance.dropna(subset=["Data Value"])
    .groupby("Element Name")
    .agg(
        occupation_records=("O*NET-SOC Code", "nunique"),
        mean_importance=("Data Value", "mean"),
    )
    .reset_index()
    .sort_values("mean_importance", ascending=False)
)

essential_summary["mean_importance"] = essential_summary[
    "mean_importance"
].round(3)

essential_summary.to_csv(
    OUT / "essential_skill_importance_summary.csv", index=False
)

# Count software examples and preserve source flags.
software["Hot Technology"] = (
    software["Hot Technology"].astype("string").str.strip().str.upper()
)
software["In Demand"] = (
    software["In Demand"].astype("string").str.strip().str.upper()
)

software_summary = (
    software.groupby("Workplace Example", dropna=False)
    .agg(
        occupation_records=("O*NET-SOC Code", "nunique"),
        hot_technology_records=(
            "Hot Technology", lambda s: int(s.eq("Y").sum())
        ),
        in_demand_records=("In Demand", lambda s: int(s.eq("Y").sum())),
    )
    .reset_index()
    .sort_values(
        ["in_demand_records", "occupation_records"],
        ascending=False,
    )
)

software_summary.to_csv(
    OUT / "software_skill_summary.csv", index=False
)

summary["essential_skills_importance_rows"] = int(len(importance))
summary["essential_skill_names"] = int(
    essential["Element Name"].nunique()
)
summary["software_examples"] = int(
    software["Workplace Example"].nunique()
)
summary["hot_technology_yes_rows"] = int(
    software["Hot Technology"].eq("Y").sum()
)
summary["in_demand_yes_rows"] = int(
    software["In Demand"].eq("Y").sum()
)

with open(OUT / "onet_audit_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

report = [
    "# O*NET Dataset Inspection Report",
    "",
    "## Purpose",
    "Inspect O*NET occupation and skill tables for potential use in FuturePath AI.",
    "",
    "## Dataset summary",
]

for name, details in summary["files"].items():
    report.extend([
        f"### {name}",
        f"- Rows: {details['rows']}",
        f"- Columns: {details['columns']}",
        f"- Exact duplicate rows: {details['duplicate_rows']}",
        f"- Missing cells: {details['missing_cells']}",
        f"- Columns: {', '.join(details['column_names'])}",
        "",
    ])

report.extend([
    "## Occupation-code linkage",
    f"- Unique occupation codes: {summary['relationships']['unique_occupation_codes']}",
    f"- Essential-skills codes matching occupation data: {summary['relationships']['essential_codes_matching_occupation_data']}",
    f"- Software-skills codes matching occupation data: {summary['relationships']['software_codes_matching_occupation_data']}",
    "",
    "## Essential skill importance",
    "The summary averages rows whose Scale ID is IM (Importance). "
    "It is descriptive of this O*NET release, not a measure of current job-posting demand.",
    "",
    "## Software skill flags",
    "Hot Technology and In Demand counts preserve the source-provided flags. "
    "They should not be interpreted as live or India-specific demand.",
    "",
    "## Limitations",
    "- O*NET primarily describes US occupations.",
    "- Occupation-code matching does not guarantee identical coverage in all tables.",
    "- A missing value does not mean a skill or attribute is absent in reality.",
    "- O*NET skills and job-posting skills use different taxonomies and may need careful mapping.",
    "",
    "## Generated outputs",
    "- outputs/metrics/onet/onet_audit_summary.json",
    "- outputs/metrics/onet/essential_skill_importance_summary.csv",
    "- outputs/metrics/onet/software_skill_summary.csv",
])

(REPORTS / "onet_inspection_report.md").write_text(
    "\n".join(report), encoding="utf-8"
)

print("=== O*NET ANALYSIS COMPLETE ===")
print(json.dumps(summary["relationships"], indent=2))
print("\nEssential skill names:", summary["essential_skill_names"])
print("Importance rows analysed:", summary["essential_skills_importance_rows"])
print("Distinct software examples:", summary["software_examples"])
print("Hot Technology = Y rows:", summary["hot_technology_yes_rows"])
print("In Demand = Y rows:", summary["in_demand_yes_rows"])
print("\nTop 10 essential skills by mean Importance:")
print(essential_summary.head(10).to_string(index=False))
print("\nSaved outputs:")
print(OUT / "onet_audit_summary.json")
print(OUT / "essential_skill_importance_summary.csv")
print(OUT / "software_skill_summary.csv")
print(REPORTS / "onet_inspection_report.md")
