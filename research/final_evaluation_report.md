# FuturePath AI
## Final-Year Project Evaluation Report

### 1. Project Overview

**Project title:** FuturePath AI ? An AI-Powered Labor Market Intelligence and Career Optimization Platform

FuturePath AI is a prototype that compares a user's stated or resume-extracted skills with skill frequencies observed in job postings for a selected target role. It provides a role-specific comparison, highlights skills not detected in the supplied information, and allows the user to download the results as a CSV report.

The current implementation focuses on transparent, rule-based skill matching. It should not be described as a validated forecasting or predictive career recommendation model.

### 2. Problem Statement

Students and early-career professionals may find it difficult to identify which skills appear frequently in job postings for a desired role. General career advice may not reflect the skills observed in a particular dataset or role.

FuturePath AI addresses this problem by using job-posting evidence to create role-specific skill profiles and compare them with skills detected in user-provided information.

### 3. Objectives

- Analyze skill information in a global job-posting dataset.
- Build skill-frequency profiles for multiple target occupations.
- Accept manually entered skills or text extracted from a resume.
- Compare detected skills with the selected role's profile.
- Present skill frequencies and skills that may merit further review.
- Export the comparison as a downloadable CSV file.
- Use occupational and macroeconomic reference data to support future research, while keeping different data sources analytically distinct.

### 4. System Architecture

The current prototype uses the following components:

1. **Data layer:** A NextGig job-posting Parquet file, O*NET occupational reference tables, and World Bank labour-market indicator data.
2. **Processing layer:** Python and Pandas scripts for data inspection, skill-frequency analysis, occupation matching, and profile generation.
3. **Profile layer:** CSV files containing role-skill frequencies and usable posting counts.
4. **Application layer:** A Streamlit dashboard that reads the generated role profiles.
5. **Input layer:** Manual skill entry or resume upload in PDF, DOCX, or TXT format.
6. **Matching layer:** Text-based skill detection and comparison with skills selected from the target role profile.
7. **Output layer:** Summary metrics, a skill-comparison table, a resume improvement checklist, and CSV export.

The application relies on previously generated CSV profiles. The current dashboard does not train a predictive model during user interaction.

### 5. Datasets

#### 5.1 NextGig global job postings

- File: `data/raw/nextgig_jobs_2026-06.parquet`
- Records: 112,816
- Columns: 47
- Geographic scope: International, subject to inconsistencies in country labels.
- Postings with usable skill lists: 80,250.
- Distinct normalized skill labels in the initial skill analysis: 53,727.

The dataset provides the observed job-posting skill evidence used to construct role-specific profiles. These records are a dataset sample, not a verified census of all vacancies worldwide.

The date field is incomplete: 20,199 dates were parseable and 92,617 were missing or unparseable in the initial audit. Consequently, the dataset is not treated as a reliable historical time series for forecasting.

#### 5.2 O*NET occupational reference data

Files in `data/raw/onet/`:
- `occupation_data.csv`
- `essential_skills.csv`
- `software_skills.csv`

The inspected tables contain 1,016 occupation records, 18,200 essential-skill records, and 31,821 software-skill records.

O*NET provides standardized occupational descriptions and skill references, primarily for the United States. Importance ratings and source-provided software-skill flags are reference information, not live job-ad frequencies. They are not directly interchangeable with NextGig skill counts.

#### 5.3 World Bank labour-market indicators

- Raw file: `data/raw/world_bank/world_bank_labour_indicators_2010_2025.csv`
- Validated analysis copy: `outputs/metrics/world_bank/world_bank_labour_indicators_validated.csv`
- Period: 2010?2025
- Observations: 7,492
- Entities: 235
- Indicators: unemployment rate and labour force participation rate.

The validated copy uses an entity identifier to distinguish countries and aggregate groups. It contains zero duplicate entity-year-indicator keys. There are 128 records without country codes; these have been retained rather than automatically discarded.

These indicators provide broad labour-market context. They do not measure demand for a specific occupation or skill and are not inputs to the current role-specific skill-matching calculation.

### 6. Data Processing and Methodology

#### 6.1 General skill-frequency analysis

The initial analysis reads the NextGig Parquet file with Pandas, parses the `skills_required` field as lists, normalizes labels by trimming whitespace, collapsing repeated spaces, and converting text to lowercase, and counts a skill at most once per posting.

