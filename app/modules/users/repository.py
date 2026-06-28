from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.users.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        result = self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    def get_by_username(self, username: str) -> User | None:
        result = self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    def get_by_email(self, email: str) -> User | None:
        result = self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    def create(self, username: str, email: str, image_file: str | None = None) -> User:
        new_user = User(username=username, email=email, image_file=image_file)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
