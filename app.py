import streamlit as st
import google.generativeai as genai

st.title("🔍 Model Diagnostic Tool")

try:
    # Configure API
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    st.write("Checking available models for your API key...")
    
    # Ask Google: "What models can I use?"
    models = genai.list_models()
    
    found_any = False
    for m in models:
        # We only care about models that can 'generateContent'
        if 'generateContent' in m.supported_generation_methods:
            st.success(f"✅ AVAILABLE: {m.name}")
            found_any = True
            
    if not found_any:
        st.error("No compatible models found. Your API key might be restricted.")

except Exception as e:
    st.error(f"Error: {e}")
