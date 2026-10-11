from pathlib import Path
import pandas as pd
import re

profile_path = Path("outputs/metrics/role_skill_frequency.csv")
counts_path = Path("outputs/metrics/role_posting_counts.csv")

profiles = pd.read_csv(profile_path)
posting_counts = pd.read_csv(counts_path)

roles = sorted(profiles["target_role"].dropna().unique())

print("=== FUTUREPATH AI: SKILL GAP ANALYSIS ===")
for number, role in enumerate(roles, start=1):
    print(f"{number}. {role}")

choice = input("\nEnter the number for your target role: ").strip()

if not choice.isdigit() or not 1 <= int(choice) <= len(roles):
    raise SystemExit("Invalid choice. Run the script again and select a listed number.")

role = roles[int(choice) - 1]

resume_input = input(
    "\nEnter skills from your resume, separated by commas:\n"
).strip()

def normalize(skill):
    return re.sub(r"\s+", " ", skill.strip().casefold())

resume_skills = {
    normalize(skill)
    for skill in resume_input.split(",")
    if skill.strip()
}

role_profiles = profiles[profiles["target_role"] == role].copy()
role_profiles = role_profiles[
    role_profiles["percentage_of_postings_with_skills"] >= 10
]
role_profiles = role_profiles.sort_values(
    "posting_count", ascending=False
).head(15)

role_count = posting_counts[posting_counts["target_role"] == role]
usable_count = int(role_count["postings_with_skills"].iloc[0])

role_profiles["status"] = role_profiles["skill"].apply(
    lambda skill: (
        "Present in supplied skills"
        if normalize(skill) in resume_skills
        else "Not detected in supplied skills"
    )
)

role_profiles = role_profiles.rename(columns={
    "skill": "skill",
    "posting_count": "postings_mentioning_skill",
    "percentage_of_postings_with_skills": "posting_percentage",
})

print(f"\n=== RESULTS FOR {role.upper()} ===")
print(f"Postings with usable skill lists: {usable_count}")
print("\nA skill not detected is not proof that you lack it.")
print("Check your resume wording before treating it as a gap.\n")

print(role_profiles[
    ["skill", "posting_percentage", "status"]
].to_string(index=False))

output = Path("outputs/metrics")
output.mkdir(parents=True, exist_ok=True)

safe_role = re.sub(r"[^a-z0-9]+", "_", role.casefold()).strip("_")
report_path = output / f"skill_gap_{safe_role}.csv"

role_profiles.to_csv(report_path, index=False)
print(f"\nReport saved to: {report_path}")
