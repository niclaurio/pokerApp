from models import Base
from sqlalchemy import Integer, ForeignKey, UniqueConstraint, PrimaryKeyConstraint, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from match import Match
from user import User
from level import Level


class MmMatchUser(Base):
    __tablename__ = "mm_matches_users"
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("matches.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    placement: Mapped[int] = mapped_column(Integer, nullable=False)
    match: Mapped['Match'] = relationship("Match", back_populates='users')
    user: Mapped['User'] = relationship("User", back_populates='matches')

    __table_args__ = (
        PrimaryKeyConstraint("match_id", "user_id", name='mm_matches_users_primary_key'),
        UniqueConstraint("match_id", 'placement', name='match_user__position_unique')
    ),

    @validates('placement')
    def validate_placement(self, key, value):
        stmt = select(Level.players_num).join(Match, Match.level == Level.id, isouter=True).filter(Match.id==self.match_id)
        if not 1 <= value <= self.__session.execute(stmt).one():
            raise ValueError("placement must be greater than 1 and lower that players_num")
