"""Account registration and cookie-based authentication."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.rate_limit import enforce_rate_limit
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import AuthRequest, AuthResponse

router = APIRouter(prefix="/auth", tags=["authentication"])
_COOKIE = "access_token"

def _set_session(response: Response, user: User) -> None:
    settings = get_settings()
    response.set_cookie(
        key=_COOKIE, value=create_access_token(user.id), httponly=True,
        secure=settings.use_secure_cookies, samesite="strict",
        max_age=settings.access_token_minutes * 60, path="/",
    )

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: Request, payload: AuthRequest, response: Response, db: Session = Depends(get_db)):
    enforce_rate_limit(request, "auth-register", 5)
    email = str(payload.email).lower().strip()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(id=str(uuid.uuid4()), email=email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists") from None
    db.refresh(user)
    _set_session(response, user)
    return {"user": user}

@router.post("/login", response_model=AuthResponse)
def login(request: Request, payload: AuthRequest, response: Response, db: Session = Depends(get_db)):
    enforce_rate_limit(request, "auth-login", 10)
    email = str(payload.email).lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account is disabled")
    _set_session(response, user)
    return {"user": user}

@router.get("/me", response_model=AuthResponse)
def me(user: User = Depends(get_current_user)):
    return {"user": user}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=_COOKIE, path="/", httponly=True, secure=get_settings().use_secure_cookies, samesite="strict")
    return {"status": "logged_out"}
