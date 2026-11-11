"""Authenticated evidence-led article analysis endpoint."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.rate_limit import enforce_rate_limit
from app.db.database import get_db
from app.db.models import User, Verification
from app.schemas.analysis import AnalysisReport
from app.schemas.prediction import TextRequest, UrlRequest
from app.services.scraper import extract_text_from_url, UnsafeUrlError, ExtractionError
from app.services.verification_service import analyze

router = APIRouter(prefix="/api/v1", tags=["evidence-analysis"])

@router.post("/analyze/text", response_model=AnalysisReport)
def analyze_text(request: Request, payload: TextRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "analysis", 20)
    report = analyze(payload.text, "text", payload.text.strip()[:160])
    _save_history(db, user, "text", payload.text.strip()[:160], report)
    return report

@router.post("/analyze/url", response_model=AnalysisReport)
def analyze_url(request: Request, payload: UrlRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "analysis", 10)
    try:
        article = extract_text_from_url(payload.url)
    except UnsafeUrlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    report = analyze(article, "url", payload.url[:160])
    _save_history(db, user, "url", payload.url[:160], report)
    return report

def _save_history(db: Session, user: User, source_type: str, preview: str, report: AnalysisReport):
    db.add(Verification(
        user_id=user.id, source_type=source_type, source_preview=preview,
        is_fake=report.article_classifier_signal == "misleading_pattern",
        confidence=report.classifier_score or 0.0,
        error=None if report.overall_status == "evidence_found" else "insufficient_evidence",
    ))
    db.commit()
