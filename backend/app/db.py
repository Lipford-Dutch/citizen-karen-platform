# backend/app/db.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/karing")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String(64), unique=True, index=True, nullable=False)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    agency = Column(String(128), nullable=True)  # resolved agency name
    payload = Column(JSON, nullable=False)
    status = Column(String(32), default="pending", nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)
