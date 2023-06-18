from pydantic import BaseModel


class User(BaseModel) :
    id : int
    uid : str
    email: str
    social : str | None = None
    name : str | None = None
    info : str | None = None
    notes : str | None = None
    schedules : str | None = None
    weekly : str | None = None 
    # token : str | None = None
    # goals : str | None = None
    # groups : str | None = None
    # notes : str | None = None
    # chats : str | None = None

    class Config:
        orm_mode = True
        # arbitrary_types_allowed = True