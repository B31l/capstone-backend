from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# 사용자 모델
class Note(Base) :
    __tablename__ = "note"
    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String(45), nullable=False)
    body = Column(Text, nullable=False)
    writer_id = Column(Integer, ForeignKey("writer.id"))
    writer = relationship("User", backref="notes")
    last_updated_date = Column(DateTime, nullable=False)


