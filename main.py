from fastapi import FastAPI

app = FastAPI()


@app.get('/hello')
def Hello():
    return {"message": '안녕하세요'}