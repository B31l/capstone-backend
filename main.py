from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import user_router, note_router


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