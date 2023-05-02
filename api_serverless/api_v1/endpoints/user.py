from fastapi import APIRouter, Depends, Path, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import EngineConn

from models.user_model import User

router = APIRouter(prefix="/api/user")
engine = EngineConn()
session = engine.sessionmaker()

class Item(BaseModel):
    name: str

@router.get("/")
async def user_list():
    db = session
    _user_list = db.query(User).all()
    db.close()
    return _user_lists