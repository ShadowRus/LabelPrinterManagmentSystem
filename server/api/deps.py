from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

SRC_DATA_BASE = config('SRC_DATA_BASE', default='./server/src/printer.db')

SQLALCHEMY_DATABASE_URL = ("sqlite:///"+ str(SRC_DATA_BASE))

# создание движка
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base = declarative_base()



SessionLocal = sessionmaker(autoflush=False, bind=engine)
def get_db() -> Generator:
    db = SessionLocal()
    db.current_user_id = None
    try:
        yield db
    finally:
        db.close()