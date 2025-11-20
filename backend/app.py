"""
FastAPI Backend for Workplace Safety Monitoring Application
Handles video processing, authentication, and notifications
"""
import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator
import torch
import yaml
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext

# Add parent directory to path to import from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.action_detector import create_model
from inference import UnsafeActionDetector
from backend.database import (
    get_db, User, VideoProcessing, AlertConfig, 
    Jurisdiction, Industry, Project, JurisdictionRegulation, 
    ActionSeverity, ProjectActionSeverity, Stream as StreamModel
)
from backend.notifications import send_email_alert, send_sms_alert
from backend.stream_manager import StreamManager, StreamConfig, validate_stream_url
from backend.model_registry import get_model_registry

# Initialize FastAPI app
app = FastAPI(title="Workplace Safety Monitoring API", version="1.0.0")

# CORS configuration - allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Load model configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize detector (singleton)
detector = None
stream_manager = None

def get_detector():
    global detector
    if detector is None:
        model_path = "checkpoints/best_model.pth"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        detector = UnsafeActionDetector(config, model_path)
    return detector


def get_detector_for_project(db: Session, project_id: int):
    """Get a detector configured for a specific project's jurisdiction and industry"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return get_detector()
    
    # Get model registry
    registry = get_model_registry()
    
    # Get appropriate model path
    model_path, model_type = registry.get_model_path(
        jurisdiction_code=project.jurisdiction.code,
        industry_code=project.industry.code,
        custom_path=project.model_path
    )
    
    # Create detector with project-specific model
    detector = UnsafeActionDetector(config, model_path)
    
    # Store project context for filtering
    detector.project_context = {
        "project_id": project.id,
        "jurisdiction_id": project.jurisdiction_id,
        "industry_id": project.industry_id,
        "min_severity_alert": project.min_severity_alert
    }
    
    return detector

def get_stream_manager():
    global stream_manager
    if stream_manager is None:
        detector = get_detector()
        stream_manager = StreamManager(detector)
        
        # Add alert handler for database logging
        async def alert_handler(stream_id: str, action: str, confidence: float):
            logger.info(f"Alert from stream {stream_id}: {action} ({confidence:.2%})")
            # Additional handling can be added here
        
        stream_manager.add_alert_handler(alert_handler)
    return stream_manager


# ===== Pydantic Models =====

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    oauth_provider: str  # "google" or "facebook"
    oauth_id: str
    picture: Optional[str] = None


class UserLogin(BaseModel):
    oauth_provider: str
    oauth_token: str


class AlertConfigUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    enable_email: bool = True
    enable_sms: bool = False
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone number must start with + and country code')
        return v


class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    status: str
    message: str


class AlertNotification(BaseModel):
    timestamp: str
    action: str
    confidence: float
    video_id: str
    clip_path: Optional[str] = None


class StreamCreate(BaseModel):
    name: str
    source_url: str
    source_type: str  # 'rtsp', 'rtmp', 'http', 'webcam'
    project_id: int
    fps: int = 30
    
    @validator('source_type')
    def validate_source_type(cls, v):
        allowed_types = ['rtsp', 'rtmp', 'http', 'webcam']
        if v not in allowed_types:
            raise ValueError(f'source_type must be one of {allowed_types}')
        return v
    
    @validator('fps')
    def validate_fps(cls, v):
        if v < 1 or v > 60:
            raise ValueError('fps must be between 1 and 60')
        return v


class ProjectCreate(BaseModel):
    name: str
    jurisdiction_id: int
    industry_id: int
    model_path: Optional[str] = None
    confidence_threshold_override: Optional[str] = None  # JSON string
    min_severity_alert: int = 1
    
    @validator('min_severity_alert')
    def validate_min_severity(cls, v):
        if v < 1 or v > 5:
            raise ValueError('min_severity_alert must be between 1 and 5')
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    model_path: Optional[str] = None
    confidence_threshold_override: Optional[str] = None
    min_severity_alert: Optional[int] = None
    
    @validator('min_severity_alert')
    def validate_min_severity(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('min_severity_alert must be between 1 and 5')
        return v


class ActionSeverityUpdate(BaseModel):
    action_name: str
    custom_severity_level: int
    
    @validator('custom_severity_level')
    def validate_severity(cls, v):
        if v < 1 or v > 5:
            raise ValueError('custom_severity_level must be between 1 and 5')
        return v


# ===== Authentication =====

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    import jwt
    from datetime import datetime, timedelta
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


async def verify_oauth_token(provider: str, token: str) -> dict:
    """Verify OAuth token with provider and return user info"""
    import httpx
    
    if provider == "google":
        # Verify Google OAuth token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google OAuth token"
                )
            user_info = response.json()
            return {
                "oauth_id": user_info["sub"],
                "email": user_info["email"],
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", "")
            }
    
    elif provider == "facebook":
        # Verify Facebook OAuth token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,picture",
                    "access_token": token
                }
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Facebook OAuth token"
                )
            user_info = response.json()
            return {
                "oauth_id": user_info["id"],
                "email": user_info.get("email", ""),
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", {}).get("data", {}).get("url", "")
            }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Workplace Safety Monitoring API",
        "version": "1.0.0"
    }


@app.post("/auth/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login or register user with OAuth token
    Verifies token with OAuth provider and creates/updates user
    """
    # Verify OAuth token with provider
    user_info = await verify_oauth_token(login_data.oauth_provider, login_data.oauth_token)
    
    # Check if user exists
    user = db.query(User).filter(
        User.oauth_provider == login_data.oauth_provider,
        User.oauth_id == user_info["oauth_id"]
    ).first()
    
    if not user:
        # Create new user
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            oauth_provider=login_data.oauth_provider,
            oauth_id=user_info["oauth_id"],
            picture=user_info.get("picture")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user info
        user.name = user_info["name"]
        user.picture = user_info.get("picture")
        user.last_login = datetime.utcnow()
        db.commit()
    
    # Create access token
    access_token = create_access_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    }


