# FuturePath AI — Day 1 Research Log

## 1. Research question

What patterns in job postings, required skills, occupations, and disclosed
salaries can be observed in the selected dataset, and how can these patterns
inform evidence-based career guidance?

## 2. Dataset

- File: nextgig_jobs_2026-06.parquet
- Source: NextGig-Rocks global job postings dataset
- Records loaded: 112,816
- Columns: 47
- Geographic scope: International; country labels require normalization.
- Dataset is treated as a snapshot, not a verified historical time series.

## 3. Data-quality audit

- Exact duplicate rows: 0
- Missing or unparseable posting dates: 92,617
- Parseable posting dates: 20,199
- Posting dates later than 2026-10-11: 8
- Non-empty skills fields in the initial audit: 80,412
- Records with non-empty industry fields: 7,358
- Records with non-empty salary minimums: 51,829
- Records with non-empty salary maximums: 47,162
- Records with missing country values: 9,349

Note: zero exact duplicate rows does not establish the absence of
semantically duplicated job advertisements. Date formats and future-dated
records require further verification before time-based analysis.

## 4. Experiment 1: Skill frequency

Method:
1. Read the Parquet dataset with Pandas.
2. Parse skills_required as JSON lists.
3. Normalize skill labels by trimming whitespace, collapsing repeated
   spaces, and converting to lowercase.
4. Count each normalized skill at most once per posting.
5. Calculate percentages using postings with at least one parsed skill.

Observed results:
- Total job postings: 112,816
- Postings with at least one parsed skill: 80,250
- Invalid or non-list skill fields: 162
- Distinct normalized skill labels: 53,727

Top observed skills:
- Customer service: 20,419 postings (25.44%)
- Communication: 14,002 postings (17.45%)
- Inventory management: 7,395 postings (9.21%)
- Safety compliance: 7,252 postings (9.04%)
- Team leadership: 6,338 postings (7.90%)
- Data analysis: 4,407 postings (5.49%)

These frequencies describe this dataset only. They do not represent
the complete labor market. Semantically similar labels may be counted
separately.

## 5. Generated artifacts

- src/audit_dataset.py
- src/analyze_skills.py
- outputs/metrics/missing_values.csv
- outputs/metrics/dataset_audit_summary.json
- outputs/metrics/skill_frequency.csv
- outputs/figures/top_skills.html

## 6. Current limitations

- The dataset has substantial missingness in several important fields.
- Industry is available for only a small fraction of records.
- Country labels contain aliases that must be standardized.
- Posting dates are sparse and include future-dated records.
- Salary fields contain multiple currencies and potentially different
  reporting units; direct comparisons require additional cleaning.
- Skill labels have not yet been mapped to a standardized taxonomy.
- No predictive model has been trained or validated.
- No forecasting accuracy, career-matching accuracy, or ATS performance
  has been established.

## 7. Next research steps

1. Verify country labels and geographic coverage.
2. Inspect whether available fields support reliable sector-level analysis.
3. Produce a documented chart and table from cleaned data.
4. Define transparent, interpretable career-matching and skill-priority
   rules.
5. Consider forecasting only if suitable historical observations can
   be established and evaluated chronologically.
