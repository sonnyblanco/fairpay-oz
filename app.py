import streamlit as st
import google.generativeai as genai
import os

# 1. Configuration
st.set_page_config(page_title="FairPay Oz", page_icon="🦘")
st.title("🦘 FairPay Oz: AI Wage Checker")
st.markdown("### The AI Assistant for Aussie Tradies")
st.info("DISCLAIMER: This is an AI Prototype. NOT legal advice. Always check the official Fair Work Pay Guide.")

# 2. Setup Google Gemini API
# We get the API Key from Streamlit Secrets (we will set this up next)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("API Key not found. Please set it in Streamlit Secrets.")
    st.stop()

# 3. The "Brain" Logic
def get_gemini_response(question):
    # Upload the PDF file to Gemini
    # Note: In a production app, we would cache this so we don't upload every time.
    sample_file = genai.upload_file(path="payguide.pdf", display_name="Pay Guide")

    # The System Instructions (The "Moat")
    system_instruction = """
    Role: You are "FairPay Oz," an automated wage assistant for Australian small business owners.
Context: You have been provided with the official Fair Work Ombudsman Pay Guide in PDF format.
Your Goal: Answer user questions about hourly rates, overtime, and allowances accurately based ONLY on the provided PDF.
Strict Rules:
Source of Truth: You must ONLY answer using the data in the uploaded PDF. If the user asks something not in the PDF (like "How do I fix a toilet?"), politely refuse.
No Guessing: If the text in the PDF is blurry or the answer isn't there, say: "I cannot find that specific rate in this Pay Guide."
Format: When giving a wage rate, you must state:
The Classification (e.g., "Electrical Worker Grade 1")
The Status (e.g., "Full-time" or "Casual")
The Rate (e.g., "$32.40 per hour")
Legal Disclaimer: You MUST end every single response with this text: "Disclaimer: I am an AI prototype. This is not legal advice. Always cross-check with the official Pay Guide.""
    """
    
    # Configure the model (Gemini 1.5 Pro is best for PDFs)
    model = genai.GenerativeModel(
        model_name="gemini-pro",",
        system_instruction=system_instruction
    )

    # Ask the question with the PDF attached
    response = model.generate_content([sample_file, question])
    return response.text

# 4. The User Interface
user_question = st.text_input("Ask a question (e.g., 'Overtime rate for Grade 1?'):")

if st.button("Check Rate"):
    if user_question:
        with st.spinner("Analyzing Pay Guide PDF..."):
            try:
                answer = get_gemini_response(user_question)
                st.success("Analysis Complete")
                st.write(answer)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question first.")
