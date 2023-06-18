from datetime import datetime
from pydantic import BaseModel


class Weekly(BaseModel) :
    id : int
    title: str
    start_date : datetime
    end_date : datetime
    location : str
    notes : str
    writer_id : int

    class Config:
        orm_mode = True