The initial global skill-frequency denominator is the 80,250 postings with at least one parsed skill. Frequencies describe the selected dataset and its parsing rules.

#### 6.2 Role-specific profile generation

The expanded profile artifacts are:
- `outputs/metrics/expanded/role_skill_frequency_expanded.csv`
- `outputs/metrics/expanded/role_posting_counts_expanded.csv`

The profile contains 7,335 role-skill records across 21 target roles, with no missing role names, missing skill names, or duplicate role-skill pairs in the validation check.

Role matching uses title-normalization and pattern-based matching. Such matching can produce false positives or miss relevant titles. The usable posting counts differ by role, and results for roles with very few postings are particularly uncertain.

#### 6.3 Resume skill detection

The dashboard accepts PDF, DOCX, and TXT files and attempts to extract text from them. It also accepts manually entered, comma-separated skills.

The current detection method searches for skill-name text in the extracted resume text after basic normalization and a small alias mapping. It does not understand all synonyms, infer proficiency, verify work experience, or determine whether a skill is genuinely mastered.

A skill labelled ?Not detected? should therefore be treated as a prompt to review the resume, not proof that the user lacks that skill.

#### 6.4 Skill-gap comparison

For the selected role, the application filters the role profile to skills with a posting frequency of at least 10%, sorts the records by posting count, and displays up to 15 skills.

The application reports detected skills and skills not detected in the submitted information. It also displays the usable posting count for the selected role and allows the comparison to be exported as CSV.

These results are descriptive and rule-based. They are not an assessment of a candidate's overall employability or a guarantee of hiring success.

### 7. Current Implementation

The following functionality has been manually tested during development:

- Streamlit dashboard opens.
- Expanded target-role dropdown displays 21 roles.
- Manual skill entry produces skill-gap results.
- Resume upload and text extraction produce results using a test resume.
- CSV report download works and includes the expected fields.
- Data Scientist and Accountant selections produce different, role-appropriate results.
- Expanded profile and count files contain the same 21 target roles.
- The expanded profile contains no duplicate role-skill pairs.
- The World Bank validated copy contains zero duplicate analytical keys.

These are manual functional checks, not a formal automated test suite. The `tests/` directory was empty during the project file inspection.

### 8. Data Quality and Limitations

1. **Coverage:** NextGig is a dataset sample and should not be presented as a complete representation of the global labour market.
2. **Missing data:** Posting dates and sector metadata are substantially incomplete.
3. **Title matching:** Pattern-based role matching may include false positives and miss relevant postings.
4. **Small samples:** Some roles have very few usable postings. For example, HR Analyst has 3, Marketing Analyst 7, Business Intelligence Analyst 11, Cybersecurity Analyst 12, and Frontend Developer 15.
5. **Skill normalization:** Similar skills and synonyms may remain separate labels.
6. **Resume parsing:** Text extraction may fail on scanned PDFs or unusual document layouts. Basic string matching may miss synonyms or context.
7. **External reference compatibility:** O*NET and World Bank indicators have different scopes, definitions, and units from job-posting data. They are not merged indiscriminately into the role-frequency calculations.
8. **No predictive validation:** Forecasting accuracy, automation-risk accuracy, salary prediction performance, and career recommendation quality have not been established by the current dashboard.
9. **No formal user study:** The reported functional checks do not demonstrate usability or real-world career outcomes.

### 9. Future Work

- Add automated tests for data processing and application functions.
- Improve title normalization and validate occupation matching against labelled examples.
- Standardize skill labels using a documented taxonomy and carefully reviewed synonym mappings.
- Improve resume parsing and provide clearer evidence for each detected skill.
- Add source, sample-size, and uncertainty indicators to displayed recommendations.
- Explore historical forecasting only if sufficiently complete and consistent time-series data can be obtained and evaluated chronologically.
- Develop and validate explainable predictive models as separate future modules.
- Conduct a user study and measure the usefulness and clarity of the skill-gap report.

### 10. Conclusion

FuturePath AI currently demonstrates a functioning prototype for evidence-based, role-specific skill comparison using job-posting skill frequencies. It accepts manual skills and resumes, presents skills detected or not detected in the supplied information, and exports a comparison report.

The project also includes inspected occupational reference data and validated macro labour-market indicators for future research. These sources are kept analytically distinct because they measure different things.

The current results should be interpreted as descriptive guidance from the selected data, not as validated forecasts or guarantees about future employment outcomes.
