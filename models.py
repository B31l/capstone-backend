from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from database import engine
Base = declarative_base()

# 노트모델
class Note(Base) :
    __tablename__ = "note"

    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String(45), nullable=False)
    body = Column(Text, nullable=False)
    tags = Column(String(100), nullable=True)
    writer_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, nullable=False)
    last_updated_date = Column(DateTime, nullable=False)


class User(Base) :
    __tablename__ = "user"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    uid = Column(String(12), nullable=False)
    email = Column(String(100), nullable=False)
    social = Column(String(10), nullable=True)
    name = Column(String(100),nullable=True)
    info = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    schedules = Column(Text, nullable=True)
    test = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)