import streamlit as st
import google.generativeai as genai
from github import Github
import os

# 1. Configuration
st.set_page_config(page_title="FairPay Oz", page_icon="🦘")
st.title("🦘 FairPay Oz: AI Wage Assistant")
st.markdown("### The Chatbot for Aussie Tradies")
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
                    # STEP 1: Save it LOCALLY
                    with open("payguide.pdf", "wb") as f:
                        f.write(uploaded_new_pdf.getvalue())
                    
                    # STEP 2: Save it to GITHUB
                    g = Github(st.secrets["GITHUB_TOKEN"])
                    user = g.get_user()
                    # Change 'fairpay-oz' if your repo name is different
                    repo = user.get_repo("fairpay-oz") 
                    contents = repo.get_contents("payguide.pdf")
                    
                    repo.update_file(
                        path=contents.path,
                        message="Admin updated Pay Guide via App",
                        content=uploaded_new_pdf.getvalue(),
                        sha=contents.sha
                    )
                    
                    st.success("✅ Updated Locally AND on GitHub!")
                    st.warning("Please click 'Clear Cache' below.")
                    
                except Exception as e:
                    st.error(f"Update Failed: {e}")

            if st.button("Clear AI Cache & Reload"):
                st.cache_resource.clear()
                st.rerun()
    
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# MAIN APP LOGIC
# ---------------------------------------------------------

# 3. The "Brain" Logic (Cached)
@st.cache_resource
def get_model():
    try:
        sample_file = genai.upload_file(path="payguide.pdf", display_name="Pay Guide")
    except Exception as e:
        st.error(f"Error reading PDF: {e}. Is 'payguide.pdf' in the repo?")
        return None, None

    system_instruction = """
    Role: You are "FairPay Oz," an automated wage assistant.
    Context: You use the provided Pay Guide PDF.
    Strict Rules:
    1. Answer ONLY using the PDF data.
    2. Format wages clearly (Classification, Status, Rate).
    3. If asked to calculate totals (e.g., "What is the total for 8 hours?"), perform the math step-by-step using the rate found in the PDF.
    4. End with: "Disclaimer: Prototype only. Check Fair Work website."
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=system_instruction
    )
    return model, sample_file

try:
    model, sample_file = get_model()
except:
    st.stop()

# 4. The Chat Interface (New!)

# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask a question (e.g., 'Grade 1 rate?')..."):
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing Pay Guide..."):
            try:
                # Construct the conversation history to send to Gemini
                # This allows the AI to remember the previous context
                history_context = "History of conversation:\n"
                for msg in st.session_state.messages:
                    history_context += f"{msg['role'].upper()}: {msg['content']}\n"
                
                # Send the PDF + History + New Question
                response = model.generate_content([sample_file, history_context, prompt])
                
                # Display AI Message
                st.markdown(response.text)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Error: {e}")
