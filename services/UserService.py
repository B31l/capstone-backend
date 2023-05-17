from fastapi import APIRouter, Depends
import os
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import user_schema

ASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/users")

# 특정 사용자 db 조회
@router.get("/{id}")
async def specUsers(id:int, db : Session = Depends(get_db)) : 
    user =  db.query(User).filter(User.id == id).first()
    return user

# 전체 사용자 db 조회
@router.get("/")
async def checkUsers(db : Session = Depends(get_db)) : 
    user =  db.query(User).all()
    return user

# 수정 - 이름 or 프로필이미지 
@router.post("/edit/{id}")
async def editUser(id : int, editUser : user_schema.User, db : Session = Depends(get_db)) :
    user =  db.query(User).filter(User.id == id).first()
    if editUser.name : 
        user.name = editUser.name
    if editUser.profile_image :
        user.profile_image = editUser.profile_image
    db.commit()
    db.refresh(user)
    return user


