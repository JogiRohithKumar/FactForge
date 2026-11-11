from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from urllib.parse import urlsplit
from app.api.routes import analysis, auth, history, predict
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.core.rate_limit import check_redis
from app.db.database import engine
from sqlalchemy import text
from app.schemas.prediction import HealthResponse
from app.services.ml_service import registry

configure_logging()
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.is_production and (settings.jwt_secret_key == "local-development-only-change-this-secret" or len(settings.jwt_secret_key.encode("utf-8")) < 32):
        raise RuntimeError("JWT_SECRET_KEY must be a unique secret of at least 32 bytes in production")
    yield

app = FastAPI(title=settings.app_name, description="Evidence-aware claim research and language-pattern analysis API", version="1.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origins,
    allow_credentials=True, allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)

_ALLOWED_ORIGINS = {origin.rstrip("/") for origin in settings.cors_origins}

@app.middleware("http")
async def enforce_request_origin(request, call_next):
    # Browser state-changing requests carry Origin. Validate it independently
    # of CORS so simple form submissions cannot bypass the browser policy.
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if not origin:
            referer = request.headers.get("referer")
            if referer:
                parsed = urlsplit(referer)
                origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else None
        if origin and origin.rstrip("/") not in _ALLOWED_ORIGINS:
            return JSONResponse(status_code=403, content={"detail": "Request origin is not allowed"})
    return await call_next(request)

@app.get("/", tags=["meta"])
def root():
    return {"name": "FactForge", "status": "running", "api_version": "v1"}

@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health():
    return {"status": "ok", "model_loaded": registry.is_loaded}

@app.get("/ready", tags=["meta"])
def readiness():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        check_redis()
    except Exception:
        raise HTTPException(status_code=503, detail="A required dependency is unavailable") from None
    return {"status": "ready", "model_loaded": registry.is_loaded}

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(history.router)
app.include_router(analysis.router)
