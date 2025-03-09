from __future__ import annotations
from sqlalchemy import String, Integer, DateTime, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    age: Mapped[int | None] = mapped_column(Integer)
    is_online: Mapped[int] = mapped_column(Boolean, default=1)
    is_playing: Mapped[int] = mapped_column(Boolean, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    amount: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=0)
    state: Mapped[str] = mapped_column(String, nullable=False)
    iban: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        CheckConstraint('age > 17', name='check_user_on_age'),
        CheckConstraint('amount >=0 and points >=0', name='points_amount_positive_value')
    )

    def add_user(self)-> None:
        try:
            User._session.add(self)
            User._session.commit()
        except Exception as e:
            User._session.rollback()
            raise e

    @classmethod
    def get_ids_from_usernames(cls, users: list[str]) -> list[int]:
        users_id = User._session.query(User.id).filter(User.username.in_(users)).all()
        if not users_id:
            raise RowNotFound('invalid users list')
        if len(users) != len(users_id):
            raise RowNotFound("not all users exist")
        return users_id


    @classmethod
    def get_user_by_username(cls, username: str) -> User:
        user = cls._session.query(User).filter(User.username == username).one()
        if not user:
            raise RowNotFound("user not found")
        return user