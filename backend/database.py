"""
Database models and configuration for Workplace Safety Monitoring
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/workplace_safety.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    oauth_provider = Column(String, nullable=False)  # "google" or "facebook"
    oauth_id = Column(String, unique=True, nullable=False)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    alert_config = relationship("AlertConfig", back_populates="user", uselist=False)
    videos = relationship("VideoProcessing", back_populates="user")


class AlertConfig(Base):
    """Alert configuration for users"""
    __tablename__ = "alert_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    enable_email = Column(Boolean, default=True)
    enable_sms = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="alert_config")


class VideoProcessing(Base):
    """Video processing records"""
    __tablename__ = "video_processing"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    status = Column(String, default="uploaded")  # uploaded, processing, safe, unsafe_detected, error
    result = Column(Text, nullable=True)  # JSON string with detection results
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="videos")


# Create all tables
def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)


# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Create database tables
    print("Creating database tables...")
    init_db()
    print("Database initialized successfully!")

