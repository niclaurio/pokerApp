from models import Base
from sqlalchemy import Integer, CheckConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column
from __future__ import annotations

class Level(Base):
    __tablename__ = 'level'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    start_from: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    end_to: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    fee: Mapped[float] = mapped_column(Float, unique=True, nullable=False)
    players_num: Mapped[int] = mapped_column(Integer, nullable=False)
    award_people: Mapped[int] = mapped_column(Integer, nullable=False)
    earned_points: Mapped[int] = mapped_column(Integer, nullable=False)
    player_per_table: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('start_from < end_to and start_from >= 0', name='start_lt_end'),
        {'extend_existing': True},
        CheckConstraint("fee > 0 and players_num>0 and award_people > 0", name='positive_cols'),
        CheckConstraint("award_people < players_num", name='awarded_lt_players')
    )
    @classmethod
    def get_level_max_players_and_fee(cls, level_id: int) -> tuple[int, float]:
        max_players, fee = cls._session.query(Level.players_num, Level.fee).filter(Level.id == level_id).one()
        if not max_players:
            raise RowNotFound("level not found")
        return max_players, fee
