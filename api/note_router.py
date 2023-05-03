from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Note
from schemas import note_schema

router = APIRouter(prefix="/api/note")

# 유저 리스트 조회
@router.get("/", response_model=list[note_schema.Note])
async def get_note_list(db: Session = Depends(get_db)):
    _user_list = db.query(Note).all()
    return _user_list
