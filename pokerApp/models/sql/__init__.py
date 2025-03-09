import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from __future__ import annotations

DB_URL = os.environ.get('DB_URL')
engine = create_engine(DB_URL, echo=True)

class Base(DeclarativeBase):
    _session: Session | None =None

    @classmethod
    def get_db_connection(cls) ->Base:
        if not cls._session:
            cls.__initialize_session__()
        return cls

    @classmethod
    def __initialize_session__(cls)-> None:
        if cls._session:
            raise RuntimeError("there is another session that is already running")
        cls._session = Session(engine)

    @classmethod
    def __get_unique_cols__(cls) -> list[str]:
        return [column.name for column in cls.__table__.columns if column.unique]

    @classmethod
    def __get_not_null_cols(cls):
        return [column.name for column in cls.__table__.columns if not column.nullable]
