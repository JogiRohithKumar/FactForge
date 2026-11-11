import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.rate_limit import enforce_rate_limit
from app.db.database import get_db
from app.db.models import User, Verification
from app.schemas.prediction import PredictionResponse, TextRequest, UrlRequest
from app.services.ml_service import ModelUnavailableError, get_prediction
from app.services.scraper import ExtractionError, UnsafeUrlError, extract_text_from_url

logger = logging.getLogger(__name__)
router = APIRouter(tags=["prediction"])

def _preview(text: str, limit: int = 160) -> str:
    text = text.strip().replace("\n", " ")
    return text[:limit] + ("..." if len(text) > limit else "")

def _persist(db: Session, user: User, *, source_type: str, preview: str, result: dict) -> Verification:
    record = Verification(user_id=user.id, source_type=source_type, source_preview=preview, is_fake=result["is_fake"], confidence=result["confidence"])
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.post("/predict", response_model=PredictionResponse)
def predict_text(request: Request, payload: TextRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "legacy-prediction", 20)
    try:
        result = get_prediction(payload.text)
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Prediction model is currently unavailable") from exc
    except Exception:
        logger.exception("Unexpected error during text prediction")
        raise HTTPException(status_code=500, detail="Prediction failed unexpectedly") from None
    return _persist(db, user, source_type="text", preview=_preview(payload.text), result=result)

@router.post("/predict-url", response_model=PredictionResponse)
def predict_url(request: Request, payload: UrlRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "legacy-url-prediction", 10)
    try:
        article_text = extract_text_from_url(payload.url)
    except UnsafeUrlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        result = get_prediction(article_text)
    except ModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Prediction model is currently unavailable") from exc
    except Exception:
        logger.exception("Unexpected error during URL prediction")
        raise HTTPException(status_code=500, detail="Prediction failed unexpectedly") from None
    return _persist(db, user, source_type="url", preview=_preview(payload.url), result=result)
