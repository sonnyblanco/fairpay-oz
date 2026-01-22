import streamlit as st
import google.generativeai as genai
from github import Github # This is the library to talk to GitHub
import os

# 1. Configuration
st.set_page_config(page_title="FairPay Oz", page_icon="🦘")
st.title("🦘 FairPay Oz: AI Wage Checker")
st.markdown("### The AI Assistant for Aussie Tradies")
st.info("DISCLAIMER: This is an AI Prototype. NOT legal advice. Always check the official Fair Work Pay Guide.")

# 2. Setup Google Gemini API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("API Key not found. Please set it in Streamlit Secrets.")
    st.stop()

# ---------------------------------------------------------
# ADMIN SECTION: Handle File Updates
# ---------------------------------------------------------
with st.sidebar:
    st.header("🔒 Admin Access")
    admin_pass = st.text_input("Enter Password", type="password")
    
    if admin_pass == st.secrets["ADMIN_PASSWORD"]:
        st.success("Logged In")
        uploaded_new_pdf = st.file_uploader("Update Pay Guide PDF", type="pdf")
        
        if uploaded_new_pdf is not None:
            if st.button("Upload & Update AI"):
                try:
                    # Connect to GitHub
                    g = Github(st.secrets["GITHUB_TOKEN"])
                    # Get the Repo (Change 'yourusername/fairpay-oz' to YOUR actual repo path if needed, 
                    # but usually get_user().get_repo works if you own it)
                    # NOTE: You might need to hardcode the repo name if the automatic detection fails.
                    # Let's assume the repo name is 'fairpay-oz'
                    user = g.get_user()
                    repo = user.get_repo("fairpay-oz")
                    
                    # Get the existing file to update it
                    contents = repo.get_contents("payguide.pdf")
                    
                    # Update the file on GitHub
                    repo.update_file(
                        path=contents.path,
                        message="Admin updated Pay Guide via App",
                        content=uploaded_new_pdf.getvalue(),
                        sha=contents.sha
                    )
                    
                    st.success("✅ GitHub Updated! Rebooting app to refresh AI...")
                    # Clear the cache so the AI re-reads the new file
                    st.cache_resource.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Update Failed: {e}")
                    st.warning("Make sure your Repo Name is exactly 'fairpay-oz' and your Token has 'repo' permissions.")

# ---------------------------------------------------------
# MAIN APP LOGIC
# ---------------------------------------------------------

# 3. The "Brain" Logic (Cached)
@st.cache_resource
def get_model():
    try:
        # Upload the PDF file
        # Note: We read the file from the local disk (which Streamlit pulled from GitHub)
        sample_file = genai.upload_file(path="payguide.pdf", display_name="Pay Guide")
    except Exception as e:
        st.error(f"Error reading PDF: {e}. Is 'payguide.pdf' in the repo?")
        return None, None

    # System Instructions
    system_instruction = """
    Role: You are "FairPay Oz," an automated wage assistant for Australian small business owners.
    Context: You have been provided with the official Fair Work Ombudsman Pay Guide in PDF format.
    Your Goal: Answer user questions about hourly rates, overtime, and allowances accurately based ONLY on the provided PDF.
    
    Strict Rules:
    1. Source of Truth: You must ONLY answer using the data in the uploaded PDF. If the user asks something not in the PDF, politely refuse.
    2. No Guessing: If the text in the PDF is blurry or the answer isn't there, say: "I cannot find that specific rate in this Pay Guide."
    3. Format: When giving a wage rate, you must state:
       - The Classification (e.g., "Electrical Worker Grade 1")
       - The Status (e.g., "Full-time" or "Casual")
       - The Rate (e.g., "$32.40 per hour")
    4. Legal Disclaimer: You MUST end every single response with this text: "Disclaimer: I am an AI prototype. This is not legal advice. Always cross-check with the official Pay Guide."
    """
    
    # Configure the model
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=system_instruction
    )
    return model, sample_file

# Initialize
try:
    model, sample_file = get_model()
except:
    st.stop()

# 4. User Interface
user_question = st.text_input("Ask a question (e.g., 'Overtime rate for Grade 1?'):")

if st.button("Check Rate"):
    if user_question and model:
        with st.spinner("Analyzing Pay Guide PDF..."):
            try:
                response = model.generate_content([sample_file, user_question])
                st.success("Analysis Complete")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question first.")
