from pathlib import Path
import re
import io
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent



PROFILE_PATH = BASE / "outputs" / "metrics" / "expanded" / "role_skill_frequency_expanded.csv"
COUNTS_PATH = BASE / "outputs" / "metrics" / "expanded" / "role_posting_counts_expanded.csv"

st.set_page_config(page_title="FuturePath AI", page_icon="🎯", layout="wide")

st.title("🎯 FuturePath AI")
st.subheader("Labor Market Intelligence & Career Optimization")
st.write(
    "Compare your skills with those reported in job postings "
    "and identify areas to review for your target role."
)

if not PROFILE_PATH.exists() or not COUNTS_PATH.exists():
    st.error("Required CSV files are missing. Run the role-skill profile script first.")
    st.stop()

profiles = pd.read_csv(PROFILE_PATH)
counts = pd.read_csv(COUNTS_PATH)
roles = sorted(profiles["target_role"].dropna().unique())

ALIASES = {
    "microsoft excel": "excel",
    "ms excel": "excel",
    "powerbi": "power bi",
    "structured query language": "sql",
    "python programming": "python",
    "pandas library": "pandas",
    "numpy library": "numpy",
}

def normalize(value):
    value = re.sub(r"\s+", " ", str(value).strip().casefold())
    return ALIASES.get(value, value)

def extract_resume_text(uploaded_file):
    if uploaded_file is None:
        return ""

    suffix = Path(uploaded_file.name).suffix.lower()
    raw = uploaded_file.getvalue()

    if suffix == ".txt":
        return raw.decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            st.warning("PDF reading needs pypdf. Run: python -m pip install pypdf")
        except Exception as exc:
            st.warning(f"Could not read this PDF: {exc}")

    if suffix == ".docx":
        try:
            from docx import Document
            document = Document(io.BytesIO(raw))
            return "\n".join(p.text for p in document.paragraphs)
        except ImportError:
            st.warning("DOCX reading needs python-docx. Run: python -m pip install python-docx")
        except Exception as exc:
            st.warning(f"Could not read this DOCX: {exc}")

    return ""

with st.sidebar:
    st.header("Your career profile")
    target_role = st.selectbox("Choose your target role", roles)
    uploaded = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        help="Text-based PDF, DOCX, or TXT. Scanned PDFs may need OCR."
    )
    manual_skills = st.text_area(
        "Or enter skills manually",
        placeholder="Python, SQL, Excel, Power BI",
        height=120
    )
    analyze = st.button("Analyze my skills", type="primary", use_container_width=True)

if analyze:
    resume_text = extract_resume_text(uploaded)

    role_profiles = profiles[profiles["target_role"] == target_role].copy()
    role_profiles = role_profiles[
        role_profiles["percentage_of_postings_with_skills"] >= 10
    ].sort_values("posting_count", ascending=False).head(15)

    if role_profiles.empty:
        st.error("No usable skill profile exists for this role.")
        st.stop()

    detected_skills = set()

    if resume_text.strip():
        resume_lower = resume_text.casefold()
        for skill in role_profiles["skill"].dropna().unique():
            normalized_skill = normalize(skill)
            if re.search(
                r"(?<!\w)" + re.escape(normalized_skill) + r"(?!\w)",
                resume_lower
            ):
                detected_skills.add(normalized_skill)

    for skill in manual_skills.split(","):
        if skill.strip():
            detected_skills.add(normalize(skill))

    role_count = counts[counts["target_role"] == target_role]
    usable_count = int(role_count["postings_with_skills"].iloc[0])

    role_profiles["status"] = role_profiles["skill"].apply(
        lambda skill: "Detected" if normalize(skill) in detected_skills
        else "Not detected"
    )

    matched = int((role_profiles["status"] == "Detected").sum())
    total = len(role_profiles)

    st.header(f"Results: {target_role}")
    st.caption(
        f"Based on {usable_count} job postings with usable skill lists. "
        "This is a sample-based comparison, not a market-wide prediction."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Skills reviewed", total)
    col2.metric("Skills detected", matched)
    col3.metric("Skills to review", total - matched)

    st.progress(matched / total if total else 0)

    st.subheader("Skill comparison")
    st.dataframe(
        role_profiles[
            ["skill", "posting_count",
             "percentage_of_postings_with_skills", "status"]
        ].rename(columns={
            "skill": "Skill",
            "posting_count": "Postings mentioning skill",
            "percentage_of_postings_with_skills": "Posting frequency (%)",
            "status": "Resume match",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "A skill marked 'Not detected' may still be one you have. "
        "Review your resume wording and the extracted text before treating "
        "it as a genuine skill gap."
    )

    st.subheader("Resume improvement checklist")
    missing = role_profiles[role_profiles["status"] == "Not detected"]

    if missing.empty:
        st.success("All displayed skills were detected in your supplied information.")
    else:
        for _, row in missing.iterrows():
            st.write(
                f"- Review **{row['skill']}** "
                f"({row['percentage_of_postings_with_skills']:.1f}% "
                "of usable postings for this role). If you genuinely have "
                "this skill, consider showing it clearly in your resume."
            )

    csv = role_profiles.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download skill-gap report",
        data=csv,
        file_name="futurepath_skill_gap_report.csv",
        mime="text/csv",
    )

else:
    st.info("Choose a target role, upload a resume or enter skills, then select Analyze my skills.")
    st.write("### What this prototype does")
    st.write("- Role-specific skill comparison")
    st.write("- Resume text extraction when the required reader is available")
    st.write("- Evidence-based skill frequencies from your dataset")
    st.write("- Downloadable skill-gap report")
