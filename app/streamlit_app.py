import streamlit as st
import requests
import os
import sys

# Page Configuration (Must be first)
st.set_page_config(page_title="FactForge Pro", page_icon="📰", layout="centered")

# Safe Import of Backend Service as a Fallback
try:
    sys.path.append(os.getcwd())
    from api.service import get_prediction
except ImportError:
    get_prediction = None

st.title("📰 FactForge Pro")
st.subheader("Production-Grade Misinformation Detection SaaS")

# Initialize State Management for User History
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

# Main Input Interface
user_input = st.text_area(
    "Paste the news article content below for real-time validation:", 
    height=200,
    placeholder="Type or paste text here..."
)

if st.button("Analyze Article", type="primary"):
    if not user_input.strip():
        st.warning("Please enter some text before processing.")
    else:
        with st.spinner("Running text parsing and statistical NLP inference..."):
            data = None
            
            # Mode 1: Attempt to communicate via Microservice (FastAPI Local Engine)
            try:
                payload = {"text": user_input}
                response = requests.post("http://127.0.0.1:8000/predict", json=payload, timeout=2)
                if response.status_code == 200:
                    data = response.json()
            except requests.exceptions.RequestException:
                # API is down or restricted by cloud provider environment
                data = None

            # Mode 2: Cloud Fallback Engine (Runs the service directly)
            if data is None and get_prediction is not None:
                try:
                    data = get_prediction(user_input)
                except Exception as e:
                    st.error(f"Prediction processing error: {e}")

            # Render Results if Inferences Succeeded
            if data is not None:
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
                st.error("🔌 System Connection Failure: Unable to compute model inference via API or local fallback engine.")