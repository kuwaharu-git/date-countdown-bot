import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db import engine
from app.models import Event


# データベース操作をする際のデコレーター
def db_session(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            print(f"Error: {e}")
            return "error"

    return wrapper


# イベントの追加
@db_session
def create_event(event_name: str, event_date: datetime.datetime) -> None:
    new_event = Event(event_name=event_name, event_date=event_date)
    session = Session(bind=engine)
    session.add(new_event)
    session.commit()
    session.close()


# まだ終了していないイベントを取得
@db_session
def get_unfinished_events() -> list:
    session = Session(bind=engine)
    events = session.query(Event).filter(Event.is_finished == 0).all()
    session.close()
    return events


# 終了済みのイベントを取得
@db_session
def get_finished_events() -> list:
    session = Session(bind=engine)
    events = session.query(Event).filter(Event.is_finished == 1).all()
    session.close()
    return events


# すべてのイベントを取得
@db_session
def get_all_events() -> list:
    session = Session(bind=engine)
    events = session.query(Event).all()
    session.close()
    return events


# イベントの終了更新処理
@db_session
def update_event_finished(event_id: int) -> None:
    session = Session(bind=engine)
    event = session.query(Event).filter(Event.id == event_id).first()
    if event:
        event.is_finished = 1
        session.commit()
    session.close()


# イベントの削除
@db_session
def delete_event(event_id: int) -> bool:
    session = Session(bind=engine)
    event = session.query(Event).filter(Event.id == event_id).first()
    if event:
        session.delete(event)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False


# 指定したIDのイベントがあるかどうかを確認
@db_session
def is_exist_event(event_id: int) -> bool:
    session = Session(bind=engine)
    event = session.query(Event).filter(Event.id == event_id).first()
    session.close()
    return True if event else False
