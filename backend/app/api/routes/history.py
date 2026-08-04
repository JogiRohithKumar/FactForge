from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Verification
from app.schemas.prediction import HistoryResponse

router = APIRouter(tags=["history"])


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Verification).order_by(Verification.created_at.desc()).limit(limit)
    items = db.execute(stmt).scalars().all()
    return {"items": items}
