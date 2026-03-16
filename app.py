import streamlit as st
from fpdf import FPDF

# Import necessary libraries for functions
import PyPDF2
import google.generativeai as genai
import os
from dotenv import load_dotenv # Keep for completeness, though os.environ setting might make it redundant in Colab
import time

# --- Function Definitions from Notebook Cells ---

# Function for extracting resume text
def extract_resume_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text[:4000]

# Configure Gemini API and define ask_gemini function
load_dotenv() # Load .env file, if present. Colab's os.environ setting will override if GOOGLE_API_KEY is present.
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash") # Changed model from gemini-1.5-flash to gemini-2.5-flash

def ask_gemini(prompt):
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < 2:
                time.sleep(10)
            else:
                return f"API Error: {str(e)}"

# Function for generating prompt
def generate_prompt(resume, role, jd):
    return f"""
You are an expert AI career advisor.
Resume:
{resume}
Target Role:
{role}
Job Description:
{jd}
Generate structured output:
1️⃣ ATS Resume Score (0-100) with explanation
2️⃣ Job Description Match %
3️⃣ Missing Skills
4️⃣ Recommended Skills to Learn
5️⃣ Salary Range in India
6️⃣ LinkedIn Profile Improvement Tips
7️⃣ 5 Course Recommendations with links (Coursera / Udemy)
8️⃣ 10 Interview Questions with answers
Return the report in clear sections.
"""

# --- Streamlit App Layout ---

# page config
st.set_page_config(
    page_title="GenAI Career Dashboard",
    page_icon="🚀",
    layout="wide"
)

# load css - This line is removed as CSS is injected in a previous cell
# with open("assets/style.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🚀 GenAI Career Mentor")
st.write("AI Powered Resume Analysis & Career Planning")

# input layout
col1, col2 = st.columns(2)

with col1:
    role = st.text_input("🎯 Target Role")
    resume_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"]
    )

with col2:
    jd = st.text_area(
        "Paste Job Description (optional)",
        height=200
    )

st.divider()

if st.button("Analyze Career Profile"):
    if resume_file and role:
        with st.spinner("Analyzing resume with AI..."):
            resume_text = extract_resume_text(resume_file)
            prompt = generate_prompt(resume_text, role, jd)
            result = ask_gemini(prompt)

        st.success("Analysis Complete")
        st.markdown("## 📊 AI Career Report")
        st.write(result)

        # PDF export
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in result.split("\n"):
            # Encode to latin-1, replacing characters that cannot be encoded
            # Then decode back to a string, as multi_cell expects a string
            safe_line = line.encode('latin-1', errors='replace').decode('latin-1')
            pdf.multi_cell(0, 8, safe_line)

        pdf.output("career_report.pdf")

        with open("career_report.pdf", "rb") as f:
            st.download_button(
                "📄 Download Report",
                f,
                file_name="career_report.pdf"
            )
    else:
        st.warning("Please upload resume and enter role")

# mock interview section
st.divider()
st.subheader("🎤 Mock Interview Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.text_input("Ask Interview Question")

if st.button("Ask AI"):
    if question:
        prompt = f"""
You are an interviewer for {role} role.
Question:
{question}
Give a professional interview answer.
"""
        answer = ask_gemini(prompt)
        st.session_state.chat_history.append((question, answer))

for q, a in st.session_state.chat_history:
    st.markdown(f"**👤 You:** {q}")
    st.markdown(f"**🤖 AI:** {a}")
