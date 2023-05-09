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
                    db_user = User(id=response_json["id"], password="",
                                             nickname=response_json["name"], goals="", groups="",
                                             profile_image="", notes="", chats="")
                    db.add(db_user)
                    db.commit()
                    db.refresh(db_user)
                except:
                    RedirectResponse("http://localhost:8000/google")
                return response_json
            else:
                return {"error": "failed to get user info"}
        else:
            return {"error": "failed to get access token"}