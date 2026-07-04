from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from modules.auth.dependencies import get_auth_service, get_current_user
from modules.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    Token,
)
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
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def handle_forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.handle_forgot_password(request_data.email, background_tasks)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def handle_reset_password(
    request_data: ResetPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.handle_reset_password(
        request_data.new_password, request_data.token
    )


@router.post("/me/password", status_code=status.HTTP_200_OK)
async def handle_change_password(
    request_data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.handle_change_password(
        current_user, request_data.current_password, request_data.new_password
    )
