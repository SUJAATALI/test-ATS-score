# Resume ATS Score Analyzer

A streamlined application to intelligently evaluate resumes against job descriptions, simulating how real-world ATS (Applicant Tracking Systems) and recruiters assess applications—especially for entry-level tech roles.

## 🚀 Features

- **Resume Parsing:** Extracts content from uploaded PDF resumes.
- **Job Description Matching:** Compares resumes against selected or custom job descriptions.
- **Keyword Intelligence:** Scores resumes based on the presence and relevance of domain-specific and role-specific keywords.
- **Metrics Evaluation:** Recognizes quantified achievements such as percentages, counts, and monetary impact to simulate recruiter preferences.
- **Dual Evaluation Engine:**
  - **Rule-Based Scoring:** Based on structure, keywords, project presence, and certification matches.
  - **Intelligent Scoring Feedback:** Provides reasoned scoring and actionable suggestions on resume quality and alignment with job expectations.

## 🧠 Scoring Breakdown

The analyzer scores resumes across key sections:

- Education  
- Experience (or Projects, for freshers)  
- Skills & Tools  
- Certifications  
- Quantified Impact (numbers, results, KPIs)  
- JD Keyword Match  
- Layout & Structure  

## 📂 How to Use Locally

1. **Clone the repository**

   ```bash
   git clone https://github.com/SUJAATALI/test-ATS-score
   cd test-ATS-score

2.**Install dependencies**

pip install -r requirements.txt

3. **Create .env file**

OPENAI_API_KEY=your-api-key-here

4. **Run the application **
 streamlit run main.py

5. **Upload your resume and select a job role to get scored.**

   
---

```markdown
## 📁 Files Included

- `main.py` – Streamlit app code  
- `job_descriptions.json` – Predefined job roles and expectations  
- `.gitignore` – Hides sensitive environment settings  
- `.env` – (Not pushed) Holds private API keys locally  

## ✅ Use Cases

- Freshers preparing for placement season  
- Resume reviewers simulating ATS systems  
- Career services in universities  
- Ed-tech platforms offering personalized resume tips  

## 📌 Note

📌 This tool respects ATS standards and evaluates resumes fairly even when traditional experience is limited—especially helpful for early-career roles.

Feel free to fork and adapt for your own job descriptions or institutional needs.




