from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import engine
Base = declarative_base()


# 사용자 모델
class Note(Base) :
    __tablename__ = "note"

    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String(45), nullable=False)
    body = Column(Text, nullable=False)
    writer_id = Column(Integer, nullable=False)
    # writer_id = Column(Integer, ForeignKey("writer.id"))
    # writer = relationship("User", backref="notes")
    last_updated_date = Column(DateTime, nullable=False)


# 사용자 모델
class User(Base) :
    __tablename__ = "user"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False)
    password = Column(String(100),nullable=False)
    name = Column(String(100),nullable=True)
    social = Column(String(100), nullable=True)
    # goals = Column(String(100),nullable=True)
    # groups = Column(String(100),nullable=True)
    # profile_image = Column(String(100),nullable=True)
    # notes = Column(String(100),nullable=True)
    # chats = Column(String(100),nullable=True)



    # def __init__(self, id, password, name,
    #              # goals, groups, profile_image, notes, chats
    #              ):
    #     self.id = id
    #     self.password = password
    #     self.name = name
        # self.goals = goals
        # self.groups = groups
        # self.profile_image = profile_image
        # self.notes = notes
        # self.chats = chats

Base.metadata.create_all(bind=engine)