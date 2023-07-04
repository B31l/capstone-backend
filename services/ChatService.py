from fastapi import APIRouter, Depends
import os
from sqlalchemy.orm import Session
from database import get_db
from models import User, Chat, Message
from schemas import user_schema, chat_schema, message_schema
from fastapi.encoders import jsonable_encoder
from datetime import datetime
import json
from fastapi.responses import RedirectResponse

ASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/chats")

# 채팅방 전체 목록 
@router.get("/")
async def getChats(db:Session = Depends(get_db)) : 
    chats = db.query(Chat).all()
    return chats

# 사용자가 참여한 채팅방 목록
@router.get("/mychat/{userId}")
async def getMyChats(userId: int, db:Session = Depends(get_db)) : 
    userById =  db.query(User).filter(User.id == userId).first()
    chat_list = []
    if (userById.__getattribute__("chats") != "") :
        for chatid in ((userById.__getattribute__("chats").rstrip("|")).split("|")) : 
            chats = db.query(Chat).filter(Chat.id == chatid).first()
            chat_list.append(jsonable_encoder(chats.__dict__))
        chatsByuser = jsonable_encoder(chat_list)
    else :
        chatsByuser = None
    return chatsByuser

# 채팅방 생성
@router.post("/create")
async def createGroups(generate_id:int, chat:chat_schema.Chat, db:Session = Depends(get_db)) : 
    UserbyId = db.query(User).filter(User.id == generate_id).first()
    new_chat = Chat(title=chat.title, generate_id=generate_id, participate_id=f"{generate_id}|", info=chat.info, messages="")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    UserbyId.chats += str(new_chat.id) + "|"
    db.add(UserbyId)
    db.commit()
    db.refresh(UserbyId)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    redirect_url = f"/chats"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response

# 채팅방 참가 -> 사용자 chat 업뎃, 채팅 db 참가자 업뎃
@router.post("/join/{chat_id}")
async def joinGroup(chat_id: int, user_id : int, db:Session = Depends(get_db)) :
    UserbyId = db.query(User).filter(User.id == user_id).first()
    chatIDs = []
    for chatid in ((UserbyId.__getattribute__("chats").rstrip("|")).split("|")) :
        chatIDs.append(chatid)
    if str(chat_id) in chatIDs :
        pass
    else : 
        UserbyId.chats += str(chat_id) +"|"
        db.add(UserbyId)
        db.commit()
        db.refresh(UserbyId)


    ChatbyId = db.query(Chat).filter(Chat.id == chat_id).first()
    userIDs = []
    for userid in ((ChatbyId.__getattribute__("participate_id").rstrip("|")).split("|")) :
        userIDs.append(userid)

    if str(user_id) in userIDs :
        pass
    else : 
        ChatbyId.participate_id += str(user_id) +"|"
        db.add(ChatbyId)
        db.commit()
        db.refresh(ChatbyId)

    redirect_url = f"/chats/{chat_id}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    return response

# 특정 그룹(채팅) 조회
@router.get("/{chat_id}")
async def showChatsbyId(chat_id:int, db:Session=Depends(get_db)) :
    chatbyID =  db.query(Chat).filter(Chat.id == chat_id).all()
    return chatbyID


# 채팅방 업데이트 ( 수정, 삭제 ) 
@router.post("/{chat_id}/upadate")
async def editGroup(chat:chat_schema.Chat, chatId:int, db:Session=Depends(get_db)) :
    ChatbyChatId = db.query(Chat).filter(Chat.id == chatId).first()

    if chat.title :
        ChatbyChatId.title = chat.title
    if chat.info : 
        ChatbyChatId.info = chat.info
    db.commit()
    db.refresh(ChatbyChatId)
    return ChatbyChatId

# 그룹 만든 사람만 삭제 가능 -> 연관 
@router.delete("/{chat_id}/delete")
async def deleteGroup(chat:chat_schema.Chat, chatId:int, userId:int, db:Session=Depends(get_db)) :
    
    ParticipantsId = []
    ChatbyChatId = db.query(Chat).filter(Chat.id == chatId).first()
    generate_id = ChatbyChatId.__getattribute__("generate_id")
    for participantId in ((ChatbyChatId.__getattribute__("participate_id").rstrip("|")).split("|")) :
        ParticipantsId.append(participantId)


    if str(generate_id) == str(userId) : 
        for usersId in ParticipantsId : 
            ParticipantByChat = db.query(User).filter(User.id == usersId).first()
            resultChat = []
            for chatsId in ((ParticipantByChat.__getattribute__("chats").rstrip("|")).split("|")) :
                if int(chatsId) != int(chatId) : 
                    resultChat.append(chatsId)
                else :
                    pass
            ParticipantByChat.chats = ""
            db.commit()
            db.refresh(ParticipantByChat)
            for chatsID in resultChat : 
                db.query(User).filter(User.id == usersId).first().chats +=  str(chatsID) + "|"
            db.commit()
            db.refresh(ParticipantByChat)
            if ChatbyChatId : 
                db.delete(ChatbyChatId)
                db.commit()

        res = "{Delete : Success}"
    else : 
        res = "{Delete : Fail}"
    
    return res

# 메시지 보내기 -> 메시지 DB 업데이트 및 조회
# @router.post("/{chat_id}/message")

# 참가자의 그룹 탈퇴
