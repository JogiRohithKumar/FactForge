import streamlit as st
import requests
import multiprocessing
import uvicorn
import time
import os
import sys

# 1. Background Process to run FastAPI inside Streamlit Cloud
def run_backend():
    # Adds the root path to python path so it can find 'api'
    sys.path.append(os.getcwd())
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="warning")

# Start FastAPI in a background thread if it's not running
if 'backend_started' not in st.session_state:
    backend_process = multiprocessing.Process(target=run_backend, daemon=True)
    backend_process.start()
    st.session_state.backend_started = True
    time.sleep(2) # Give the API a brief moment to boot up safely

# 2. Page Configuration
st.set_page_config(page_title="FactForge Pro", page_icon="📰", layout="centered")

st.title("📰 FactForge Pro")
st.subheader("Production-Grade Misinformation Detection SaaS")

# 3. State Management for User History
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar for displaying user history session
st.sidebar.title("👤 User Workspace")
st.sidebar.markdown("---")
st.sidebar.subheader("Recent Verifications")

if not st.session_state.history:
    st.sidebar.info("No articles verified in this session.")
else:
    for item in reversed(st.session_state.history):
        st.sidebar.write(item)

# 4. Main Input Interface
user_input = st.text_area(
    "Paste the news article content below for real-time validation:", 
    height=200,
    placeholder="Type or paste text here..."
)

# 5. Connect Frontend to FastAPI Backend Service
if st.button("Analyze Article", type="primary"):
    if not user_input.strip():
        st.warning("Please enter some text before processing.")
    else:
        with st.spinner("Running text parsing and statistical NLP inference..."):
            try:
                payload = {"text": user_input}
                response = requests.post("http://127.0.0.1:8000/predict", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    is_fake = data["is_fake"]
                    confidence = data["confidence"]
                    
                    result_label = "🚨 Fake News Pattern Found" if is_fake else "✅ Verified Authentic Content"
                    history_snippet = f"{'❌ Fake' if is_fake else '🟢 True'} ({confidence}%) - {user_input[:15]}..."
                    
                    st.session_state.history.append(history_snippet)
                    
                    st.markdown("### 📊 Analysis Report")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if is_fake:
                            st.error(result_label)
                        else:
                            st.success(result_label)
                            
                    with col2:
                        st.metric(label="Model Confidence Score", value=f"{confidence}%")
                else:
                    st.error(f"Backend API error code: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🔌 System Connection Failure: Backend microservice thread is still booting up. Please wait 5 seconds and try again!")