from sqlalchemy import String, Integer, DateTime, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models import Base
from mm_match_user import MmMatchUser

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    age: Mapped[int | None] = mapped_column(Integer)
    is_online: Mapped[int] = mapped_column(Boolean, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    amount: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=0)
    state: Mapped[str] = mapped_column(String, nullable=False)
    matches: Mapped[list['MmMatchUser']] = relationship('MmMatchUser', back_populates='user')

    __table_args__ = (
        CheckConstraint('age > 17', name='check_user_on_age'),
        CheckConstraint('amount >=0 and points >=0', name='points_amount_positive_value')
    )