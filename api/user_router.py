from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import user_schema
# from services import findUserService
from passlib.hash import bcrypt
router = APIRouter(prefix="/api/user")

# 유저 리스트 조회
@router.get("/", response_model=list[user_schema.User])
async def get_user_list(db: Session = Depends(get_db)):
    _user_list = db.query(User).all()
    return _user_list

# 특정 유저 조회
# @router.get('/{id}')
# async def IdCheck(id) :
#     _user = findUserService.UserDBCheck(id)
#     return _user

# 회원가입
# @router.post("/{id}", response_model=list[user_schema.User])
# async def set_user(user: User, db: Session=Depends(get_db)) :
#     hash_password = bcrypt.hash(user.password)
#     db_user = User(
#         id=user.id,
#         email=user.email,
#         password=hash_password,
#         name=user.name
#         # goals=user.goals,
#         # groups=user.groups,
#         # profile_image=user.profile_image,
#         # notes=user.notes,
#         # chats=user.chats
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
