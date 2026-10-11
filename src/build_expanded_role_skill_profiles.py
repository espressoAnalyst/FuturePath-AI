from pathlib import Path
import ast
import re
import pandas as pd

SOURCE = Path("data/raw/nextgig_jobs_2026-06.parquet")
OUTPUT = Path("outputs/metrics/expanded")
OUTPUT.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(SOURCE)

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
titles = df["normalized_title"].astype("string")

roles = {
    "Data Analyst": r"\bdata analyst\b",
    "Business Analyst": r"\bbusiness analyst\b",
    "Business Intelligence Analyst": r"\bbusiness intelligence analyst\b",
    "Financial Analyst": r"\bfinancial analyst\b",
    "Operations Analyst": r"\boperations analyst\b",
    "Data Engineer": r"\bdata engineer\b",
    "Data Scientist": r"\bdata scientist\b",
    "Machine Learning Engineer": r"\bmachine learning engineer\b|\bml engineer\b",
    "Software Engineer": r"\bsoftware engineer\b",
    "Software Developer": r"\bsoftware developer\b",
    "Full Stack Developer": r"\bfull[ -]?stack (?:developer|engineer)\b",
    "Frontend Developer": r"\bfront[ -]?end (?:developer|engineer)\b",
    "Backend Developer": r"\bback[ -]?end (?:developer|engineer)\b",
    "QA Engineer": r"\bqa engineer\b|\bquality assurance engineer\b",
    "Cybersecurity Analyst": r"\bcybersecurity analyst\b|\binformation security analyst\b",
    "Cloud Engineer": r"\bcloud engineer\b",
    "Product Manager": r"\bproduct manager\b",
    "Project Manager": r"\bproject manager\b",
    "HR Analyst": r"\bhr analyst\b|\bhuman resources analyst\b",
    "Marketing Analyst": r"\bmarketing analyst\b",
    "Accountant": r"\baccountant\b",
}

profile_rows = []
posting_rows = []

for role, pattern in roles.items():
    matched = df.loc[
        titles.str.contains(pattern, case=False, na=False, regex=True)
    ]
    usable = matched.loc[matched["parsed_skills"].map(bool)]

    posting_rows.append({
        "target_role": role,
        "matched_postings": len(matched),
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

profiles = pd.DataFrame(
    profile_rows,
    columns=[
        "target_role", "skill", "posting_count",
        "percentage_of_postings_with_skills"
    ]
)
summary = pd.DataFrame(posting_rows)

profiles.to_csv(OUTPUT / "role_skill_frequency_expanded.csv", index=False)
summary.to_csv(OUTPUT / "role_posting_counts_expanded.csv", index=False)

print("=== EXPANDED GLOBAL ROLE COVERAGE ===")
print(summary.sort_values(
    "postings_with_skills", ascending=False
).to_string(index=False))

print("\n=== TOP 5 SKILLS FOR EACH ROLE ===")
for role in roles:
    selected = profiles[profiles["target_role"] == role]
    selected = selected.sort_values("posting_count", ascending=False).head(5)
    print(f"\n{role}")
    if selected.empty:
        print("No usable skill records.")
    else:
        print(selected[
            ["skill", "posting_count",
             "percentage_of_postings_with_skills"]
        ].to_string(index=False))

print("\nSaved files:")
print(OUTPUT / "role_skill_frequency_expanded.csv")
print(OUTPUT / "role_posting_counts_expanded.csv")
