from models import Base
from sqlalchemy import Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Level(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    start_from: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    end_to: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    fee: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    players_num: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('start_from < end_to and start_from >= 0', name='start_lt_end'),
        {'extend_existing': True},
        CheckConstraint("fee > 0 and players_num>0", name='fee_players_num_positive')
    )

