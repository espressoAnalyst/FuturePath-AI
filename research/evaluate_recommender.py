import os
import json
import math
from collections import Counter
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from career_recommender import recommend_roles, normalize_skill


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/nextgig_jobs_2026-06.parquet"
RANDOM_SEED = int(os.environ.get("FUTUREPATH_SEED", "42"))
OUTPUT_DIR = ROOT / "outputs" / "evaluation" / f"seed_{RANDOM_SEED}"


TRAIN_FRACTION = 0.80

ROLES = [
    "Accountant",
    "Business Analyst",
    "Data Analyst",
    "Data Engineer",
    "Data Scientist",
    "Financial Analyst",
    "Product Manager",
    "Project Manager",
    "Software Engineer",
]

ALIASES = {
    "microsoft excel": "excel",
    "ms excel": "excel",
    "powerbi": "power bi",
    "structured query language": "sql",
    "python programming": "python",
    "pandas library": "pandas",
    "numpy library": "numpy",
}


def parse_skills(value):
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return []

    if not isinstance(parsed, list):
        return []

    return sorted({
        normalize_skill(skill, ALIASES)
        for skill in parsed
        if str(skill).strip()
    })


def ranking_metrics(ranked_roles, true_role, k=3):
    top_k = ranked_roles[:k]
    relevant_rank = (
        ranked_roles.index(true_role) + 1
        if true_role in ranked_roles
        else None
    )

    hit = int(true_role in top_k)

    return {
        f"precision_at_{k}": hit / k,
        f"recall_at_{k}": float(hit),
        f"ndcg_at_{k}": (
            1 / math.log2(relevant_rank + 1)
            if relevant_rank is not None and relevant_rank <= k
            else 0.0
        ),
        "top1_correct": int(
            bool(ranked_roles) and ranked_roles[0] == true_role
        ),
    }


def main():
    df = pd.read_parquet(DATA_PATH)

    required = {"normalized_title", "skills_required"}
    if not required.issubset(df.columns):
        raise ValueError(f"Dataset must contain: {required}")

    df["normalized_title"] = (
        df["normalized_title"].fillna("").astype(str).str.strip()
    )
    df["parsed_skills"] = df["skills_required"].map(parse_skills)

    # Keep only exact-title examples for the selected roles.
    data = df[
        df["normalized_title"].isin(ROLES)
        & df["parsed_skills"].map(bool)
    ][["normalized_title", "parsed_skills"]].copy()

    data = data.rename(columns={"normalized_title": "target_role"})

    # Prevent identical role-and-skill examples appearing in both splits.
    data["skill_key"] = data["parsed_skills"].map(
        lambda skills: tuple(skills)
    )
    data = data.drop_duplicates(["target_role", "skill_key"])
    data = data.reset_index(drop=True)

    if data.empty:
        raise ValueError("No eligible postings were found.")

    # Split each role independently to preserve representation by role.
    train_parts = []
    test_parts = []

    for role in ROLES:
        group = data[data["target_role"] == role]
        group = group.sample(frac=1, random_state=RANDOM_SEED)

        if len(group) < 5:
            print(f"Skipping {role}: fewer than 5 unique examples.")
            continue

        split_at = int(len(group) * TRAIN_FRACTION)
        split_at = min(max(split_at, 1), len(group) - 1)

        train_parts.append(group.iloc[:split_at])
        test_parts.append(group.iloc[split_at:])

    if not train_parts or not test_parts:
        raise ValueError("Insufficient examples for train/test evaluation.")

    train = pd.concat(train_parts).reset_index(drop=True)
    test = pd.concat(test_parts).reset_index(drop=True)
    evaluated_roles = sorted(train["target_role"].unique())

    # Build all skill profiles from training postings only.
    profile_rows = []

    for role in evaluated_roles:
        group = train[train["target_role"] == role]
        skill_counts = Counter(
            skill
            for skills in group["parsed_skills"]
            for skill in set(skills)
        )

        for skill, count in skill_counts.items():
            profile_rows.append({
                "target_role": role,
                "skill": skill,
                "posting_count": count,
                "percentage_of_postings_with_skills": (
                    count / len(group) * 100
                ),
            })

    profiles = pd.DataFrame(profile_rows)

    if profiles.empty:
        raise ValueError("Could not build role-skill profiles.")

    # The baseline ranks roles by their training-set frequency.
    #role_frequency = train["target_role"].value_counts()
    #baseline_ranking = role_frequency.index.tolist()

    
    # Baseline 1: rank roles by training-set frequency.
    role_frequency = train["target_role"].value_counts()
    frequency_ranking = role_frequency.index.tolist()

    # Baseline 2: create training-only skill profiles for Jaccard overlap.
    role_skill_sets = {}

    for role in evaluated_roles:
        role_data = profiles[
            (profiles["target_role"] == role)
            & (profiles["percentage_of_postings_with_skills"] >= 10)
    ].sort_values(
        ["posting_count", "percentage_of_postings_with_skills"],
        ascending=False,
    ).head(15)

        role_skill_sets[role] = set(role_data["skill"])



    results = []

    for _, row in test.iterrows():
        recommendations = recommend_roles(
            profiles=profiles,
            detected_skills=row["parsed_skills"],
            aliases=ALIASES,
            min_frequency=10,
            max_skills=15,
        )

        model_ranking = recommendations["target_role"].tolist()
        true_role = row["target_role"]

        model_metrics = ranking_metrics(model_ranking, true_role)
        
        frequency_metrics = ranking_metrics(
            frequency_ranking, true_role
        )

        posting_skills = set(row["parsed_skills"])
        jaccard_scores = {}

        for role, role_skills in role_skill_sets.items():
            union = posting_skills | role_skills
            jaccard_scores[role] = (
                len(posting_skills & role_skills) / len(union)
                if union else 0.0
            )

        jaccard_ranking = sorted(
            jaccard_scores,
            key=lambda role: (
                jaccard_scores[role],
                role_frequency.get(role, 0),
            ),
            reverse=True,
        )

        jaccard_metrics = ranking_metrics(
            jaccard_ranking, true_role
        )


        
        results.append({
            "true_role": true_role,
            "predicted_role": (
                model_ranking[0] if model_ranking else ""
            ),
            "model_top1": model_metrics["top1_correct"],
            "model_precision_at_3": model_metrics["precision_at_3"],
            "model_recall_at_3": model_metrics["recall_at_3"],
            "model_ndcg_at_3": model_metrics["ndcg_at_3"],
            "frequency_top1": frequency_metrics["top1_correct"],
            "frequency_precision_at_3": frequency_metrics["precision_at_3"],
            "frequency_recall_at_3": frequency_metrics["recall_at_3"],
            "frequency_ndcg_at_3": frequency_metrics["ndcg_at_3"],
            "jaccard_top1": jaccard_metrics["top1_correct"],
            "jaccard_precision_at_3": jaccard_metrics["precision_at_3"],
            "jaccard_recall_at_3": jaccard_metrics["recall_at_3"],
            "jaccard_ndcg_at_3": jaccard_metrics["ndcg_at_3"],
            "recommendation_coverage": (
                len(model_ranking) / len(evaluated_roles)
            ),
        })


    predictions = pd.DataFrame(results)

    # Overall test metrics.
    
    metric_columns = [
        "model_top1",
        "model_precision_at_3",
        "model_recall_at_3",
        "model_ndcg_at_3",
        "frequency_top1",
        "frequency_precision_at_3",
        "frequency_recall_at_3",
        "frequency_ndcg_at_3",
        "jaccard_top1",
        "jaccard_precision_at_3",
        "jaccard_recall_at_3",
        "jaccard_ndcg_at_3",
        "recommendation_coverage",
    ]


    overall = predictions[metric_columns].mean().to_dict()
    overall = {
        "test_postings": len(test),
        "training_postings": len(train),
        "evaluated_roles": len(evaluated_roles),
        "random_seed": RANDOM_SEED,
        **overall,
    }

    # Per-role results and a top-1 confusion matrix.
    
    per_role = predictions.groupby("true_role").agg(
        test_postings=("true_role", "size"),
        top1_accuracy=("model_top1", "mean"),
        precision_at_3=("model_precision_at_3", "mean"),
        recall_at_3=("model_recall_at_3", "mean"),
        ndcg_at_3=("model_ndcg_at_3", "mean"),
        frequency_baseline_top1=("frequency_top1", "mean"),
        jaccard_baseline_top1=("jaccard_top1", "mean"),
    ).reset_index()


    confusion = pd.crosstab(
        predictions["true_role"],
        predictions["predicted_role"],
        rownames=["Actual role"],
        colnames=["Recommended top role"],
        dropna=False,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([overall]).to_csv(
        OUTPUT_DIR / "overall_metrics.csv", index=False
    )
    per_role.to_csv(
        OUTPUT_DIR / "per_role_metrics.csv", index=False
    )
    confusion.to_csv(
        OUTPUT_DIR / "confusion_matrix.csv"
    )
    predictions.to_csv(
        OUTPUT_DIR / "test_predictions.csv", index=False
    )

    metadata = {
        "dataset": str(DATA_PATH.relative_to(ROOT)),
        "method": "Exact-title, deduplicated, stratified holdout",
        "train_fraction": TRAIN_FRACTION,
        "random_seed": RANDOM_SEED,
        "roles": evaluated_roles,
        "training_postings": len(train),
        "test_postings": len(test),
        "unique_examples_before_split": len(data),
        "important_caveat": (
            "Exploratory evaluation on exact-title postings. "
            "Results do not establish resume-level career suitability "
            "or future labour-market forecasting accuracy."
        ),
    }

    with open(
        OUTPUT_DIR / "evaluation_metadata.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metadata, file, indent=2)

    print("\nOVERALL EVALUATION METRICS")
    print(pd.DataFrame([overall]).to_string(index=False))

    print("\nPER-ROLE METRICS")
    print(per_role.to_string(index=False))

    print("\nSaved evaluation files to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
