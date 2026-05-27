from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.v1.deps import DbSession
from app.core.security import create_access_token, verify_password
from app.models.domain import User
from app.schemas.domain import LoginRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: DbSession) -> Token:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.email))
