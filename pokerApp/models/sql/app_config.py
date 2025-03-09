from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String
from models import Base


class AppConfig(Base):
    __tablename__ = 'app_configs'
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)

    @classmethod
    def get_config(cls, key: str) ->str:
        return cls._session.query(cls.value).filter(cls.key == key).one()