@app.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "created_at": current_user.created_at.isoformat()
    }


@app.get("/config/alerts")
async def get_alert_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's alert configuration"""
    alert_config = db.query(AlertConfig).filter(
        AlertConfig.user_id == current_user.id
    ).first()
    
    if not alert_config:
        # Return default config
        return {
            "email": current_user.email,
            "phone": None,
            "enable_email": True,
            "enable_sms": False
        }
    
    return {
        "email": alert_config.email,
        "phone": alert_config.phone,
        "enable_email": alert_config.enable_email,
        "enable_sms": alert_config.enable_sms
    }


@app.put("/config/alerts")
async def update_alert_config(
    config: AlertConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's alert configuration"""
    alert_config = db.query(AlertConfig).filter(
        AlertConfig.user_id == current_user.id
    ).first()
    
    if not alert_config:
        # Create new config
        alert_config = AlertConfig(
            user_id=current_user.id,
            email=config.email or current_user.email,
            phone=config.phone,
            enable_email=config.enable_email,
            enable_sms=config.enable_sms
        )
        db.add(alert_config)
    else:
        # Update existing config
        if config.email:
            alert_config.email = config.email
        if config.phone:
            alert_config.phone = config.phone
        alert_config.enable_email = config.enable_email
        alert_config.enable_sms = config.enable_sms
    
    db.commit()
    db.refresh(alert_config)
    
    return {
        "message": "Alert configuration updated successfully",
        "config": {
            "email": alert_config.email,
            "phone": alert_config.phone,
            "enable_email": alert_config.enable_email,
            "enable_sms": alert_config.enable_sms
        }
    }


# ===== Jurisdiction & Industry Management =====

@app.get("/jurisdictions")
async def list_jurisdictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available jurisdictions"""
    jurisdictions = db.query(Jurisdiction).filter(Jurisdiction.is_active == True).all()
    
    return {
        "jurisdictions": [
            {
                "id": j.id,
                "name": j.name,
                "code": j.code,
                "country": j.country,
                "regulation_url": j.regulation_url,
                "description": j.description
            }
            for j in jurisdictions
        ]
    }


@app.get("/industries")
async def list_industries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available industries"""
    industries = db.query(Industry).filter(Industry.is_active == True).all()
    
    return {
        "industries": [
            {
                "id": i.id,
                "name": i.name,
                "code": i.code,
                "description": i.description,
                "hazard_categories": json.loads(i.hazard_categories) if i.hazard_categories else []
            }
            for i in industries
        ]
    }


@app.get("/jurisdictions/{jurisdiction_id}/regulations")
async def get_regulations(
    jurisdiction_id: int,
    industry_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get regulations for a specific jurisdiction and optionally industry"""
    query = db.query(JurisdictionRegulation).filter(
        JurisdictionRegulation.jurisdiction_id == jurisdiction_id
    )
    
    if industry_id:
        query = query.filter(JurisdictionRegulation.industry_id == industry_id)
    
    regulations = query.all()
    
    return {
        "regulations": [
            {
                "id": r.id,
                "regulation_code": r.regulation_code,
                "title": r.title,
                "description": r.description,
                "violation_mapping": json.loads(r.violation_mapping) if r.violation_mapping else {},
                "industry_id": r.industry_id
            }
            for r in regulations
        ]
    }


# ===== Project Management =====

@app.post("/projects")
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    # Validate jurisdiction exists
    jurisdiction = db.query(Jurisdiction).filter(Jurisdiction.id == project_data.jurisdiction_id).first()
    if not jurisdiction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jurisdiction not found"
        )
    
    # Validate industry exists
    industry = db.query(Industry).filter(Industry.id == project_data.industry_id).first()
    if not industry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry not found"
        )
    
    # Create project
    project = Project(
        user_id=current_user.id,
        name=project_data.name,
        jurisdiction_id=project_data.jurisdiction_id,
        industry_id=project_data.industry_id,
        model_path=project_data.model_path,
        confidence_threshold_override=project_data.confidence_threshold_override,
        min_severity_alert=project_data.min_severity_alert
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return {
        "project_id": project.id,
        "name": project.name,
        "jurisdiction": {
            "id": jurisdiction.id,
            "name": jurisdiction.name,
            "code": jurisdiction.code
        },
        "industry": {
            "id": industry.id,
            "name": industry.name,
            "code": industry.code
        },
        "min_severity_alert": project.min_severity_alert,
        "created_at": project.created_at.isoformat()
    }


@app.get("/projects")
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's projects"""
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    
    return {
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "jurisdiction": {
                    "id": p.jurisdiction.id,
                    "name": p.jurisdiction.name,
                    "code": p.jurisdiction.code
                },
                "industry": {
                    "id": p.industry.id,
                    "name": p.industry.name,
                    "code": p.industry.code
                },
                "min_severity_alert": p.min_severity_alert,
                "video_count": len(p.videos),
                "stream_count": len(p.streams),
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat()
            }
            for p in projects
        ]
    }


