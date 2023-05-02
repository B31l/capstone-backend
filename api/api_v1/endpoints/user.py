from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel
from database import EngineConn
from models import User

router = APIRouter(prefix="/api/user")

engine = EngineConn()
session = engine.sessionmaker()

class Item(BaseModel):
    name: str

@router.get("/")
async def get_users():
    user = session.query(User).all()
    return user