import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

DB_URL = os.environ.get('DB_URL')
engine = create_engine(DB_URL, echo=True)

class Base(DeclarativeBase):
    __session =None
    def __init__(self)-> None:
        if not self.__session:
            self.__initialize_session()

    @classmethod
    def __initialize_session__(cls)-> None:
        if cls.__session:
            raise RuntimeError("there is another session that is already running")
        cls.__session = Session(engine)

    @classmethod
    def __get_unique_cols__(cls) -> list[str]:
        return [column.name for column in cls.__table__.columns if column.unique]

    @classmethod
    def __get_not_null_cols(cls):
        return [column.name for column in cls.__table__.columns if not column.nullable]
