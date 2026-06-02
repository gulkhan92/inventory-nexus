from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user
from app.models.domain import User
from app.schemas.domain import SupersetGuestToken
from app.services.superset import create_guest_token

router = APIRouter(prefix="/superset", tags=["superset"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/guest-token", response_model=SupersetGuestToken)
def guest_token(current_user: CurrentUser) -> SupersetGuestToken:
    return SupersetGuestToken(token=create_guest_token(current_user))
