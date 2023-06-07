from fastapi import APIRouter, Depends
import os
from sqlalchemy.orm import Session
from sqlalchemy import select, text, column, and_
from database import get_db, engine
from models import User, Todo
from schemas import user_schema, todo_schema
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse


ASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/todo")


# todolist 추가 
@router.post("/{id}")
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


# 수정 
@router.post("/edit/{TodoId}")
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

# 삭제
@router.delete("/delete/{TodoId}")
async def deleteTodo(TodoId:int, todo:todo_schema.Todo, db:Session = Depends(get_db)) :
    resultTodo = []
    TodobyID = db.query(Todo).filter(Todo.id == TodoId).first()
    id = TodobyID.__getattribute__("writer_id")
    UserbyTodo = db.query(User).filter(User.id == id).first()

    for todoid in ((UserbyTodo.__getattribute__("schedules").rstrip("|")).split("|")) :
        if int(todoid) != int(TodoId) : 
            resultTodo.append(todoid)
        else :
            pass
    

    if TodobyID : 
        db.delete(TodobyID)
        db.commit()
        UserbyTodo.schedules = ""
        db.commit()
        db.refresh(UserbyTodo)


    for todosId in resultTodo : 
        db.query(User).filter(User.id == id).first().schedules +=  str(todosId) + "|"
    db.commit()
    db.refresh(UserbyTodo)

    return "{Delete : Success}"

# completed 
@router.post("/check/{todoId}")
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
