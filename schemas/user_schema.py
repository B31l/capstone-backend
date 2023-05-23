from pydantic import BaseModel


class User(BaseModel) :
    id : int
    email: str
    password : str
    name : str | None = None
    social : str | None = None
    # token : str | None = None
    # goals : str | None = None
    # groups : str | None = None
    profile_image : str | None = None
    # notes : str | None = None
    # chats : str | None = None

    class Config:
        orm_mode = True
        # arbitrary_types_allowed = True