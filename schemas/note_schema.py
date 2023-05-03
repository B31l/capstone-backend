import datetime
from pydantic import BaseModel


class Note(BaseModel) :
    id : int
    title: str
    body: str
    writer: str
    last_updated_date: datetime.datetime
    class Config:
        orm_mode = True