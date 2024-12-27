from sqlalchemy import Column, Integer, String, Date
from app.db import Base


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    event_name = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    is_finished = Column(Integer, default=0)
