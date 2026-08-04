from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import history, predict
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.db.database import init_db
from app.schemas.prediction import HealthResponse
from app.services.ml_service import registry

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Fake-news / misinformation detection API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", tags=["meta"])
async def root():
    return {"message": f"{settings.app_name} is running"}


@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health():
    return {"status": "ok", "model_loaded": registry.is_loaded}


app.include_router(predict.router)
app.include_router(history.router)
