from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from database import get_db
from models import User
import httpx
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_FILE = os.path.join(BASE_DIR, 'secrets.json')
secrets = json.loads(open(SECRET_FILE).read())
KEY = secrets["KEY"]
router = APIRouter(prefix="/kakao")

@router.get("/")
async def login_kakao(request : Request) :
    kakao_url = "https://kauth.kakao.com/oauth/authorize?"
    kakao_params = {
        "response_type" : "code",
        "client_id" : KEY.kakao.id,
        "redirect_uri" : "http://localhost:8000/kakao/auth"
    }
    kakao_login_url = kakao_url + urlencode(kakao_params)
    return RedirectResponse(kakao_login_url)

@router.get("/auth")
async def callback_kakao(request: Request, code: str, db : Session = Depends(get_db)) :
    kakao_token_url = "https://kauth.kakao.com/oauth/token"
    kakao_data = {
        "grant_type": "authorization_code",
        "client_id": "--",
        "code": code,
        "redirect_uri": "http://localhost:8000/kakao/auth"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(kakao_token_url, data=kakao_data, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json["access_token"]

        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get("https://kapi.kakao.com/v2/user/me", headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            try :
                db_user = User(id=response_json["id"], password="", nickname=response_json["properties"]["nickname"], goals="", groups="", profile_image="", notes="", chats="")
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
            except :
                RedirectResponse("http://localhost:8000/kakao")
            return response_json
        else:
            return {"error": "failed to get user info"}
    else:
        return {"error": "failed to get access token"}