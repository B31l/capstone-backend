from datetime import datetime
from pydantic import BaseModel


class Todo(BaseModel) :
    id : int
    date: str
    task: str
    completed: bool
    writer_id: int

    class Config:
        orm_mode = True