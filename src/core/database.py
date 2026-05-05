import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///database.sqlite"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ProductWatch(Base):
    __tablename__ = "product_watches"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True, nullable=False)
    keywords = Column(String, nullable=False) # comma-separated keywords
    is_active = Column(Boolean, default=True)

class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    price_found = Column(String)
    original_link = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    group_id = Column(String) # To help with debugging where it came from

class MonitoredGroup(Base):
    __tablename__ = "monitored_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_username_or_id = Column(String, unique=True, index=True, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado.")
