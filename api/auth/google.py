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
        "response_type" : "token",
        "state" : str,
        "redirect_uri": "http://localhost:8000/google/auth",
        "scope" : "https://www.googleapis.com/auth/userinfo.email"
    }
    google_login_url = google_url + urlencode(google_params)
    return RedirectResponse(google_login_url)
