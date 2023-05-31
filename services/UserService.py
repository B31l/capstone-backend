from fastapi import APIRouter, Depends
import os
from sqlalchemy.orm import Session
from sqlalchemy import select, text, column, and_
from database import get_db, engine
from models import User, Note, Todo
from schemas import user_schema, todo_schema
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
import datetime
from typing import List

ASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/users")


def combine_json(json_list: List[dict], key: str):
    combined_data = {}

    for json_data in json_list:
        if key in json_data:
            data = json_data[key]
            if data in combined_data:
                del json_data["date"]
                combined_data[data].append(json_data)
            else:
                del json_data["date"]
                combined_data[data] = [json_data]

    return combined_data


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
    todo_list = []
    user =  db.query(User).filter(User.id == id).first()

    if (user.__getattribute__("notes") != "") : 
        for noteId in ((user.__getattribute__("notes").rstrip("|")).split("|")) :
            note = db.query(Note).filter(Note.id == noteId).first()
            del note.__dict__["_sa_instance_state"]
            note_list.append(jsonable_encoder(note.__dict__))
        user.notes = jsonable_encoder(note_list)
    if (user.__getattribute__("schedules") != ""):
        for todoid in ((user.__getattribute__("schedules").rstrip("|")).split("|")) :
            todos = db.query(Todo).filter(Todo.id == todoid).first()
            todo_list.append(jsonable_encoder(todos.__dict__))
        todo_res = combine_json(todo_list, "date")
        user.schedules = todo_res

    users_data = {"name" : user.name, "uid" : user.uid,  "email" : user.email, "social" : user.social, "id" : user.id, 
                    "info" : user.info, "schedules" : user.schedules, "notes": user.notes}
    res = jsonable_encoder(users_data)

    return res

# @router.delete("/{uid}")
# async def kakao


# uid와 id에 따른 사용자 조회
@router.get("/useruid/{uid}")
async def specUsers(uid:str, db : Session = Depends(get_db)) :
    UserbyUid =  db.query(User).filter(User.uid == uid).first()
    return UserbyUid

@router.get("/userid/{uid}")
async def specUsers(id:int, db : Session = Depends(get_db)) : 
    Userbyid =  db.query(User).filter(User.id == id).first()
    return Userbyid

@router.get("/ube/{email}")
async def ube(email: str, social: str, db: Session = Depends(get_db)):
    User_by_email = db.query(User).filter(and_(User.email == email, User.social == social)).first()
    return User_by_email

# todolist 추가 
@router.post("/todo/{id}")
async def addTodo(id:int, date:str, user:user_schema.User, db:Session = Depends(get_db)) :
    UserbyId = db.query(User).filter(User.id == id).first()
    # 첫 추가 - todo db 업뎃
    # today = str(datetime.now().strftime('%Y-%m-%d'))
    todos = Todo(date = date, task=user.schedules, writer_id = id)
    db.add(todos)
    db.commit()
    db.refresh(todos)

    # 첫 추가 - 사용자 db 업뎃 
    UserbyId.schedules +=  str(todos.id) + "|"
    db.add(UserbyId)
    db.commit()
    db.refresh(UserbyId)

    redirect_url = f"/users/{id}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response


# 수정 및 삭제 (추가 구현 필요)
@router.post("/todo/edit/{TodoId}")
async def editTodo(TodoId:int, todo:todo_schema.Todo, db:Session = Depends(get_db)) :
    TodobyID = db.query(Todo).filter(Todo.id == TodoId).first()
    id = TodobyID.__getattribute__("writer_id")
    # 수정
    if todo.task :
        TodobyID.task = todo.task
    db.commit()
    db.refresh(TodobyID)
    
    redirect_url = f"/users/{id}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response

# completed 
@router.post("/todo/check/{todoId}")
async def changeComplete(todoId : int, todo:todo_schema.Todo, db:Session = Depends(get_db)) : 
    TodobyID = db.query(Todo).filter(Todo.id == todoId).first()
    id = TodobyID.__getattribute__("writer_id")

    if todo.completed : 
        TodobyID.completed = not TodobyID.completed
    db.commit()
    db.refresh(TodobyID)

    redirect_url = f"/users/{id}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response
