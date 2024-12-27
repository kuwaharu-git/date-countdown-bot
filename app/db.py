from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine


DATA_BASE_URL = "sqlite:///database.db"
engine = create_engine(DATA_BASE_URL, echo=True)


class Base(DeclarativeBase):
    pass
