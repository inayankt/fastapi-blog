from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from modules.auth.dependencies import get_auth_service, get_current_user
from modules.auth.schemas import Token
from modules.auth.service import AuthService
from modules.users.models import User
from modules.users.schemas import UserPrivate

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.login(form_data.username, form_data.password)


@router.get("/me", response_model=UserPrivate)
async def get_me(user: Annotated[User, Depends(get_current_user)]):
    return user
