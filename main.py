import streamlit as st
import json
import fitz  # PyMuPDF
import re
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Resume ATS Score Analyzer", layout="wide")

@st.cache_data
def extract_pdf_text(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# === Manual Scoring ===
def score_section_presence(text):
    required_sections = ['education', 'experience', 'projects', 'skills']
    return sum(1 for sec in required_sections if sec in text.lower()) * 3.75  # max 15

def score_keywords(text, jd_keywords, high_priority):
    text = text.lower()
    score = sum(1 for kw in jd_keywords if kw in text)
    bonus = sum(2 for kw in high_priority if kw in text)
    return min(score + bonus, 25)

def score_metrics(text):
    return 15 if re.search(r"\d+%|\$\d+|\d+\s+(users|clients|sales|projects)", text.lower()) else 7.5

def score_projects(text):
    return 20 if "project" in text.lower() else 10

def score_certifications(text, jd_keywords):
    matches = sum(1 for cert in jd_keywords if "cert" in cert and cert in text.lower())
    return min(matches * 5, 10)

# === GPT Prompt ===
def query_openai_structured(resume_text, jd_text):
    prompt = f"""
You are an expert ATS evaluator for top tech companies hiring freshers.

Evaluate the following resume using this rubric:

- Contact Info: 5
- Professional Summary: 10
- Education: 15
- Technical Skills: 15
- Projects: 15
- Certifications: 10
- Internships/Experience: 15
- Extracurricular Activities: 5
- JD Keyword Match: 10

Give a detailed score out of 100, and respond in JSON like:a

{{
  "total_score": XX,
  "section_scores": {{
    "Contact Info": X,
    "Professional Summary": X,
    "Education": X,
    "Technical Skills": X,
    "Projects": X,
    "Certifications": X,
    "Internships/Experience": X,
    "Extracurricular Activities": X,
    "JD Keyword Match": X
  }},
  "feedback": {{
    "strengths": [ ... ],
    "areas_for_improvement": [ ... ]
  }}
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert ATS resume evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ OpenAI API error: {e}")
        return None

# === Streamlit App ===
st.title("📄 Resume ATS Score Analyzer")
st.caption("🧠 Combines manual + GPT scoring with optional JD matching")

use_jd = st.checkbox("Use Job Description for Scoring")
deep_ai_review = st.checkbox("🔍 Deep AI Review using OpenAI GPT")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Your Resume")
    resume_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    resume_text = ""
    if resume_file:
        resume_text = extract_pdf_text(resume_file)
        st.success("✅ Resume uploaded and text extracted.")

with col2:
    st.subheader("(Optional) Select a Job Role")
    jd_keywords = set()
    high_priority_keywords = []
    jd_text = ""
    if use_jd:
        try:
            with open("job_descriptions.json", "r", encoding="utf-8") as f:
                job_data = json.load(f)
            job_titles = [job["job_title"] for job in job_data]
            selected_title = st.selectbox("Choose a job title", job_titles)
            selected_job = next(job for job in job_data if job["job_title"] == selected_title)
            jd_text = selected_job["job_description"]["overview"] + "\n\nResponsibilities:\n" + "\n".join(
                selected_job["job_description"]["responsibilities"])
            jd_text = st.text_area("Job Description (editable)", value=jd_text, height=300)
            if st.checkbox("Paste your own JD instead"):
                jd_text = st.text_area("Paste your custom job description here", height=300)

            # Extract keywords from JD
            for word in jd_text.split():
                clean = word.strip(",.():").lower()
                if len(clean) > 2 and clean.isalpha():
                    jd_keywords.add(clean)

            keyword_tags = selected_job.get("key_resume_keywords_for_ats_optimization", {})
            for cat, terms in keyword_tags.items():
                for term in terms:
                    if isinstance(term, str):
                        high_priority_keywords.append(term.lower())
                        jd_keywords.add(term.lower())

        except Exception as e:
            st.error(f"⚠️ Failed to load job descriptions: {e}")

# === Button Click ===
if st.button("Compare Resume with JD") and resume_text:
    st.subheader("📊 Manual ATS Score Breakdown")
    score1 = score_section_presence(resume_text)
    score2 = score_keywords(resume_text, jd_keywords, high_priority_keywords)
    score3 = score_metrics(resume_text)
    score4 = score_projects(resume_text)
    score5 = score_certifications(resume_text, jd_keywords)

    manual_score = round(score1 + score2 + score3 + score4 + score5, 2)
    st.markdown(f"### 🧮 Manual Score: `{manual_score}%`")
    st.progress(min(int(manual_score), 100))

    st.markdown("#### Breakdown")
    st.markdown(f"- 📐 Sections Present: `{round(score1, 2)}%`")
    st.markdown(f"- 🧠 JD Keywords: `{round(score2, 2)}%`")
    st.markdown(f"- 📊 Metrics/Impact: `{round(score3, 2)}%`")
    st.markdown(f"- 🧪 Projects Mentioned: `{round(score4, 2)}%`")
    st.markdown(f"- 🏅 Certifications: `{round(score5, 2)}%`")

    if deep_ai_review:
        st.subheader("🤖 GPT-Based ATS Evaluation")
        with st.spinner("🧠 Evaluating via OpenAI..."):
            output = query_openai_structured(resume_text, jd_text)
            if output:
                try:
                    parsed = json.loads(output)
                    final_score = parsed["total_score"]
                    st.success("✅ AI Evaluation Complete")
                    st.markdown(f"### 🌟 GPT ATS Score: `{final_score}%`")
                    st.progress(min(int(final_score), 100))

                    st.markdown("#### 📘 GPT Score Breakdown")
                    for k, v in parsed["section_scores"].items():
                        st.markdown(f"- **{k}**: `{v} points`")

                    st.markdown("#### ✅ Strengths")
                    for s in parsed["feedback"]["strengths"]:
                        st.markdown(f"- {s}")

                    st.markdown("#### 🛠 Areas to Improve")
                    for s in parsed["feedback"]["areas_for_improvement"]:
                        st.markdown(f"- {s}")
                except:
                    st.error("⚠️ GPT response could not be parsed.")
                    st.text(output)
else:
    st.info("Upload your resume to begin analysis. JD scoring is optional.")
