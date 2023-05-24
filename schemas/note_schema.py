import datetime
from pydantic import BaseModel


class Note(BaseModel) :
    id : int
    title: str
    body: str
    tags: str
    writer_id: int
    created_dtae
    last_updated_date: datetime.datetime

    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String(45), nullable=False)
    body = Column(Text, nullable=False)
    tags = Column(String(100), nullable=True)
    writer_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, nullable=False)
    last_updated_date = Column(DateTime, nullable=False)
    class Config:
        orm_mode = True