from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
import os
from sqlalchemy.orm import Session
from database import get_db
from models import User, Group, Message
from schemas import group_schema, user_schema, message_schema
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime
import json
from fastapi.responses import RedirectResponse
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from main import manager

ASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/groups")

# 채팅방 전체 목록 
@router.get("/")
async def getGroups(db:Session = Depends(get_db)) : 
    groups = db.query(Group).all()
    return groups

# 사용자가 참여한 채팅방 목록
@router.get("/mygroup/{userId}")
async def getMyGroups(userId: int, db:Session = Depends(get_db)) : 
    userById =  db.query(User).filter(User.id == userId).first()
    gorup_list = []
    if (userById.__getattribute__("groups") != "") :
        for groupid in ((userById.__getattribute__("groups").rstrip("|")).split("|")) : 
            group = db.query(Group).filter(Group.id == groupid).first()
            gorup_list.append(jsonable_encoder(group.__dict__))
        groupByUser = jsonable_encoder(gorup_list)
    else :
        groupByUser = None
    return groupByUser

# 채팅방 생성
@router.post("/create")
async def createGroups(generate_id:int, group:group_schema.Group, db:Session = Depends(get_db)) : 
    UserbyId = db.query(User).filter(User.id == generate_id).first()
    new_group = Group(title=group.title, generate_id=generate_id, participate_id=f"{generate_id}|", info=group.info, messages="")
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    UserbyId.groups += str(new_group.id) + "|"
    db.add(UserbyId)
    db.commit()
    db.refresh(UserbyId)

    redirect_url = f"/groups"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response

# 채팅방 참가 -> 사용자 chat 업뎃, 채팅 db 참가자 업뎃
@router.post("/join/{groupId}")
async def joinGroup(groupId: int, user_id : int, db:Session = Depends(get_db)) :
    UserbyId = db.query(User).filter(User.id == user_id).first()
    groupIDs = []
    for groupid in ((UserbyId.__getattribute__("groups").rstrip("|")).split("|")) :
        groupIDs.append(groupid)
    if str(groupId) in groupIDs :
        pass
    else : 
        UserbyId.groups += str(groupId) +"|"
        db.add(UserbyId)
        db.commit()
        db.refresh(UserbyId)


    GroupById = db.query(Group).filter(Group.id == groupId).first()
    userIDs = []
    for userid in ((GroupById.__getattribute__("participate_id").rstrip("|")).split("|")) :
        userIDs.append(userid)

    if str(user_id) in userIDs :
        pass
    else : 
        GroupById.participate_id += str(user_id) +"|"
        db.add(GroupById)
        db.commit()
        db.refresh(GroupById)

    redirect_url = f"/groups/{groupId}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response
    
# 특정 그룹(채팅) 조회
@router.get("/{group_id}")
async def showGroupsbyId(group_id:int, db:Session=Depends(get_db)) :
    groupbyID =  db.query(Group).filter(Group.id == group_id).first()
    return groupbyID 


# 채팅방 업데이트 ( 수정, 삭제 ) 
@router.post("/{groupId}/upadate")
async def editGroup(group:group_schema.Group, groupId:int, db:Session=Depends(get_db)) :
    GroupbyGroupId = db.query(Group).filter(Group.id == groupId).first()

    if group.title :
        GroupbyGroupId.title = group.title
    if group.info : 
        GroupbyGroupId.info = group.info
    db.commit()
    db.refresh(GroupbyGroupId)
    return GroupbyGroupId

# 그룹 만든 사람만 삭제 가능 -> 연관 
@router.delete("/{groupId}/delete")
async def deleteGroup(groupId:int, userId:int, db:Session=Depends(get_db)) :
    
    ParticipantsId = []
    GroupByGroupId = db.query(Group).filter(Group.id == groupId).first()
    generate_id = GroupByGroupId.__getattribute__("generate_id")
    for participantId in ((GroupByGroupId.__getattribute__("participate_id").rstrip("|")).split("|")) :
        ParticipantsId.append(participantId)


    if int(generate_id) == int(userId) : 
        for usersId in ParticipantsId : 
            ParticipantByGroup = db.query(User).filter(User.id == usersId).first()
            resultGroup = []
            for groupsID in ((ParticipantByGroup.__getattribute__("groups").rstrip("|")).split("|")) :
                if int(groupsID) != int(groupId) : 
                    resultGroup.append(groupsID)
                else :
                    pass
            ParticipantByGroup.groups = ""
            db.commit()
            db.refresh(ParticipantByGroup)
            for groupsIDs in resultGroup : 
                db.query(User).filter(User.id == usersId).first().groups += f"{groupsIDs}|"
            db.commit()
            db.refresh(ParticipantByGroup)
        if GroupByGroupId : 
            db.delete(GroupByGroupId)
            db.commit()

        res = "{Delete : Success}"
    else : 
        res = "{Delete : Fail}"
    
    return res

# 참가자의 그룹 탈퇴 => 그룹 멤버 수정, 해당 참가자가의 그룹 수정 
@router.post("/{groupId}/unregister")
async def unregisterGroup(groupId:int, user_id:int, db:Session=Depends(get_db)) : 
    UserbyID = db.query(User).filter(User.id == user_id).first()
    GroupbyID = db.query(Group).filter(Group.id == groupId).first()

    # 참가자 그룹 수정
    resultGroup = []
    for groupsId in ((UserbyID.__getattribute__("groups").rstrip("|")).split("|")) :
        if int(groupsId) != int(groupId) : 
            resultGroup.append(groupsId)
        else :
            pass
    UserbyID.groups = ""
    db.commit()
    db.refresh(UserbyID)
    for groupID in resultGroup : 
        db.query(User).filter(User.id == user_id).first().groups +=  str(groupID) + "|"
    db.commit()
    db.refresh(UserbyID)

    # 해당 그룹 멤버 수정
    resultMember = []
    for memId in ((GroupbyID.__getattribute__("participate_id").rstrip("|")).split("|")) :
        if int(memId) != int(user_id) : 
            resultMember.append(memId)
        else :
            pass
    GroupbyID.participate_id = ""
    db.commit()
    db.refresh(GroupbyID)
    for memsId in resultMember : 
        db.query(Group).filter(Group.id == groupId).first().participate_id +=  str(memsId) + "|"
    db.commit()
    db.refresh(GroupbyID)

    redirect_url = f"/groups/mygroup/{user_id}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response

# 채팅방 초대


# 채팅 그룹 - websocket / webrtc
