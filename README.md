# FactForge

FactForge is an evidence-aware article and claim research application. It accepts article text or a URL, extracts candidate claim sentences, searches for previously published fact-check reviews, and discovers related web sources. The legacy TF-IDF classifier is retained only as a separate language-pattern signal; it is not a factual truth detector.

## Product semantics

- **Existing review found** means the configured fact-check provider returned a review matching a candidate sentence. The displayed stance is the review publisher's own textual rating mapped to a cautious category. It is not FactForge's independent finding.
- **Research sources** are search results for manual investigation. A government/education domain label is a URL-domain heuristic, not proof of authenticity, primary-source status or claim support.
- **Insufficient evidence** means no matching fact-check review was returned. It does not mean the claim is true, false or trustworthy.
- **Language-pattern signal** is the legacy classifier output. Its score is not a calibrated probability of truth.

The product must not convert an absent match, a style classifier score or a search result into a factual verdict.

## Architecture

```text
Next.js application
  -> HttpOnly cookie session (register/login/logout)
  -> FastAPI
       -> Authentication dependency + account-scoped history
       -> Redis-backed per-IP request limits
       -> URL extraction with DNS validation and socket IP pinning
       -> conservative sentence-level claim candidate extraction
       -> optional TF-IDF language-pattern signal
       -> evidence providers
            -> Google Fact Check Tools: existing review search
            -> Tavily Search: related web-source discovery and bounded page excerpts
       -> Hugging Face BART-MNLI: optional top-source relation signal
       -> attributed review-rating mapping + abstention
       -> structured report with links, publisher stance and limitations
  -> SQLAlchemy + PostgreSQL (Docker) / SQLite (local)
  -> Alembic schema migrations
```

The codebase remains a modular monolith. Redis is used for shared rate-limit counters, not as a job queue. Distributed workers and microservices are deferred until throughput and operational requirements justify them.

## Implemented

### Phase 1 — engineering foundation
- Training and inference share one text normalization function.
- Lazy model loading is optional; evidence analysis can continue when the model is unavailable.
- Backend regression tests and GitHub Actions CI.
- Docker volume layout no longer mounts over the application directory.
- PostgreSQL and Redis services have health checks.
- Backend and frontend production containers run as non-root users.
- Environment examples and Docker build hygiene.

### Phase 2 — evidence-aware workflow
- Versioned API routes: `POST /api/v1/analyze/text` and `POST /api/v1/analyze/url`.
- Conservative candidate sentence extraction.
- Optional Google Fact Check Tools adapter returns the review publisher, title, rating, date and original URL.
- Optional Tavily Search adapter discovers related web sources and bounded page excerpts.
- Publisher ratings are mapped into attributed true/false/mixed/unclear categories. Unknown ratings abstain.
- Optional Hugging Face `facebook/bart-large-mnli` zero-shot NLI classifies the top-ranked source excerpt per candidate as supporting, contradicting or insufficient; low-margin predictions abstain. The model score is uncalibrated and is shown as an experimental relation signal, never a truth verdict.
- Frontend separates fact-check reviews from research leads and classifier output.
- Missing review matches are explicitly reported as insufficient evidence.

### Phase 3 — identity, data isolation and operational security
- Email/password registration and login with Argon2 password hashing.
- Short-lived signed session in an HttpOnly, SameSite=Strict cookie; browser JavaScript does not read the session token.
- Analysis, legacy prediction and history endpoints require an authenticated account.
- Every new history row is associated with its account; history queries filter by that account. Legacy pre-migration rows remain unowned and are not exposed to any account.
- Redis-backed fixed-window per-IP limits on registration, login and analysis routes. The limiter fails closed if Redis is unavailable.
- Alembic migration adds users and nullable ownership to existing history; Docker runs migrations before starting the API.
- URL fetcher validates public DNS answers and pins the selected address into the actual HTTP/TLS socket connection. Original hostname remains in Host/SNI for certificate validation. Redirects are manually revalidated, proxy environment inheritance is disabled and response bytes are capped.
- Frontend sends cookies with credentialed requests; CORS is restricted to configured origins.
- Production startup refuses the known development JWT secret.

