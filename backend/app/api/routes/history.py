from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User, Verification
from app.schemas.prediction import HistoryResponse

router = APIRouter(tags=["history"])

@router.get("/history", response_model=HistoryResponse)
def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Verification).where(Verification.user_id == user.id).order_by(Verification.created_at.desc()).limit(limit)
    return {"items": db.execute(stmt).scalars().all()}
