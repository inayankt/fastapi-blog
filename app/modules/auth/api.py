from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from auth import oauth2_scheme
from modules.auth.dependencies import get_auth_service
from modules.auth.schemas import Token
from modules.auth.service import AuthService
from modules.users.schemas import UserPublic

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.login(form_data.username, form_data.password)


@router.get("/me", response_model=UserPublic)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.get_current_user(token)
