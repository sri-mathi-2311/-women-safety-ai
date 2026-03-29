from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    threat_level = Column(String)  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float)
    description = Column(String)
    pose_data = Column(String)  # JSON string of pose landmarks
    sms_sent = Column(Boolean, default=False)
    sms_status = Column(String, nullable=True)
    screenshot_path = Column(String, nullable=True)

class SystemEvent(Base):
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)  # STARTED, STOPPED, ERROR, CONFIG_CHANGE
    description = Column(String)
    details = Column(String, nullable=True)  # JSON string

class Statistics(Base):
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_alerts = Column(Integer, default=0)
    low_alerts = Column(Integer, default=0)
    medium_alerts = Column(Integer, default=0)
    high_alerts = Column(Integer, default=0)
    critical_alerts = Column(Integer, default=0)
    total_persons_detected = Column(Integer, default=0)
    uptime_seconds = Column(Integer, default=0)