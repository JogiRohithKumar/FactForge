# =====================================================================
# STAGE 1: Dependency Builder
# =====================================================================
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# Install system compilation dependencies required for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependency manifests
COPY requirements.txt .

# Install dependencies into a localized directory path to transfer over later
RUN pip install --no-cache-dir --user -r requirements.txt

# Download required static NLTK corpora packages ahead of runtime execution
RUN python -m nltk.downloader punkt stopwords

# =====================================================================
# STAGE 2: Final Production Runtime Container Image
# =====================================================================
FROM python:3.11-slim-bookworm AS runner

WORKDIR /workspace

# Prevent python from writing pyc artifacts to disk and force unbuffered log outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

# Copy installed python dependencies from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/nltk_data /root/nltk_data

# Update path execution maps to access the builder binaries cleanly
ENV PATH=/root/.local/bin:$PATH

# Transfer the core application codebase directories over
COPY api/ ./api/
COPY app/ ./app/
COPY utils/ ./utils/
COPY model/ ./model/

# Expose network communication ports for both FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Container initialization instructions are dynamically handled via docker-compose commands