from pathlib import Path
import ast
import re
import pandas as pd

source = Path("data/raw/nextgig_jobs_2026-06.parquet")
output = Path("outputs/metrics")
output.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(source)

def parse_skills(value):
    if not isinstance(value, str) or not value.strip():
        return []

    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []

    if not isinstance(parsed, list):
        return []

    return [
        re.sub(r"\s+", " ", skill.strip()).casefold()
        for skill in parsed
        if isinstance(skill, str) and skill.strip()
    ]

df["parsed_skills"] = df["skills_required"].apply(parse_skills)

roles = {
    "Data Analyst": r"\bdata analyst\b",
    "Business Analyst": r"\bbusiness analyst\b",
    "Financial Analyst": r"\bfinancial analyst\b",
    "Business Intelligence Analyst": r"\bbusiness intelligence analyst\b",
    "Operations Analyst": r"\boperations analyst\b",
}

profile_rows = []
posting_rows = []

for role, pattern in roles.items():
    mask = df["normalized_title"].astype("string").str.contains(
        pattern, case=False, na=False, regex=True
    )

    role_df = df.loc[mask].copy()
    usable = role_df[role_df["parsed_skills"].map(bool)].copy()

    posting_rows.append({
        "target_role": role,
        "matched_postings": len(role_df),
        "postings_with_skills": len(usable),
    })

    counts = {}

    for skills in usable["parsed_skills"]:
        for skill in set(skills):
            counts[skill] = counts.get(skill, 0) + 1

    for skill, count in counts.items():
        profile_rows.append({
            "target_role": role,
            "skill": skill,
            "posting_count": count,
            "percentage_of_postings_with_skills": round(
                count / len(usable) * 100, 2
            ) if len(usable) else 0,
        })

profiles = pd.DataFrame(profile_rows)
posting_summary = pd.DataFrame(posting_rows)

profiles.to_csv(output / "role_skill_frequency.csv", index=False)
posting_summary.to_csv(output / "role_posting_counts.csv", index=False)

print("=== ROLE POSTING COUNTS ===")
print(posting_summary.to_string(index=False))

print("\n=== TOP SKILLS BY ROLE ===")
for role in roles:
    selected = profiles[profiles["target_role"] == role]
    selected = selected.sort_values("posting_count", ascending=False).head(10)

    print(f"\n{role}")
    if selected.empty:
        print("No usable skill records found.")
    else:
        print(selected[
            ["skill", "posting_count", "percentage_of_postings_with_skills"]
        ].to_string(index=False))

print("\nSaved:")
print(output / "role_skill_frequency.csv")
print(output / "role_posting_counts.csv")
