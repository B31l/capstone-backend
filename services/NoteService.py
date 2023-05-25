from fastapi import APIRouter, Depends
import os
from sqlalchemy.orm import Session
from database import get_db
from models import Note, User
from schemas import note_schema, user_schema
from datetime import datetime

ASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/notes")

# 특정 사용자 노트 db 조회
@router.get("/{id}")
async def specUsers(id:int, db : Session = Depends(get_db)) : 
    NotebyID =  db.query(Note).filter(Note.writer_id == id).all()
    return NotebyID



# 노트 생성
@router.post("/")
async def uploadNote(note:note_schema.Note, user:user_schema.User, writer_id:int, db : Session = Depends(get_db)) :
    noteUser = Note(title=note.title, body=note.body, tags="", writer_id=writer_id, created_date=datetime.now(), last_updated_date=datetime.now())
    UserbyNote = db.query(User).filter(User.id == writer_id).first()
    if user.notes : 
        UserbyNote.notes += str(note.id) + "|"
        db.add(UserbyNote)
        db.commit()
        db.refresh(UserbyNote)
    db.add(noteUser)
    db.commit()
    db.refresh(noteUser)
    return noteUser


# 노트 수정 - title 및 body, 최근 업데이트 시간
@router.post("/{noteId}")
async def editNote(note:note_schema.Note, noteId:int, db:Session=Depends(get_db)) :
    NotebyNoteID = db.query(Note).filter(Note.id == noteId).first()
    if note.body : 
        NotebyNoteID.body = note.body
        NotebyNoteID.last_updated_date = datetime.now()
    if note.title : 
        NotebyNoteID.title = note.title
        NotebyNoteID.last_updated_date = datetime.now()
    db.commit()
    db.refresh(NotebyNoteID)
    return NotebyNoteID

