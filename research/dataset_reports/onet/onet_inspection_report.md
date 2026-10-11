# O*NET Dataset Inspection Report

## Purpose
Inspect O*NET occupation and skill tables for potential use in FuturePath AI.

## Dataset summary
### occupations
- Rows: 1016
- Columns: 3
- Exact duplicate rows: 0
- Missing cells: 0
- Columns: O*NET-SOC Code, Title, Description

### essential_skills
- Rows: 18200
- Columns: 15
- Exact duplicate rows: 0
- Missing cells: 9100
- Columns: O*NET-SOC Code, Title, Element ID, Element Name, Scale ID, Scale Name, Data Value, N, Standard Error, Lower CI Bound, Upper CI Bound, Recommend Suppress, Not Relevant, Date, Domain Source

### software_skills
- Rows: 31821
- Columns: 7
- Exact duplicate rows: 0
- Missing cells: 0
- Columns: O*NET-SOC Code, Title, Workplace Example, Element ID, Element Name, Hot Technology, In Demand

## Occupation-code linkage
- Unique occupation codes: 1016
- Essential-skills codes matching occupation data: 910
- Software-skills codes matching occupation data: 923

## Essential skill importance
The summary averages rows whose Scale ID is IM (Importance). It is descriptive of this O*NET release, not a measure of current job-posting demand.

## Software skill flags
Hot Technology and In Demand counts preserve the source-provided flags. They should not be interpreted as live or India-specific demand.

## Limitations
- O*NET primarily describes US occupations.
- Occupation-code matching does not guarantee identical coverage in all tables.
- A missing value does not mean a skill or attribute is absent in reality.
- O*NET skills and job-posting skills use different taxonomies and may need careful mapping.

## Generated outputs
- outputs/metrics/onet/onet_audit_summary.json
- outputs/metrics/onet/essential_skill_importance_summary.csv
- outputs/metrics/onet/software_skill_summary.csv