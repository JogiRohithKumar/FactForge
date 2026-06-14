# 📰 FactForge Pro: Production-Grade Misinformation Detection SaaS

FactForge Pro is a decoupled, microservice-driven SaaS application that utilizes Natural Language Processing (NLP) and Machine Learning to conduct real-time credibility assessments on news content. Built with a high-performance **FastAPI** backend and an interactive **Streamlit** frontend, the platform features a multi-engine web scraping ingestion pipeline and a resilient, dual-mode cloud failover engine designed to handle real-world deployment constraints.

🚀 **Live Deployment Link:** [try-fake-news-detector.streamlit.app](https://try-fake-news-detector.streamlit.app/)

---

## 🛠️ System Architecture & Engineering Blueprint

The platform is engineered using a decoupled architecture, completely isolating the user interface from the core machine learning inference engine. This microservice design pattern ensures high scalability, clear separation of concerns, and ease of deployment.


```

[ Frontend: Streamlit Dashboard ]
│
├── Mode 1: REST API (Local Dev Engine) ──► [ Backend: FastAPI Server ] ──► [ Model Inference ]
│                                                                                ▲
└── Mode 2: In-Process Failover Engine ──────────────────────────────────────────┘
(Bypasses Browser Cloud Sandbox Restrictions)

```

### Key Architectural Pillars:
* **Decoupled Microservice Layer:** Core text tokenization, TF-IDF vector extraction, and machine learning inference are exposed via high-throughput REST endpoints (`/predict` and `/predict-url`) using **FastAPI** and **Uvicorn**.
* **Resilient Dual-Mode Execution Engine:** To counter strict browser container sandbox restrictions (`allow-scripts` / `allow-same-origin`) embedded in production cloud runtimes like Streamlit Cloud, the application implements an automated runtime failover switch. If port communication is blocked, the frontend gracefully pivots to an in-process execution layer.
* **Multi-Engine Content Ingestion:** Implements a multi-engine live scraping pipeline (**Newspaper3k** + **BeautifulSoup4**) reinforced with advanced human-mimicking header stacks (`User-Agent`, `Accept-Language`, `Referer`) to gracefully extract clean text content from web URLs while navigating anti-bot CDN firewalls.

---

## 🔬 Machine Learning Pipeline & Implementation

The core intelligence layer processes unstructured textual data through a rigorous mathematical and linguistic pipeline:

1. **Text Preprocessing (NLTK):** Raw inputs are downcased and tokenized using the NLTK `punkt` engine to decouple linguistic structural artifacts from statistical calculations.
2. **Feature Extraction (TF-IDF Vectorization):** Cleaned text sequences are transformed into high-dimensional numerical sparse matrices using Term Frequency-Inverse Document Frequency (TF-IDF). This captures vocabulary relative significance across corpus distributions.
3. **Statistical Inference (Logistic Regression):** A Scikit-Learn `LogisticRegression` model analyzes vector weights to output absolute binary classifications alongside explicit probability confidence scores via `predict_proba`.

### Performance Metrics:
* **Classification Accuracy:** `99.8%` on baseline benchmark data distributions.
* **Interview Insight (Data Drift Note):** Real-world evaluation of highly compressed, summarized short-form content structures (e.g., localized platform snippets) may surface syntax shifts yielding lower confidence profiles. This project serves as an excellent case study in managing model feature boundaries post-production.

---

## 💻 Tech Stack Summary

* **Frontend Engine:** Streamlit, Custom Embedded HTML5/CSS3 (Glassmorphism UI Engine)
* **Backend API Framework:** FastAPI, Uvicorn, Pydantic
* **Data Processing & ML:** Scikit-Learn, Joblib, Pandas, NumPy
* **Natural Language Processing:** NLTK (Natural Language Toolkit)
* **Web Scraping Infrastructure:** Newspaper3k, BeautifulSoup4, Requests

---

## 🚀 Local Installation & Developer Setup

Follow these steps to run the complete microservice architecture on your local machine:

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/fake-news-detector.git](https://github.com/YOUR_USERNAME/fake-news-detector.git)
cd fake-news-detector

```

### 2. Set Up a Virtual Environment & Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt

```

### 3. Launch the Backend REST API Service

Start the FastAPI server with explicit reload exclusion constraints to avoid virtual environment watch loops:

```bash
uvicorn api.main:app --reload --reload-exclude ".venv/*" --reload-exclude "**/__pycache__/*"

```

The API documentation will be interactively accessible at `http://127.0.0.1:8000/docs`.

### 4. Launch the Frontend Dashboard Interface

In a separate terminal tab, run the Streamlit application:

```bash
streamlit run app/streamlit_app.py

```

Open `http://localhost:8501` in your browser to interact with the full premium glassmorphic UI.

---

## 🎨 Premium UI Polish: Glassmorphism Design

Rather than utilizing basic UI primitives, the user interface features a specialized **Frosted Glass (Glassmorphism)** architecture. By injecting custom scoped CSS style rules into the browser DOM engine, the app delivers a modern SaaS dashboard look, utilizing high-contrast focus elements, smooth hover transitions, real-time status spinners, and a stateful contextual workspace side drawer tracking verification history.



