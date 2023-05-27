from fastapi import APIRouter, Depends
import os
from sqlalchemy.orm import Session
from sqlalchemy import select, text, column
from database import get_db, engine
from models import User, Note
from schemas import user_schema
from fastapi.encoders import jsonable_encoder

ASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/users")


# 전체 사용자 db 조회
@router.get("/")
async def checkUsers(db: Session = Depends(get_db)) :
    user =  db.query(User).all()
    return user

# 수정 - 이름 or 상태메시지
@router.post("/edit/{id}")
async def editUser(id: int, editUser: user_schema.User, db: Session = Depends(get_db)) :
    user =  db.query(User).filter(User.id == id).first()
    if editUser.name : 
        user.name = editUser.name
    if editUser.info :
        user.info = editUser.info
    db.commit()
    db.refresh(user)
    return user

# id에 따른 사용자 정보 조회 및 노트 조회
@router.get("/{id}")
async def specUsers(id:str, db : Session = Depends(get_db)) : 
    note_list = []
    user =  db.query(User).filter(User.id == id).first()
    for noteId in ((user.__getattribute__("notes").rstrip("|")).split("|")) :
        note = db.query(Note).filter(Note.id == noteId).first()
        del note.__dict__["_sa_instance_state"]
        note_list.append(jsonable_encoder(note.__dict__))
    users_data = {"name" : user.name, "uid" : user.uid,  "email" : user.email, "social" : user.social, "id" : user.id, "info" : user.info, "schedules" : user.schedules, "notes": jsonable_encoder(note_list)}
    res = jsonable_encoder(users_data)
    return res

# @router.delete("/{uid}")
# async def kakao


# uid와 id에 따른 사용자 조회
@router.get("/useruid/{uid}")
async def specUsers(uid:int, db : Session = Depends(get_db)) : 
    UserbyUid =  db.query(User).filter(User.uid == uid).all()
    return UserbyUid

@router.get("/userid/{uid}")
async def specUsers(id:int, db : Session = Depends(get_db)) : 
    Userbyid =  db.query(User).filter(User.id == id).all()
    return Userbyid
