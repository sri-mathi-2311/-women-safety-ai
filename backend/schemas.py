from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Alert Schemas
class AlertBase(BaseModel):
    threat_level: str
    confidence: float
    description: str
    pose_data: Optional[str] = None
    sms_sent: bool = False
    sms_status: Optional[str] = None
    screenshot_path: Optional[str] = None

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# System Event Schemas
class SystemEventBase(BaseModel):
    event_type: str
    description: str
    details: Optional[str] = None

class SystemEventCreate(SystemEventBase):
    pass

class SystemEventResponse(SystemEventBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Statistics Schemas
class StatisticsResponse(BaseModel):
    id: int
    date: datetime
    total_alerts: int
    low_alerts: int
    medium_alerts: int
    high_alerts: int
    critical_alerts: int
    total_persons_detected: int
    uptime_seconds: int
    
    class Config:
        from_attributes = True

# WebSocket Message Schema
class WebSocketMessage(BaseModel):
    type: str  # "alert", "status", "stats"
    data: dict