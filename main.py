from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from api import user_router, note_router
from api.auth import kakao, naver, google
from services import UserService, NoteService, TodoService, WeeklyService
from datetime import datetime
import json

app = FastAPI()

# CORS 예외 URL 설정
# React 기본 포트인 3000 등록
origins = [
    "*",
    # "http://localhost:3000",
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
app.include_router(kakao.router)
app.include_router(naver.router)
app.include_router(user_router.router)
app.include_router(note_router.router)
app.include_router(google.router)
app.include_router(UserService.router)
app.include_router(NoteService.router)
app.include_router(TodoService.router)
app.include_router(WeeklyService.router)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
#
@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            message = {"time": current_time, "clientId": client_id, "message": data}
            await manager.broadcast(json.dumps(message))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        message = {"time": current_time, "clientId": client_id, "message": "Offline"}
        await manager.broadcast(json.dumps(message))


##########
# 본인 mysql의 user이름, password, db이름 작성
##########
# from pymysql import cursors
# conn = pymysql.connect(host='127.0.0.1', user='--', password='--', db='--', charset='utf8')
# cursor = conn.cursor(cursors.DictCursor)
# Base.metadata.create_all(bind=engine)