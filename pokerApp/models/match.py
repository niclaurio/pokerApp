from models import Base
from sqlalchemy import Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from mm_match_user import MmMatchUser



class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default= datetime.now())
    ended_at: Mapped[datetime] = mapped_column(DateTime)
    level: Mapped[int] = mapped_column(Integer, ForeignKey('levels.id'))

    users: Mapped[list['MmMatchUser']] = relationship('MmMatchUser', back_populates='match')

    __table_args__ = CheckConstraint(
        'end_date IS NULL OR end_date > start_date',
        name='check_end_date'
    ),