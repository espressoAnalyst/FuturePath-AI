
import re
import pandas as pd


def normalize_skill(value, aliases):
    skill = re.sub(r"\s+", " ", str(value).strip().casefold())
    return aliases.get(skill, skill)


def recommend_roles(
    profiles,
    detected_skills,
    aliases,
    min_frequency=10,
    max_skills=15,
):
    required_columns = {
        "target_role",
        "skill",
        "posting_count",
        "percentage_of_postings_with_skills",
    }
    if not required_columns.issubset(profiles.columns):
        raise ValueError("Role-skill profile is missing required columns.")

    user_skills = {
        normalize_skill(skill, aliases)
        for skill in detected_skills
        if str(skill).strip()
    }

    data = profiles.copy()
    data["normalized_skill"] = data["skill"].map(
        lambda skill: normalize_skill(skill, aliases)
    )
    data["posting_count"] = pd.to_numeric(
        data["posting_count"], errors="coerce"
    ).fillna(0)
    data["percentage_of_postings_with_skills"] = pd.to_numeric(
        data["percentage_of_postings_with_skills"], errors="coerce"
    )

    data = data[
        data["normalized_skill"].ne("")
        & data["percentage_of_postings_with_skills"].ge(min_frequency)
    ]

    # Merge alias duplicates without double-counting a skill.
    data = (
        data.sort_values(
            ["posting_count", "percentage_of_postings_with_skills"],
            ascending=False,
        )
        .drop_duplicates(["target_role", "normalized_skill"])
    )

    results = []

    for role, group in data.groupby("target_role"):
        group = group.head(max_skills)
        required = group["normalized_skill"].tolist()

        if not required:
            continue

        matched = [skill for skill in required if skill in user_skills]
        missing = [skill for skill in required if skill not in user_skills]
        total = len(required)

        results.append({
            "target_role": role,
            "role_fit_score": round(len(matched) / total * 100, 1),
            "matched_count": len(matched),
            "skills_used": total,
            "missing_count": len(missing),
            "matched_skills": matched,
            "missing_skills": missing,
        })

    return pd.DataFrame(results).sort_values(
        ["role_fit_score", "matched_count", "skills_used"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