@app.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get action severities for this jurisdiction/industry
    action_severities = db.query(ActionSeverity).filter(
        ActionSeverity.jurisdiction_id == project.jurisdiction_id,
        ActionSeverity.industry_id == project.industry_id
    ).all()
    
    # Get custom severities for this project
    custom_severities = db.query(ProjectActionSeverity).filter(
        ProjectActionSeverity.project_id == project_id
    ).all()
    
    custom_severity_map = {cs.action_name: cs.custom_severity_level for cs in custom_severities}
    
    # Get videos associated with this project
    videos = db.query(VideoProcessing).filter(
        VideoProcessing.project_id == project_id
    ).order_by(VideoProcessing.uploaded_at.desc()).all()
    
    # Get video statistics
    total_videos = len(videos)
    safe_videos = sum(1 for v in videos if v.status == "safe")
    unsafe_videos = sum(1 for v in videos if v.status == "unsafe_detected")
    processing_videos = sum(1 for v in videos if v.status in ["uploaded", "processing"])
    
    # Get stream count
    active_streams = db.query(StreamModel).filter(
        StreamModel.project_id == project_id,
        StreamModel.status == "active"
    ).count()
    
    return {
        "id": project.id,
        "name": project.name,
        "jurisdiction": {
            "id": project.jurisdiction.id,
            "name": project.jurisdiction.name,
            "code": project.jurisdiction.code,
            "regulation_url": project.jurisdiction.regulation_url
        },
        "industry": {
            "id": project.industry.id,
            "name": project.industry.name,
            "code": project.industry.code
        },
        "model_path": project.model_path,
        "confidence_threshold_override": json.loads(project.confidence_threshold_override) if project.confidence_threshold_override else None,
        "min_severity_alert": project.min_severity_alert,
        "action_severities": [
            {
                "action_name": asev.action_name,
                "severity_level": custom_severity_map.get(asev.action_name, asev.severity_level),
                "default_severity": asev.severity_level,
                "is_custom": asev.action_name in custom_severity_map,
                "notification_priority": asev.notification_priority,
                "description": asev.description
            }
            for asev in action_severities
        ],
        "stats": {
            "total_videos": total_videos,
            "safe_videos": safe_videos,
            "unsafe_videos": unsafe_videos,
            "processing_videos": processing_videos,
            "active_streams": active_streams
        },
        "videos": [
            {
                "video_id": v.id,
                "filename": v.filename,
                "status": v.status,
                "uploaded_at": v.uploaded_at.isoformat(),
                "processed_at": v.processed_at.isoformat() if v.processed_at else None
            }
            for v in videos
        ],
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat()
    }


