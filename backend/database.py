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
    projects = relationship("Project", back_populates="user")


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


class Jurisdiction(Base):
    """Jurisdiction model for regional regulations"""
    __tablename__ = "jurisdictions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Ontario"
    code = Column(String, unique=True, nullable=False, index=True)  # e.g., "ontario"
    country = Column(String, nullable=False)  # e.g., "Canada"
    regulation_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="jurisdiction")
    regulations = relationship("JurisdictionRegulation", back_populates="jurisdiction")
    action_severities = relationship("ActionSeverity", back_populates="jurisdiction")


class Industry(Base):
    """Industry model for industry-specific safety standards"""
    __tablename__ = "industries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Food Safety"
    code = Column(String, unique=True, nullable=False, index=True)  # e.g., "food_safety"
    description = Column(Text, nullable=True)
    hazard_categories = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="industry")
    regulations = relationship("JurisdictionRegulation", back_populates="industry")
    action_severities = relationship("ActionSeverity", back_populates="industry")


class Project(Base):
    """Project model for organizing cameras and videos by jurisdiction/industry"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    jurisdiction_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=False)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    model_path = Column(String, nullable=True)  # Custom model path (optional)
    confidence_threshold_override = Column(String, nullable=True)  # JSON for custom thresholds
    min_severity_alert = Column(Integer, default=1)  # Minimum severity level to trigger alerts (1-5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    jurisdiction = relationship("Jurisdiction", back_populates="projects")
    industry = relationship("Industry", back_populates="projects")
    videos = relationship("VideoProcessing", back_populates="project")
    streams = relationship("Stream", back_populates="project")
    custom_severities = relationship("ProjectActionSeverity", back_populates="project")


class JurisdictionRegulation(Base):
    """Regulations specific to jurisdiction and industry combinations"""
    __tablename__ = "jurisdiction_regulations"
    
    id = Column(Integer, primary_key=True, index=True)
    jurisdiction_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=False)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    regulation_code = Column(String, nullable=False)  # e.g., "OHSA_25(2)(h)"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    violation_mapping = Column(Text, nullable=True)  # JSON mapping unsafe actions to violations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="regulations")
    industry = relationship("Industry", back_populates="regulations")


class ActionSeverity(Base):
    """Severity levels for unsafe actions by jurisdiction and industry"""
    __tablename__ = "action_severities"
    
    id = Column(Integer, primary_key=True, index=True)
    action_name = Column(String, nullable=False, index=True)
    jurisdiction_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=False)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    severity_level = Column(Integer, nullable=False)  # 1=Low, 2=Medium, 3=High, 4=Critical, 5=Emergency
    default_severity = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    notification_priority = Column(String, default="normal")  # low, normal, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="action_severities")
    industry = relationship("Industry", back_populates="action_severities")


class ProjectActionSeverity(Base):
    """Custom severity overrides for specific projects"""
    __tablename__ = "project_action_severities"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    action_name = Column(String, nullable=False)
    custom_severity_level = Column(Integer, nullable=False)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="custom_severities")


class Stream(Base):
    """Live stream configurations"""
    __tablename__ = "streams"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    source_url = Column(String, nullable=False)  # URL for AI detection
    browser_preview_url = Column(String, nullable=True)  # Optional URL for browser viewing (uses source_url if NULL)
    source_type = Column(String, nullable=False)  # rtsp, rtmp, http, webcam
    status = Column(String, default="inactive")  # inactive, active, error
    error_message = Column(Text, nullable=True)  # Error details if status is 'error'
    fps = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="streams")


class VideoProcessing(Base):
    """Video processing records"""
    __tablename__ = "video_processing"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # Nullable for backward compatibility
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    status = Column(String, default="uploaded")  # uploaded, processing, safe, unsafe_detected, error
    result = Column(Text, nullable=True)  # JSON string with detection results
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="videos")
    project = relationship("Project", back_populates="videos")


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

