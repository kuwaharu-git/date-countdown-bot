from app.db import Base, engine
from app.models import Event


# テーブルを作成
def create_table():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_table()
