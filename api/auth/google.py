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
import requests

def generate_uid(length):
    uid = shortuuid.ShortUUID().random(length=length)
    return uid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_FILE = os.path.join(BASE_DIR, '../../secrets.json')
secrets = json.loads(open(SECRET_FILE).read())
KEY = secrets["KEY"]
router = APIRouter(prefix="/google")

@router.get("/")
async def login(request: Request):
    google_url = "https://accounts.google.com/o/oauth2/auth?"
    google_params = {
        "client_id": KEY["google"]["id"],
        "response_type" : "code",
        "state" : "12345",
        "redirect_uri": "http://localhost:8000/google/auth",
        "scope" : "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid",
    }
    google_login_url = google_url + urlencode(google_params)
    return RedirectResponse(google_login_url)

@router.get("/auth")
async def callback_google(request: Request, code: str, state: str, db : Session = Depends(get_db)):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": KEY["google"]["id"],
        "client_secret": KEY["google"]["pw"],
        "redirect_uri": "http://localhost:8000/google/auth",
        "grant_type": "authorization_code",
        "code": code,
        "state" : state
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            access_token = response_json["access_token"]

            headers = {
                "Authorization": f"Bearer {access_token}",
            }
            async with httpx.AsyncClient() as client:
                response = await client.get("https://www.googleapis.com/userinfo/v2/me", headers=headers)

            if response.status_code == 200:
                response_json = response.json()
                try:
                    duplicate_check = db.query(User).filter((User.email == response_json["email"]) & (User.social == "google")).first()
                    if not duplicate_check : 
                        db_user = User(uid=generate_uid(10), email=response_json["email"], social="google", name=response_json["name"], info="",notes="", schedules="")
                        db.add(db_user)
                        db.commit()
                        db.refresh(db_user)
                except:
                    RedirectResponse("http://localhost:8000/google")
                user_res = db.query(User).filter((User.email == response_json["email"]) & (User.social == "google")).first()
                return user_res
            else:
                return {"error": "failed to get user info"}
        else:
            return {"error": "failed to get access token"}
        

# 구글 로그아웃 - 클라이언트에서 token 받아서 처리 (실행 확인 : curl -X GET http://localhost:8000/google/logout -H "Authorization: Bearer {your_token_value}")
@router.get("/logout")
async def token_logout_google(request : Request) : 
    token = request.headers["authorization"].split(" ")[1]

    google_token_url = "https://oauth2.googleapis.com/revoke"
    data = {
        "token": token
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(google_token_url, data=data, headers=headers)

    if not response.json() :
        return  RedirectResponse("http://localhost:8000/google")
