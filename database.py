from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_FILE = os.path.join(BASE_DIR, 'secrets.json')
secrets = json.loads(open(SECRET_FILE).read())
DB = secrets["DB"]
DB_URL = f"mysql+mysqldb://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}/{DB['database']}?charset=utf8"
engine = create_engine(
    DB_URL
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() :
    db = SessionLocal()
    try :
        yield db
    finally :
        db.close()

