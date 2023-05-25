import datetime
from pydantic import BaseModel


class Note(BaseModel) :
    id : int
    title: str
    body: str
    tags: str
    writer_id: int
    created_date : datetime.datetime
    last_updated_date: datetime.datetime

    class Config:
        orm_mode = True