### Phase 4 — evidence retrieval and assessment foundation
- Fact-check provider matches are surfaced with original review attribution.
- Review-rating mapper categorizes the publisher's own stance and abstains on unknown or mixed ratings.
- Tavily source discovery returns source title, URL, snippet and relevance score.
- A URL-domain heuristic flags potential official domains for manual inspection only.
- The system does **not** claim to perform independent semantic entailment/contradiction yet. Search relevance and publisher ratings are not enough to prove that a candidate claim is supported by primary evidence.

## Configuration

Copy root `.env.example` to `.env`. Use long random alphanumeric values for `POSTGRES_PASSWORD` and a separate random secret of at least 32 bytes for `JWT_SECRET_KEY`. The database URL in Compose interpolates the password, so keep it URL-safe (alphanumeric is the simplest choice).

Optional external providers:
- `GOOGLE_FACT_CHECK_API_KEY` enables existing fact-check review search.
- `TAVILY_API_KEY` enables web-source discovery and bounded source excerpts.
- `HUGGINGFACE_API_TOKEN` enables the optional MNLI relation signal over the top retrieved source excerpt for each candidate claim. This can incur inference usage charges.

If a provider key is absent, that provider is skipped and the API reports the missing capability in the analysis limitations. The API remains usable without external provider credentials.

## Run with Docker

```bash
cp .env.example .env
# Edit .env and set strong POSTGRES_PASSWORD and JWT_SECRET_KEY values.
docker compose up --build
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Liveness: http://localhost:8000/health
- Readiness: http://localhost:8000/ready

The Compose frontend build uses `NEXT_PUBLIC_API_URL=http://localhost:8000`. Change the build argument for a deployed environment so the browser can reach the public API origin. Set `CORS_ORIGINS` to the exact frontend origin in that environment.

## Local development

Backend (from `backend/`):

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

The local default database is SQLite. Redis is required for registration, login and rate-limited analysis routes; start a local Redis instance and set `REDIS_URL` accordingly.

Frontend (from `frontend/`):

```bash
npm install
npm run typecheck
npm run dev
```

## Tests and validation

Backend:

```bash
cd backend
PYTHONPATH=. pytest -q
```

Frontend:

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

GitHub Actions runs backend tests and frontend typecheck/build on pushes and pull requests.

## Remaining production work — do not treat this as fully launch-ready

1. **Independent evidence assessment:** add primary-source retrieval (not just general web search), source authenticity checks, evidence passage extraction, temporal/context alignment and a validated NLI/LLM entailment/contradiction model with calibrated abstention.
2. **Human review:** queue uncertain, high-impact and conflicting cases for editorial adjudication and audit trails.
3. **Account lifecycle:** email verification, password reset, session revocation/rotation, account deletion and privacy retention controls.
4. **CSRF and deployment controls:** the API validates browser Origin/Referer headers against configured origins; also enforce trusted-origin/CSRF policy at the edge, deploy frontend/API on the same site, use HTTPS, configure secure cookies and verify reverse-proxy trust boundaries.
5. **Abuse and resilience:** account-based quotas, request body limits at the reverse proxy, provider budgets, circuit breakers and retry/backoff policies.
6. **Operations:** structured metrics/tracing, error reporting, backups/restore drills, dependency scanning, SBOM, secret rotation and load/security testing.
7. **ML evaluation:** replace synthetic demo model claims with audited real datasets, source/time-separated evaluation, calibration, drift monitoring and model registry.

## Known limitations

- Candidate extraction is sentence splitting, not semantic claim decomposition.
- Fact-check search matches may be approximate or outdated.
- Tavily results are research leads, not validated primary evidence.
- The official-domain label is heuristic only.
- Rating mapping reflects the review publisher's vocabulary, which differs across fact-check organizations.
- No independent entailment/contradiction model or human review workflow is implemented.
- Rate limiting is IP-based; account-based quotas and reverse-proxy trust configuration remain.
- The cookie session uses SameSite=Strict. The local Compose profile disables the Secure cookie flag because it serves plain HTTP on localhost; real deployments must enable COOKIE_SECURE=true and serve the UI/API over HTTPS. Cross-site frontend/API deployments require a deliberate CSRF-protected cookie design.
- The checked-in synthetic classifier model is only a pipeline demonstration and must not be presented as a production misinformation detector.
