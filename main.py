from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import user_router, note_router



# 네이버, 카카오 로그인 시 필요
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from models import User
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse
import httpx
from database import get_db

app = FastAPI()
# CORS 예외 URL 설정
# React 기본 포트인 3000 등록
origins = [
    "http://localhost:3000",
]
# 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # request에서 cookie 허용
    allow_methods=["*"],    # 전체 method 허용
    allow_headers=["*"],    # 전체 header 허용
)
# 라우터 설정
app.include_router(user_router.router)
app.include_router(note_router.router)

@app.get('/')
async def hello():
    return {'message': 'Hello World'}

##########
# 본인 mysql의 user이름, password, db이름 작성
##########
# from pymysql import cursors
# conn = pymysql.connect(host='127.0.0.1', user='--', password='--', db='--', charset='utf8')
# cursor = conn.cursor(cursors.DictCursor)
# Base.metadata.create_all(bind=engine)

##########
# serverless
##########
# from api_serverless.api_v1.api import router as api_router
# from mangum import Mangum
# handler = Mangum(app)



################ 네이버 카카오 로그인 

# 카카오 로그인
@app.get("/kakao")
async def login_kakao(request : Request) :
    kakao_url = "https://kauth.kakao.com/oauth/authorize?"
    kakao_params = {
        "response_type" : "code",
        "client_id" : "--",
        "redirect_uri" : "http://localhost:8000/kakao/auth"
    }
    kakao_login_url = kakao_url + urlencode(kakao_params)
    return RedirectResponse(kakao_login_url)

@app.get("/kakao/auth")
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

# 네이버 로그인
@app.get("/naver")
async def login_naver(request: Request) :
    naver_url = "https://nid.naver.com/oauth2.0/authorize?"
    naver_params = {
        "client_id": "-",
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/naver/auth",
        "state": str
    }
    naver_login_url = naver_url + urlencode(naver_params)
    return RedirectResponse(naver_login_url)

@app.get("/naver/auth")
async def callback_naver(request: Request, code: str, state: str, db : Session = Depends(get_db)) :
    naver_token_url = "https://nid.naver.com/oauth2.0/token"
    naver_data = {
        "grant_type": "authorization_code",
        "client_id": "--",
        "client_secret": "--",
        "code": code,
        "state": state,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(naver_token_url, data=naver_data, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get("https://openapi.naver.com/v1/nid/me", headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            try :
                db_user = User(id=response_json["response"]["id"], password="", nickname=response_json["response"]["name"], goals="", groups="", profile_image="", notes="", chats="")
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
            except :
                RedirectResponse("http://localhost:8000/naver")
            return response_json
        else:
            return {"error": "failed to get user info"}
    else:
        return {"error": "failed to get access token"}
