from pydantic import BaseModel

class Chat(BaseModel) :
    id : int
    title: str
    generate_id: int
    participate_id : str
    info : str
    messages : str

    class Config:
        orm_mode = True