@app.put("/projects/{project_id}")
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project settings"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    if project_update.name is not None:
        project.name = project_update.name
    if project_update.model_path is not None:
        project.model_path = project_update.model_path
    if project_update.confidence_threshold_override is not None:
        project.confidence_threshold_override = project_update.confidence_threshold_override
    if project_update.min_severity_alert is not None:
        project.min_severity_alert = project_update.min_severity_alert
    
    db.commit()
    db.refresh(project)
    
    return {
        "message": "Project updated successfully",
        "project_id": project.id,
        "name": project.name
    }


@app.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if project has active streams
    active_streams = db.query(StreamModel).filter(
        StreamModel.project_id == project_id,
        StreamModel.status == "active"
    ).count()
    
    if active_streams > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project with active streams. Stop all streams first."
        )
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}


@app.put("/projects/{project_id}/action-severity")
async def update_action_severity(
    project_id: int,
    severity_update: ActionSeverityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update custom severity level for an action in a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if custom severity already exists
    custom_severity = db.query(ProjectActionSeverity).filter(
        ProjectActionSeverity.project_id == project_id,
        ProjectActionSeverity.action_name == severity_update.action_name
    ).first()
    
    if custom_severity:
        custom_severity.custom_severity_level = severity_update.custom_severity_level
    else:
        custom_severity = ProjectActionSeverity(
            project_id=project_id,
            action_name=severity_update.action_name,
            custom_severity_level=severity_update.custom_severity_level
        )
        db.add(custom_severity)
    
    db.commit()
    
    return {
        "message": "Action severity updated successfully",
        "action_name": severity_update.action_name,
        "custom_severity_level": severity_update.custom_severity_level
    }


async def process_video_task(
    video_id: str,
    video_path: str,
    user_id: str,
    project_id: Optional[int] = None,
):
    """Process video in a worker thread so the event loop stays responsive."""
    from backend.database import SessionLocal

    def _send_email(alert_config, action, confidence, filename):
        try:
            asyncio.run(send_email_alert(
                alert_config.email,
                action,
                confidence,
                filename
            ))
        except Exception as notify_err:
            print(f"Failed to send email alert: {notify_err}")

    def _send_sms(alert_config, action, confidence, filename):
        try:
            asyncio.run(send_sms_alert(
                alert_config.phone,
                action,
                confidence,
                filename
            ))
        except Exception as notify_err:
            print(f"Failed to send SMS alert: {notify_err}")

    def worker():
        db = SessionLocal()
        try:
            video_record = db.query(VideoProcessing).filter(
                VideoProcessing.id == video_id
            ).first()
            if not video_record:
                return

            video_record.status = "processing"
            db.commit()

            # Get detector with project-specific model if available
            detector = get_detector_for_project(db, project_id) if project_id else get_detector()

            alert_config = db.query(AlertConfig).filter(
                AlertConfig.user_id == user_id
            ).first()
            
            # Get project for severity filtering
            project = None
            if project_id:
                project = db.query(Project).filter(Project.id == project_id).first()

            import cv2
            cap = cv2.VideoCapture(video_path)

            unsafe_actions_detected = []

            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    result = detector.process_frame(frame)

                    if result.get('alert') and result.get('is_unsafe'):
                        action = result['action']
                        confidence = result['confidence']

                        if alert_config:
                            if alert_config.enable_email and alert_config.email:
                                _send_email(alert_config, action, confidence, video_record.filename)

                            if alert_config.enable_sms and alert_config.phone:
                                _send_sms(alert_config, action, confidence, video_record.filename)

                        unsafe_actions_detected.append({
                            "action": action,
                            "confidence": float(confidence),
                            "timestamp": datetime.now().isoformat()
                        })
            finally:
                cap.release()

            if unsafe_actions_detected:
                video_record.status = "unsafe_detected"
                video_record.result = json.dumps({
                    "unsafe_actions": unsafe_actions_detected,
                    "total_detections": len(unsafe_actions_detected)
                })
            else:
                video_record.status = "safe"
                video_record.result = json.dumps({
                    "unsafe_actions": [],
                    "total_detections": 0
                })

            video_record.processed_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            video_record = db.query(VideoProcessing).filter(
                VideoProcessing.id == video_id
            ).first()
            if video_record:
                video_record.status = "error"
                video_record.result = json.dumps({"error": str(e)})
                db.commit()
            print(f"Error processing video: {e}")
        finally:
            db.close()

    await asyncio.to_thread(worker)


@app.post("/videos/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload video for processing
    Video will be processed in background and alerts sent if unsafe actions detected
    """
    # Validate project if provided
    if project_id:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    # Validate file type
    if not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )
    
    # Create uploads directory
    upload_dir = Path("backend/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    import uuid
    video_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    video_filename = f"{video_id}{file_extension}"
    video_path = upload_dir / video_filename
    
    # Save uploaded file in chunks to avoid blocking the event loop
    with open(video_path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    await file.close()
    
    # Create video processing record
    video_record = VideoProcessing(
        id=video_id,
        user_id=current_user.id,
        project_id=project_id,
        filename=file.filename,
        filepath=str(video_path),
        status="uploaded"
    )
    db.add(video_record)
    db.commit()
    
    # Kick off processing without blocking the response cycle
    asyncio.create_task(
        process_video_task(
            video_id,
            str(video_path),
            current_user.id,
            project_id,
        )
    )
    
    return VideoUploadResponse(
        video_id=video_id,
        filename=file.filename,
        status="uploaded",
        message="Video uploaded successfully. Processing in background..."
    )


@app.get("/videos/{video_id}")
async def get_video_status(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get video processing status and results"""
    video = db.query(VideoProcessing).filter(
        VideoProcessing.id == video_id,
        VideoProcessing.user_id == current_user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    result_data = json.loads(video.result) if video.result else {}
    
    # Get project information if associated
    project_info = None
    if video.project_id:
        project = db.query(Project).filter(Project.id == video.project_id).first()
        if project:
            jurisdiction = db.query(Jurisdiction).filter(Jurisdiction.id == project.jurisdiction_id).first()
            industry = db.query(Industry).filter(Industry.id == project.industry_id).first()
            project_info = {
                "id": project.id,
                "name": project.name,
                "jurisdiction": {
                    "id": jurisdiction.id,
                    "name": jurisdiction.name,
                    "code": jurisdiction.code
                } if jurisdiction else None,
                "industry": {
                    "id": industry.id,
                    "name": industry.name,
                    "code": industry.code
                } if industry else None
            }
    
    return {
        "video_id": video.id,
        "filename": video.filename,
        "status": video.status,
        "uploaded_at": video.uploaded_at.isoformat(),
        "processed_at": video.processed_at.isoformat() if video.processed_at else None,
        "result": result_data,
        "filepath": video.filepath,
        "project": project_info
    }


from fastapi.responses import FileResponse

async def get_user_from_token(token: str, db: Session) -> User:
    """Verify token and return user"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


@app.get("/videos/{video_id}/download")
async def download_video(
    video_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Download the original video file"""
    # Authenticate using token from query param
    user = await get_user_from_token(token, db)
    
    video = db.query(VideoProcessing).filter(
        VideoProcessing.id == video_id,
        VideoProcessing.user_id == user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    video_path = Path(video.filepath)
    if not video_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found on server"
        )
    
    return FileResponse(
        path=str(video_path),
        media_type='video/mp4',
        filename=video.filename,
        headers={
            "Content-Disposition": f"attachment; filename={video.filename}"
        }
    )


@app.get("/videos/{video_id}/stream")
async def stream_video(
    video_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    """Stream video for playback in browser"""
    # Authenticate using token from query param
    user = await get_user_from_token(token, db)
    
    video = db.query(VideoProcessing).filter(
        VideoProcessing.id == video_id,
        VideoProcessing.user_id == user.id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    video_path = Path(video.filepath)
    if not video_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found on server"
        )
    
    return FileResponse(
        path=str(video_path),
        media_type='video/mp4',
        filename=video.filename
    )


@app.get("/videos")
async def list_videos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """List user's uploaded videos"""
    videos = db.query(VideoProcessing).filter(
        VideoProcessing.user_id == current_user.id
    ).order_by(VideoProcessing.uploaded_at.desc()).limit(limit).offset(offset).all()
    
    video_list = []
    for v in videos:
        video_data = {
            "video_id": v.id,
            "filename": v.filename,
            "status": v.status,
            "uploaded_at": v.uploaded_at.isoformat(),
            "processed_at": v.processed_at.isoformat() if v.processed_at else None,
            "project": None
        }
        
        # Add project info if associated
        if v.project_id:
            project = db.query(Project).filter(Project.id == v.project_id).first()
            if project:
                video_data["project"] = {
                    "id": project.id,
                    "name": project.name
                }
        
        video_list.append(video_data)
    
    return {
        "videos": video_list,
        "total": db.query(VideoProcessing).filter(
            VideoProcessing.user_id == current_user.id
        ).count()
    }


# ===== Live Streaming Endpoints =====

@app.post("/streams")
async def create_stream(
    stream_data: StreamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create and start a new live video stream
    Supports RTSP, RTMP, HTTP streams, and webcams
    """
    # Validate project exists and belongs to user
    project = db.query(Project).filter(
        Project.id == stream_data.project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Validate stream URL
    if not validate_stream_url(stream_data.source_url, stream_data.source_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {stream_data.source_type} URL format"
        )
    
    # Generate unique stream ID
    import uuid
    stream_id = str(uuid.uuid4())
    
    # Create stream configuration
    stream_config = StreamConfig(
        stream_id=stream_id,
        name=stream_data.name,
        source_url=stream_data.source_url,
        source_type=stream_data.source_type,
        status='inactive',
        fps=stream_data.fps,
        created_at=datetime.now().isoformat()
    )
    
    # Add stream to manager
    manager = get_stream_manager()
    success = manager.add_stream(stream_config)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start stream"
        )
    
    # Save stream to database
    stream_db = StreamModel(
        id=stream_id,
        project_id=stream_data.project_id,
        name=stream_data.name,
        source_url=stream_data.source_url,
        source_type=stream_data.source_type,
        status="active",
        fps=stream_data.fps
    )
    db.add(stream_db)
    db.commit()
    
    return {
        "stream_id": stream_id,
        "name": stream_data.name,
        "status": "active",
        "message": "Stream started successfully"
    }


@app.get("/streams")
async def list_streams(
    current_user: User = Depends(get_current_user)
):
    """List all active streams"""
    manager = get_stream_manager()
    streams = manager.list_streams()
    
    return {
        "streams": streams,
        "total": len(streams)
    }


@app.get("/streams/{stream_id}")
async def get_stream_status(
    stream_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get status and details of a specific stream"""
    manager = get_stream_manager()
    stream = manager.get_stream(stream_id)
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    return stream.get_status()


@app.delete("/streams/{stream_id}")
async def delete_stream(
    stream_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stop and remove a stream"""
    manager = get_stream_manager()
    success = manager.remove_stream(stream_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    return {
        "message": "Stream stopped and removed successfully"
    }


@app.get("/streams/{stream_id}/frame")
async def get_stream_frame(
    stream_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get current frame from stream as base64 encoded JPEG
    Used for polling-based video display in frontend
    """
    manager = get_stream_manager()
    frame_base64 = manager.get_stream_frame(stream_id, format='base64')
    
    if frame_base64 is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found or no frame available"
        )
    
    return {
        "stream_id": stream_id,
        "frame": frame_base64,
        "timestamp": datetime.now().isoformat()
    }


from fastapi.responses import StreamingResponse

@app.get("/streams/{stream_id}/video")
async def stream_video(
    stream_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Stream video as MJPEG (Motion JPEG) for continuous playback
    This provides a continuous video stream that can be displayed in an <img> tag
    """
    manager = get_stream_manager()
    stream = manager.get_stream(stream_id)
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    def generate():
        """Generate MJPEG stream"""
        while stream.is_running:
            frame_jpeg = stream.get_frame_jpeg()
            if frame_jpeg is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_jpeg + b'\r\n')
            time.sleep(1.0 / stream.config.fps)
    
    return StreamingResponse(
        generate(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

