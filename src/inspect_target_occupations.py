from pathlib import Path
import pandas as pd

raw = Path("data/raw/onet")

occupations = pd.read_csv(raw / "occupation_data.csv")
software = pd.read_csv(raw / "software_skills.csv")
essential = pd.read_csv(raw / "essential_skills.csv")

matches = occupations[
    occupations["Title"].str.contains(
        r"data analyst|business intelligence analyst|operations research analyst",
        case=False,
        na=False,
        regex=True,
    )
]

print("=== MATCHING OCCUPATIONS ===")
if matches.empty:
    print("No matching occupation titles found.")
else:
    print(matches[["O*NET-SOC Code", "Title"]].to_string(index=False))

    codes = set(matches["O*NET-SOC Code"])

    print("\n=== SOFTWARE SKILLS FOR MATCHING OCCUPATIONS ===")
    selected = software[software["O*NET-SOC Code"].isin(codes)]
    columns = [
        "Title",
        "Workplace Example",
        "Hot Technology",
        "In Demand",
    ]
    print(selected[columns].drop_duplicates().head(25).to_string(index=False))

    print("\n=== ESSENTIAL SKILL RECORDS ===")
    selected_essential = essential[
        essential["O*NET-SOC Code"].isin(codes)
        & essential["Scale ID"].astype(str).str.strip().eq("IM")
    ]
    columns = ["Title", "Element Name", "Data Value", "Scale Name"]
    print(selected_essential[columns].to_string(index=False))

print("\nCheck complete.")
