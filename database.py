from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/Capstone"

class EngineConn:
    def __init__(self):
        self.engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )

    def sessionmaker(self):
        Session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn