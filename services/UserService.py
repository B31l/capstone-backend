from fastapi import APIRouter, Depends
import os
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import user_schema

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

@router.get("/{uid}")
async def specUsers(uid:str, db : Session = Depends(get_db)) : 
    user =  db.query(User).filter(User.uid == uid).first()
    return user

# @router.delete("/{uid}")
# async def kakao

