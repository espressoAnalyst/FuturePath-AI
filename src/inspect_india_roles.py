import pandas as pd

path = "data/raw/nextgig_jobs_2026-06.parquet"
df = pd.read_parquet(path)

# Normalize country labels for this inspection only.
country = df["country"].astype(str).str.strip().str.casefold()
india = df[country.isin(["india", "in"])].copy()

print("India postings:", len(india))

print("\n--- Most common normalized job titles in India ---")
if "normalized_title" in india.columns:
    print(india["normalized_title"].dropna()
          .astype(str).value_counts().head(40).to_string())
else:
    print("normalized_title column not found")

print("\n--- Candidate role counts in India ---")
roles = {
    "Data Analyst": r"\bdata analyst\b",
    "Business Analyst": r"\bbusiness analyst\b",
    "Business Intelligence Analyst": r"\bbusiness intelligence analyst\b",
    "Financial Analyst": r"\bfinancial analyst\b",
    "Operations Analyst": r"\boperations analyst\b",
    "Data Engineer": r"\bdata engineer\b",
    "Software Developer": r"\bsoftware developer\b|\bsoftware engineer\b",
    "QA Engineer": r"\bqa engineer\b|\bquality assurance engineer\b",
    "Cybersecurity Analyst": r"\bcybersecurity analyst\b|\bsecurity analyst\b",
    "HR Analyst": r"\bhr analyst\b|\bhuman resources analyst\b",
    "Marketing Analyst": r"\bmarketing analyst\b",
    "Accountant": r"\baccountant\b",
    "Project Manager": r"\bproject manager\b",
    "Supply Chain Analyst": r"\bsupply chain analyst\b",
    "Logistics Coordinator": r"\blogistics coordinator\b",
    "Mechanical Engineer": r"\bmechanical engineer\b",
    "Civil Engineer": r"\bcivil engineer\b",
    "Quality Analyst": r"\bquality analyst\b",
    "Product Manager": r"\bproduct manager\b",
    "Customer Support Specialist": r"\bcustomer support specialist\b|\bcustomer service representative\b",
}

titles = india["normalized_title"].fillna("").astype(str)

for role, pattern in roles.items():
    count = titles.str.contains(pattern, case=False, regex=True).sum()
    print(f"{role}: {count}")

