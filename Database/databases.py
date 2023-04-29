from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 'mysql+mysqldb://{userName}:{password}@localhost:3306/{DBname}'
DB_URL = 'mysql+mysqldb://--:--@localhost:3306/--'

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()