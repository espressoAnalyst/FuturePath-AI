# FuturePath AI — Career Recommender Evaluation

## 1. Objective

The evaluation examines whether FuturePath AI can recommend relevant career roles based on the skills extracted from job postings. It compares the current recommendation model against two baselines and tests how results vary across different random train-test splits.

## 2. Dataset and Experimental Setup

- **Dataset:** `data/raw/nextgig_jobs_2026-06.parquet`
- **Roles evaluated:** 9
- **Training postings:** 444
- **Test postings per run:** 116
- **Training proportion:** 80%
- **Random seeds:** 7, 17, 21, 42, 100
- **Evaluation approach:** Exact-title filtering, deduplication, and per-role holdout splitting.

The experiment evaluates Accountant, Business Analyst, Data Analyst, Data Engineer, Data Scientist, Financial Analyst, Product Manager, Project Manager, and Software Engineer.

## 3. Evaluation Metrics

- **Top-1 accuracy:** Fraction of test postings for which the first recommended role matches the labeled role.
- **Precision@3:** Fraction of the three recommendation positions occupied by the correct role. With one ground-truth role, a hit in the top three contributes 1/3.
- **Recall@3:** Fraction of relevant roles retrieved within the first three recommendations. With one ground-truth role, this is 1 when the correct role appears in the top three and 0 otherwise.
- **NDCG@3:** Ranking-quality metric that rewards placing the correct role higher in the top three.
- **Recommendation coverage:** Fraction of evaluated roles for which the model generates recommendations.

## 4. Results Across Five Random Seeds

| Metric | Mean | Minimum | Maximum |
|---|---:|---:|---:|
| Top-1 accuracy | 76.90% | 67.24% | 88.79% |
| Precision@3 | 31.15% | 29.60% | 33.05% |
| Recall@3 | 93.45% | 88.79% | 99.14% |
| NDCG@3 | 0.8691 | 0.8039 | 0.9521 |

The model's Top-1 accuracy varies across splits. Its mean Recall@3 is higher than its mean Top-1 accuracy, suggesting that the correct labeled role is frequently retrieved within the top three even when it is not ranked first.

## 5. Baseline Comparison

Two baselines were evaluated:

1. **Frequency baseline:** Ranks roles by their frequency in the training set.
2. **Jaccard baseline:** Ranks roles using overlap between the skills in a test posting and the training-derived role skill profiles.

Across the five seeds, the recommender's Top-1 accuracy ranges from 67.24% to 88.79%. The frequency baseline has Top-1 accuracy of approximately 26.72% on each run, while the Jaccard baseline varies across splits.

These comparisons provide preliminary evidence that skill-profile matching can be more useful than ranking roles by training-set frequency alone. Further validation is needed before drawing broader conclusions.

## 6. Limitations

- The evaluation uses job-posting titles as ground-truth labels rather than real candidate career outcomes.
- Only nine career roles are included in this experiment.
- The test set contains 116 postings per run, so per-role estimates can be sensitive to individual examples.
- Different random seeds reuse the same underlying dataset; the runs are not independent external validations.
- The dataset contains duplicated or overlapping skill patterns that may make some roles easier to distinguish.
- The evaluation does not establish resume-level suitability, future skill demand, salary prediction, or long-term career sustainability.
- The dataset's posting dates are uneven, so it should not be treated as a reliable long-term time series without further validation.

## 7. Conclusion

The current recommender shows promising preliminary performance for matching job-posting skill profiles to labeled career roles. However, the variation across random splits demonstrates that further evaluation is required.

Future work should include validation on genuinely unseen postings or candidate resumes, broader role coverage, improved skill normalization, and a more rigorous temporal evaluation where reliable dated observations are available.

## 8. Reproducibility and Output Files

Evaluation outputs are stored under `outputs/evaluation/`.

- `repeatability_runs.csv` — metrics from the five random-seed runs.
- `repeatability_summary.csv` — mean, minimum, and maximum for selected metrics.
- `seed_7/`, `seed_17/`, `seed_21/`, `seed_100/` — seed-specific evaluation results.
- The existing parent-folder evaluation files preserve the original seed-42 results.

The evaluation script is `research/evaluate_recommender.py`. The random seed can be configured using the `FUTUREPATH_SEED` environment variable.

## 9. Research Integrity Note

These results should be described as an exploratory internal evaluation, not as proof of production-ready career recommendation accuracy. All reported claims should remain consistent with the saved evaluation outputs and the limitations of the dataset and methodology.