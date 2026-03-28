from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String)  # news, social, web
    source_name = Column(String)
    content = Column(String)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class Trend(Base):
    __tablename__ = "trends"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    score = Column(Float)
    signal_count = Column(Integer)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
