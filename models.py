from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from database import engine
Base = declarative_base()

# 노트모델
class Note(Base) :
    __tablename__ = "note"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    title = Column(String(45), nullable=False)
    body = Column(Text, nullable=False)
    tags = Column(String(100), nullable=True)
    writer_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, nullable=False)
    last_updated_date = Column(DateTime, nullable=False)


class User(Base) :
    __tablename__ = "user"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    uid = Column(Text, nullable=False)
    email = Column(String(100), nullable=False)
    social = Column(String(10), nullable=True)
    name = Column(String(100),nullable=True)
    info = Column(String(100), nullable=True)
    notes = Column(String(100), nullable=True)
    schedules = Column(Text, nullable=True)
    weekly = Column(Text, nullable=True)
    chats = Column(Text, nullable=True)


# TO-DO-List
class Todo(Base) :
    __tablename__ = "todo"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    date = Column(String(100), nullable=False)
    task = Column(String(100), nullable=False)
    completed = Column(Boolean, default=False)
    writer_id = Column(Integer, nullable=False)



# Weekly Schedule
class Weekly(Base) :
    __tablename__ = "weekly"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    start_date = Column(DateTime, default=False)
    end_date = Column(DateTime, default=False)
    location = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    writer_id = Column(Integer, nullable=False)


# 채팅 DB
class Chat(Base) :
    __tablename__ = "chat"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    generate_id = Column(Integer, nullable=False)
    participate_id = Column(Text, nullable=True)
    info = Column(Text, nullable=True)
    messages = Column(Text, nullable=True)


# 메시지 DB
class Message(Base) :
    __tablename__ = "message"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, nullable=False)
    writer_id = Column(Integer, nullable=False)
    body = Column(Text, nullable=True)  
    time = Column(DateTime, nullable=False) 


Base.metadata.create_all(bind=engine)

