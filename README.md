# FactForge — Full-Stack Migration

Migrated from a single Streamlit app into a decoupled FastAPI backend +
Next.js/TypeScript frontend. This README documents what changed and why,
and what's needed to get it running.

## What changed from the original Streamlit version

| Area | Before | After |
|---|---|---|
| URL analysis | `/predict-url` was called by the UI but never existed in the API — every URL check silently fell through to an in-process fallback | `/predict-url` is implemented and actually used |
| SSRF | Any user-supplied URL was fetched server-side with no validation | Scheme allowlist (http/https only) + DNS resolution check that rejects private/loopback/link-local/reserved IP ranges before connecting; redirects are not auto-followed |
| Model loading | `joblib.load()` at import time — a missing/bad model file crashed the whole process | Lazy-loaded singleton with error handling; `/health` reports `model_loaded` instead of the server being dead |
| History | In-memory `st.session_state`, lost on refresh | Persisted to SQLite via SQLAlchemy, served through `GET /history` |
| Errors | Unhandled exceptions could leak stack traces via FastAPI's default 500 | Caught and mapped to appropriate status codes (400/422/503/500) with safe messages |
| Input validation | None (empty strings, oversized payloads accepted) | Pydantic validators: min/max text length, URL shape check |
| UI | Streamlit + injected CSS | Next.js App Router + Tailwind, custom design system (see below) |
| Config | Hardcoded `127.0.0.1:8000` and ad hoc cloud-detection heuristics | Environment-variable driven (`.env` files), no environment sniffing |

## Design direction

The interface leans into a "case file" metaphor — each check gets logged
like an exhibit, with a circular verdict dial (styled like an analog
gauge/rubber stamp) as the signature element, rather than a generic
dashboard donut chart. Palette: deep ink-navy surfaces, amber "evidence
highlighter" accent, verified-green / flagged-red status colors. Type:
Fraunces (display/italic) for authority, Inter for body/UI, IBM Plex Mono
for data (confidence scores, timestamps, case IDs).

## Project layout

```
factforge/
├── backend/            FastAPI app
│   ├── app/
│   │   ├── main.py
│   │   ├── core/        config, logging
│   │   ├── api/routes/  predict.py, history.py
│   │   ├── services/    ml_service.py, scraper.py
│   │   ├── db/          SQLAlchemy models + session
│   │   ├── schemas/     Pydantic request/response models
│   │   └── model/       <-- put fake_news_model.pkl + tfidf_vectorizer.pkl here
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            Next.js 14 + TypeScript + Tailwind
│   ├── app/              pages, layout, global styles
│   ├── components/       AnalyzerCard, ResultPanel, VerdictDial, HistorySidebar, Navbar
│   ├── lib/               api client, types
│   └── Dockerfile
├── ml/                   offline training pipeline (unchanged logic, path-robust)
│   ├── data_preparation.py
│   └── model_training.py
└── docker-compose.yml
```

## ⚠️ About the model in this repo

`backend/app/model/*.pkl` **is a working model, but it's trained on synthetic, template-generated data** (`ml/generate_demo_data.py`) — fictional topics, no real people or events. This exists so you can run the whole pipeline (train → save → load → predict → serve) and confirm it actually works, which it does — verified directly against the saved artifacts:

```
predict("SHOCKING: ... secretly planned this for YEARS ...")  → is_fake: True,  confidence: 89.09%
predict("Officials from ... announced on Tuesday that ...")   → is_fake: False, confidence: 89.48%
```

**This is not a real misinformation detector yet.** The synthetic data has artificially clean class separation (100% held-out accuracy — a real dataset will never look like this). Do not cite this model's accuracy as meaningful. Before using this for anything real:

1. Download the real dataset (e.g. the ISOT "Fake and Real News" dataset on Kaggle — search "fake news detection datasets" on Kaggle, or use whatever labeled dataset you originally trained on).
2. Place `fake.csv` / `true.csv` in `ml/data/` (columns: `title`, `text`).
3. Run `python ml/data_preparation.py` then `python ml/model_training.py` (the nltk-based version — install `nltk` and run once with network access so `nltk.download('stopwords')` succeeds).
4. This overwrites `backend/app/model/*.pkl` with the real trained artifacts.

**Version pinning matters here:** `requirements.txt` pins `scikit-learn==1.8.0` / `joblib==1.5.3` / `pandas==3.0.2` / `numpy==2.4.4` to match whatever produced the checked-in `.pkl` files. If you retrain with different library versions, either update these pins to match, or re-pickle isn't guaranteed to load — a version mismatch here is a silent unpickling failure, not a clear error.

## Running locally

A working (synthetic-data) model already ships in `backend/app/model/` — see the warning above. You can run the app immediately; swap in real training data later using the steps above.

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
API docs: `http://127.0.0.1:8000/docs`. Check `http://127.0.0.1:8000/health`
to confirm the model loaded.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```
UI: `http://localhost:3000`

### Or with Docker

```bash
docker compose up --build
```

## Testing instructions

- `GET /health` → `{"status": "ok", "model_loaded": true}` once artifacts are in place.
- `POST /predict` with `{"text": "..."}` (≥20 chars) → prediction + persisted history row.
- `POST /predict-url` with `{"url": "https://..."}` → same, after live scraping.
- Try `{"url": "http://169.254.169.254/"}` → should be rejected with a 400 (SSRF check working).
- Try `{"text": "short"}` → should be rejected with a 422 (validation working).
- Frontend: submit a link or text, confirm the verdict dial renders, and confirm the case log sidebar updates.

## Known gaps / recommended next steps

1. **DNS-rebinding hardening**: the SSRF check validates the resolved IP before connecting, but doesn't pin that IP into the actual TCP connection — a fuller fix uses a custom `requests` transport that connects to the pre-validated IP directly.
2. **Authentication**: there's no user system yet. History is currently global, not per-user. Worth adding if this becomes multi-tenant.
3. **Rate limiting**: not yet implemented on `/predict` / `/predict-url` — recommended before any public deployment, since URL fetching is inherently abusable as a proxy.
4. **Alembic migrations**: currently using `Base.metadata.create_all()` for simplicity; add Alembic once the schema needs to evolve without dropping data.
5. **Automated tests**: none yet — pytest for the backend (especially the SSRF validator and prediction error paths) would be the highest-value addition.
