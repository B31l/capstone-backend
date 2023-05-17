from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from database import get_db
from models import User
import requests
import httpx
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_FILE = os.path.join(BASE_DIR, '../../secrets.json')
secrets = json.loads(open(SECRET_FILE).read())
KEY = secrets["KEY"]
router = APIRouter(prefix="/naver")

@router.get("/")
async def login_naver(request: Request) :
    naver_url = "https://nid.naver.com/oauth2.0/authorize?"
    naver_params = {
        "client_id": KEY["naver"]["id"],
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/naver/auth",
        "state": str
    }
    naver_login_url = naver_url + urlencode(naver_params)
    return RedirectResponse(naver_login_url)

# 토근 저장
def get_token(request: Request, code: str, state: str, db: Session=Depends(get_db)) :
    naver_token_url = "https://nid.naver.com/oauth2.0/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": KEY["naver"]["id"],
        "client_secret": KEY["naver"]["pw"],
        "code": code,
        "state": state,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }

    # 액세스 토큰 취득
    with httpx.Client() as client:
        response = client.post(naver_token_url, data=data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json["access_token"]
    return access_token


@router.get("/auth")
async def callback_naver(request: Request, code: str, state: str, db: Session=Depends(get_db)) :
        access_token = get_token(request, code, state, db)
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        # 유저 정보 조회 및 토큰 갱신
        with httpx.Client() as client:
            response = client.get("https://openapi.naver.com/v1/nid/me", headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            try :
                user_check = db.query(User).filter((User.email == response_json["response"]["email"]) & (User.social == "naver")).first()
                if not user_check : 
                    db_user = User(email=response_json["response"]["email"], password="", name=response_json["response"]["name"], social="naver", token = access_token)
                    db.add(db_user)
                    db.commit()
                    db.refresh(db_user)
                if User.token != access_token : 
                    user_check.token = access_token
                    db.commit()
                    db.refresh(user_check)
            except :
                RedirectResponse("http://localhost:8000/naver")
            user_res = db.query(User).filter((User.email == response_json["response"]["email"]) & (User.social == "naver")).first()
            return user_res


# 네이버 회원탈퇴? 로그아웃? - token 삭제 - db에 있는 naver 소셜 로그인의 id 값
@router.get('/{id}/logout')
async def logout_naver(request : Request, id:int , db: Session=Depends(get_db)) : 
    naver_token_url = "https://nid.naver.com/oauth2.0/token"
    data = {
        "grant_type": "delete",
        "client_id": KEY["naver"]["id"],
        "client_secret": KEY["naver"]["pw"],
        "access_token": db.query(User).filter((User.id == id) & (User.social == "naver")).first().token,
        "service_provider": "NAVER"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }

    response = requests.post(naver_token_url, data=data, headers=headers)
    if response.json()["result"] == "success" :
        return  RedirectResponse("http://localhost:8000/naver")
