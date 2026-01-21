import streamlit as st
import google.generativeai as genai
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

# 3. The "Brain" Logic
def get_gemini_response(question):
    # Upload the PDF file to Gemini
    # Note: Make sure your PDF file on GitHub is named 'payguide.pdf' (lowercase)
    try:
        sample_file = genai.upload_file(path="payguide.pdf", display_name="Pay Guide")
    except Exception as e:
        return f"Error reading PDF: {e}. Did you name the file 'payguide.pdf' in GitHub?"

    # The System Instructions
    system_instruction = """
    You are FairPay Oz. Answer strictly based on the provided Pay Guide PDF.
    If the answer is not in the PDF, say "I cannot find that in the guide."
    Always format wages clearly (Classification, Status, Rate).
    End with: "Disclaimer: Prototype only. Check Fair Work website."
    """
    
    # Configure the model using the one we confirmed exists
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
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
