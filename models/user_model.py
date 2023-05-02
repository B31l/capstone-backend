from sqlalchemy import Column, String
from database import Base

# 사용자 모델
class User(Base) :
    __tablename__ = "user"

    id = Column(String(100), nullable=False, primary_key=True)
    password = Column(String(100),nullable=False)
    name = Column(String(100),nullable=True)
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

