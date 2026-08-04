import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Verification
from app.schemas.prediction import PredictionResponse, TextRequest, UrlRequest
from app.services.ml_service import ModelUnavailableError, get_prediction
from app.services.scraper import ExtractionError, UnsafeUrlError, extract_text_from_url

logger = logging.getLogger(__name__)
router = APIRouter(tags=["prediction"])


def _preview(text: str, limit: int = 160) -> str:
    text = text.strip().replace("\n", " ")
    return text[:limit] + ("..." if len(text) > limit else "")


def _persist(db: Session, *, source_type: str, preview: str, result: dict) -> Verification:
    record = Verification(
        source_type=source_type,
        source_preview=preview,
        is_fake=result["is_fake"],
        confidence=result["confidence"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/predict", response_model=PredictionResponse)
async def predict_text(request: TextRequest, db: Session = Depends(get_db)):
    try:
        result = get_prediction(request.text)
    except ModelUnavailableError as e:
        logger.error("Model unavailable: %s", e)
        raise HTTPException(status_code=503, detail="Prediction model is currently unavailable") from e
    except Exception:
        logger.exception("Unexpected error during text prediction")
        raise HTTPException(status_code=500, detail="Prediction failed unexpectedly") from None

    record = _persist(db, source_type="text", preview=_preview(request.text), result=result)
    return record


@router.post("/predict-url", response_model=PredictionResponse)
async def predict_url(request: UrlRequest, db: Session = Depends(get_db)):
    try:
        article_text = extract_text_from_url(request.url)
    except UnsafeUrlError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    try:
        result = get_prediction(article_text)
    except ModelUnavailableError as e:
        logger.error("Model unavailable: %s", e)
        raise HTTPException(status_code=503, detail="Prediction model is currently unavailable") from e
    except Exception:
        logger.exception("Unexpected error during URL prediction")
        raise HTTPException(status_code=500, detail="Prediction failed unexpectedly") from None

    record = _persist(db, source_type="url", preview=_preview(request.url), result=result)
    return record
