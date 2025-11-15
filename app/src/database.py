"""
Database connection and models
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Itinerary(Base):
    """Itinerary model"""
    __tablename__ = "itineraries"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    destination = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    preferences = Column(JSON)
    itinerary_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
