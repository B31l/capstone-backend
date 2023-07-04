import datetime
from pydantic import BaseModel


class Message(BaseModel) :
    id : int
    chat_id : int 
    writer_id: int
    body : str
    time : datetime.datetime

    class Config:
        orm_mode = True