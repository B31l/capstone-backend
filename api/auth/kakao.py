from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from database import get_db
from models import User
import httpx
import os
import json
import shortuuid

def generate_uid(length=10):
    uid = '@' + shortuuid.ShortUUID().random(length=length)
    return uid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_FILE = os.path.join(BASE_DIR, '../../secrets.json')
secrets = json.loads(open(SECRET_FILE).read())
KEY = secrets["KEY"]
router = APIRouter(prefix="/kakao")

@router.get("/")
async def login_kakao(request: Request):
    kakao_url = "https://kauth.kakao.com/oauth/authorize?"
    kakao_params = {
        "response_type" : "code",
        "client_id" : KEY["kakao"]["id"],
        "redirect_uri" : "http://localhost:8000/kakao/auth"
    }
    kakao_login_url = kakao_url + urlencode(kakao_params)
    return RedirectResponse(kakao_login_url)

@router.get("/auth")
async def callback_kakao(request: Request, code: str, db: Session=Depends(get_db)):
    kakao_token_url = "https://kauth.kakao.com/oauth/token"
    kakao_data = {
        "grant_type": "authorization_code",
        "client_id": KEY["kakao"]["id"],
        "code": code,
        "redirect_uri": "http://localhost:8000/kakao/auth"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    with httpx.Client() as client:
        response = client.post(kakao_token_url, data=kakao_data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json["access_token"]
    
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        with httpx.Client() as client:
            response = client.get("https://kapi.kakao.com/v2/user/me", headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            try :
                user_check = db.query(User).filter((User.email == response_json["kakao_account"]["email"]) & (User.social == "kakao")).first()
                if not user_check : 
                    db_user = User(
                        uid=generate_uid(10),
                        email=response_json["kakao_account"]["email"],
                        social="kakao",
                        name=response_json["properties"]["nickname"],
                        info="",
                        notes="{}",
                        schedules="",
                        weekly="",
                        chats=""
                    )
                    db.add(db_user)
                    db.commit()
                    db.refresh(db_user)
            except :
                RedirectResponse("http://localhost:8000/kakao")
            user_res = db.query(User).filter((User.email == response_json["kakao_account"]["email"]) & (User.social == "kakao")).first()
            return user_res


# 카카오 로그아웃 - API 사용
@router.get("/logout")
async def logout_kakao() :
    kakao_url = "https://kauth.kakao.com/oauth/logout?"
    kakao_params = {
        "client_id" : KEY["kakao"]["id"],
        "logout_redirect_uri" : "http://localhost:8000/kakao"
    }
    kakao_login_url = kakao_url + urlencode(kakao_params)
    return RedirectResponse(kakao_login_url)