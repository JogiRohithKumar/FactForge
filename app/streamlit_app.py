import streamlit as st
import requests
import os
import sys

# 1. Page Configuration
st.set_page_config(page_title="FactForge Pro", page_icon="📰", layout="centered")

# 2. Injecting Glassmorphism Custom CSS Layer
st.markdown("""
    <style>
    /* Main Background Custom Styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }
    
    /* Global Glassmorphic Card Styling applied to UI Blocks */
    div.stButton > button, div[data-testid="stMarkdownContainer"] h3 {
        font-family: 'Inter', sans-serif;
    }
    
    /* Designing Custom Frosted Glass Panels for Results */
    .glass-panel {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Polishing Text Area Focus Layout */
    textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
    }
    
    /* Primary Action Trigger Custom Glass Button */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(168, 85, 247, 0.8) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        padding: 10px 24px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Safe Import of Backend Service as a Fallback
try:
    sys.path.append(os.getcwd())
    from api.service import get_prediction, extract_text_from_url
except ImportError:
    get_prediction = None
    extract_text_from_url = None

st.title("📰 FactForge Pro")
st.subheader("Production-Grade Misinformation Detection SaaS")
st.markdown("---")

# Initialize State Management for User History
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar User Workspace
st.sidebar.title("👤 User Workspace")
st.sidebar.markdown("---")
st.sidebar.subheader("Recent Verifications")
if not st.session_state.history:
    st.sidebar.info("No articles verified in this session.")
else:
    for item in reversed(st.session_state.history):
        st.sidebar.write(item)

# Create Tabs for Ingestion Modes
tab1, tab2 = st.tabs(["🔗 Verify via URL", "📝 Verify via Text"])

data = None
input_source = ""

with tab1:
    url_input = st.text_input("Enter the full news article URL:", placeholder="https://www.reuters.com/article...")
    if st.button("Analyze Link", key="url_btn"):
        if not url_input.strip():
            st.warning("Please enter a valid URL.")
        else:
            # Clean up URL string display for history log snippet
            input_source = url_input.replace("https://", "").replace("www.", "")[:25] + "..."
            with st.spinner("Extracting content from web page and running NLP inference..."):
                try:
                    response = requests.post("http://127.0.0.1:8000/predict-url", json={"url": url_input}, timeout=7)
                    if response.status_code == 200:
                        data = response.json()
                except requests.exceptions.RequestException:
                    data = None

                if data is None and extract_text_from_url is not None and get_prediction is not None:
                    try:
                        text = extract_text_from_url(url_input)
                        data = get_prediction(text)
                    except Exception as e:
                        st.error(f"Scraping Engine failed: {e}")

with tab2:
    text_input = st.text_area("Paste the news article content here:", height=200, placeholder="Type or paste text here...")
    if st.button("Analyze Text", key="text_btn"):
        if not text_input.strip():
            st.warning("Please enter some text.")
        else:
            input_source = text_input[:20] + "..."
            with st.spinner("Running statistical NLP inference..."):
                try:
                    response = requests.post("http://127.0.0.1:8000/predict", json={"text": text_input}, timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                except requests.exceptions.RequestException:
                    data = None

                if data is None and get_prediction is not None:
                    data = get_prediction(text_input)

# Render Glassmorphic Results Panel (FIXED IMPLEMENTATION)
if data is not None:
    is_fake = data["is_fake"]
    confidence = data["confidence"]
    
    result_label = "🚨 Fake News Pattern Found" if is_fake else "✅ Verified Authentic Content"
    st.session_state.history.append(f"{'❌ Fake' if is_fake else '🟢 True'} ({confidence}%) - {input_source}")
    
    # Wrapping results in a custom glass container panel
    st.markdown(f"""
        <div class="glass-panel">
            <h3 style="color: white; margin-top: 0;">📊 Real-Time Analysis Report</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem; margin-bottom: 20px;">
                The structural profile of this article was validated across cross-referenced corpora weights using our NLP pipeline.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Explicitly separate column rendering logic to clear DeltaGenerator bugs
    col1, col2 = st.columns(2)
    with col1:
        if is_fake:
            st.error(result_label)
        else:
            st.success(result_label)
            
    with col2:
        st.metric(label="Model Confidence Score", value=f"{confidence}%")
        
elif input_source:
    st.error("🔌 System Connection Failure: Unable to parse URL content or connect to the model service.")