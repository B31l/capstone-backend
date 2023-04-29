from pydantic import BaseModel

from Database.databases import Base
from sqlalchemy import Column, String
from typing import Optional

# 사용자 모델
class User(Base) :
    __tablename__ = "user"

    id = Column(String(100), nullable=False, primary_key=True)
    password = Column(String(100),nullable=False)
    nickname = Column(String(100),nullable=True)
    goals = Column(String(100),nullable=True)
    groups = Column(String(100),nullable=True)
    profile_image = Column(String(100),nullable=True)
    notes = Column(String(100),nullable=True)
    chats = Column(String(100),nullable=True)

    def __init__(self, id, password, nickname, goals, groups, profile_image, notes, chats) :
        self.id = id
        self.password = password
        self.nickname = nickname
        self.goals = goals
        self.groups = groups
        self.profile_image = profile_image
        self.notes = notes
        self.chats = chats


class UserCreate(BaseModel) :
    id : str
    password : str
    nickname : Optional[str] = None
    goals : Optional[str] = None
    groups : Optional[str] = None
    profile_image : Optional[str] = None
    notes : Optional[str] = None
    chats : Optional[str] = None

