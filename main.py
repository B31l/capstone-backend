from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from passlib.hash import bcrypt
import pymysql as pymysql
from fastapi import FastAPI, Depends
from Database.databases import *
from sqlalchemy.orm import Session
from Database import UserModel
from Service import findUserService

# 본인 mysql의 user이름, password, db이름 작성
conn = pymysql.connect(host='127.0.0.1', user='--', password='--', db='--', charset='utf8')
cursor = conn.cursor(pymysql.cursors.DictCursor)
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db() :
    db = SessionLocal()
    try :
        yield db
    finally :
        db.close()


# 회원가입
@app.post("/sign/user")
async def signUser(user : UserModel.UserCreate, db : Session = Depends(get_db)) :
    hash_password = bcrypt.hash(user.password)
    db_user = UserModel.User(id=user.id, password=hash_password, nickname=user.nickname, goals=user.goals, groups=user.groups, profile_image=user.profile_image, notes=user.notes, chats=user.chats)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 사용자 정보 확인
@app.get('/users/{id}')
async def IdCheck(id) :
    result = findUserService.UserDBCheck(id)
    return result


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/hello')
def Hello():
    return {"message": '서버 메시지'}