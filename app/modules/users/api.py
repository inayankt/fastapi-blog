from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.users.dependencies import get_user_service
from modules.users.schemas import UserCreate, UserResponse, UserUpdate
from modules.users.service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.create_user(payload)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.delete_user(user_id)
