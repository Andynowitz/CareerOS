from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.user import CurrentUserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status", response_model=CurrentUserResponse)
async def auth_status(
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> CurrentUserResponse:
    return current_user