from fastapi import APIRouter, Depends
import os
from sqlalchemy.orm import Session
from sqlalchemy import select, text, column, and_
from database import get_db, engine
from models import User, Todo, Weekly
from schemas import user_schema, todo_schema, weekly_schema
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from datetime import datetime


ASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/weekly")

# Weekly Schedule 추가 
@router.post("/{id}")
async def addWeeklySchedule(id:int, weekly:weekly_schema.Weekly, db:Session = Depends(get_db)) :
    UserbyId = db.query(User).filter(User.id == id).first()

    timetable = Weekly(title = weekly.title, start_date = weekly.start_date, end_date = weekly.end_date, 
                       location = weekly.location, notes = weekly.notes, writer_id = id)
    db.add(timetable)
    db.commit()
    db.refresh(timetable)

    # 첫 추가 - 사용자 db 업뎃 
    UserbyId.weekly += str(timetable.id) + "|"
    db.add(UserbyId)
    db.commit()
    db.refresh(UserbyId)

    redirect_url = f"/users/{id}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response


# 수정 
@router.post("/edit/{weeklyId}")
async def editWeeklySchedule(weeklyId:int, schedule:weekly_schema.Weekly, db:Session = Depends(get_db)) :
    WeeklybyId = db.query(Weekly).filter(Weekly.id == weeklyId).first()
    id = WeeklybyId.__getattribute__("writer_id")

    if schedule.title :
        WeeklybyId.title = schedule.title
    if schedule.start_date :
        WeeklybyId.start_date = schedule.start_date
    if schedule.end_date :
        WeeklybyId.end_date = schedule.end_date
    if schedule.location : 
        WeeklybyId.location = schedule.location
    if schedule.notes : 
        WeeklybyId.notes = schedule.notes
    if schedule.writer_id :
        WeeklybyId.writer_id = schedule.writer_id

    db.commit()
    db.refresh(WeeklybyId)
    
    redirect_url = f"/users/{id}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response


# 삭제
@router.delete("/delete/{weeklyId}")
async def deleteWeeklySchedule(weeklyId:int, schedule:weekly_schema.Weekly, db:Session = Depends(get_db)) :
    resultSchedule = []
    WeeklybyId = db.query(Weekly).filter(Weekly.id == weeklyId).first()
    id = WeeklybyId.__getattribute__("writer_id")
    UserbyWeekly = db.query(User).filter(User.id == id).first()

    for weeklyid in ((UserbyWeekly.__getattribute__("weekly").rstrip("|")).split("|")) :
        if int(weeklyid) != int(weeklyId) : 
            resultSchedule.append(weeklyid)
        else :
            pass

    if WeeklybyId : 
        db.delete(WeeklybyId)
        db.commit()
        UserbyWeekly.weekly = ""
        db.commit()
        db.refresh(UserbyWeekly)

    for schedueId in resultSchedule : 
        db.query(User).filter(User.id == id).first().weekly +=  str(schedueId) + "|"
    db.commit()
    db.refresh(UserbyWeekly)

    return "{Delete : Success}"

