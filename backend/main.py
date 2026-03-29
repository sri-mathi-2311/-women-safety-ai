import sys

# Windows consoles often default to cp1252; emoji in print() raises UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import asyncio
import json
from datetime import datetime, timedelta
import time
import cv2
import numpy as np

import database
import models
import schemas
from websocket_manager import manager
from detection_service import detection_service

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    detection_service.loop = asyncio.get_running_loop()
    print("Women Safety AI Dashboard API Started")
    print("Database initialized")
    print("WebSocket ready")
    print("Ready to accept connections")
    yield
    # Shutdown
    print("Shutting down...")
    if detection_service.running:
        detection_service.stop()
    print("Cleanup complete")

app = FastAPI(title="Women Safety AI Dashboard", version="1.0.0", lifespan=lifespan)

# CORS — allow_origins=["*"] is invalid together with allow_credentials=True in browsers.
# Dev often uses Vite proxy (same origin); direct :5173→:8000 calls need explicit origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
system_state = {
    "running": False,
    "current_threat_level": "LOW",
    "current_confidence": 0.0,
    "persons_detected": 0,
    "last_update": None,
    "start_time": None,
    "total_uptime_before_current_session": 0,
}


def _sync_runtime_state():
    """Keep API state aligned with actual detection service state."""
    system_state["running"] = bool(detection_service.running)
    if detection_service.running:
        system_state["current_threat_level"] = detection_service.current_threat_level
        system_state["current_confidence"] = detection_service.current_confidence
        system_state["persons_detected"] = detection_service.persons_detected
        system_state["last_update"] = datetime.utcnow().isoformat()


def _get_current_uptime():
    """Calculate uptime based on running state."""
    if not system_state["running"] or not system_state["start_time"]:
        return system_state["total_uptime_before_current_session"]
    
    current_session_seconds = int((datetime.utcnow() - system_state["start_time"]).total_seconds())
    return system_state["total_uptime_before_current_session"] + current_session_seconds


# ============ REST API Endpoints ============

@app.get("/")
async def root():
    return {"message": "Women Safety AI Dashboard API", "version": "1.0.0"}

@app.get("/api/status")
async def get_status():
    """Get current system status"""
    _sync_runtime_state() # Always sync before returning
    uptime = _get_current_uptime()
    
    with detection_service.frame_lock:
        has_frame = detection_service.current_frame is not None

    return {
        "running": system_state["running"],
        "current_threat_level": system_state["current_threat_level"],
        "current_confidence": system_state["current_confidence"],
        "persons_detected": system_state["persons_detected"],
        "uptime_seconds": uptime,
        "last_update": system_state["last_update"],
        "last_error": detection_service.last_error,
        "camera_open": detection_service.camera is not None,
        "camera_has_frame": has_frame,
    }

@app.post("/api/control/start")
async def start_detection(db: Session = Depends(database.get_db)):
    """Start detection system"""
    _sync_runtime_state()
    if system_state["running"]:
        return {"status": "already_running", "message": "Detection system is already running"}
    
    # Start the actual detection service
    try:
        success = detection_service.start()
        _sync_runtime_state() # Immediately sync state after starting
        if not success:
            detail = detection_service.last_error or "Failed to start detection service (camera unavailable?)"
            raise HTTPException(status_code=500, detail=detail)
    except HTTPException:
        _sync_runtime_state() # Ensure state is synced even on error
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        _sync_runtime_state() # Ensure state is synced even on error
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
    system_state["start_time"] = datetime.utcnow()
    
    # Log system event
    event = models.SystemEvent(
        event_type="STARTED",
        description="Detection system started via API"
    )
    db.add(event)
    db.commit()
    
    # Broadcast to all clients
    await manager.broadcast({
        "type": "system",
        "data": {"status": "started", "timestamp": datetime.utcnow().isoformat()}
    })
    
    return {"status": "started", "message": "Detection system started successfully"}

@app.post("/api/control/stop")
async def stop_detection(db: Session = Depends(database.get_db)):
    """Stop detection system"""
    _sync_runtime_state()
    if not system_state["running"] and not detection_service.running:
        return {"status": "already_stopped", "message": "Detection system is already stopped"}

    # Calculate and store session uptime (only if we thought we were running)
    if system_state["start_time"]:
        session_seconds = int((datetime.utcnow() - system_state["start_time"]).total_seconds())
        system_state["total_uptime_before_current_session"] += session_seconds

    try:
        success = detection_service.stop()
        _sync_runtime_state()
        # stop() is idempotent: returns True when fully idle; never False after our fixes
        if not success:
            _sync_runtime_state()
            raise HTTPException(status_code=500, detail="Failed to stop detection service")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        _sync_runtime_state()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    system_state["running"] = False
    system_state["start_time"] = None

    try:
        event = models.SystemEvent(
            event_type="STOPPED",
            description="Detection system stopped via API",
        )
        db.add(event)
        db.commit()
    except Exception as db_err:
        # Service is stopped; still report success so the UI does not look broken
        sys.stderr.write(f"[WARN] DB log on stop failed: {db_err}\n")

    await manager.broadcast(
        {
            "type": "system",
            "data": {"status": "stopped", "timestamp": datetime.utcnow().isoformat()},
        }
    )

    return {"status": "stopped", "message": "Detection system stopped successfully"}

@app.get("/api/alerts", response_model=List[schemas.AlertResponse])
async def get_alerts(
    limit: int = 50,
    threat_level: str = None,
    db: Session = Depends(database.get_db)
):
    """Get alert history"""
    query = db.query(models.Alert)
    
    if threat_level:
        query = query.filter(models.Alert.threat_level == threat_level.upper())
    
    alerts = query.order_by(models.Alert.timestamp.desc()).limit(limit).all()
    return alerts

@app.get("/api/statistics")
async def get_statistics(db: Session = Depends(database.get_db)):
    """Get dashboard statistics"""
    # Today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_alerts = db.query(models.Alert).filter(models.Alert.timestamp >= today_start).all()
    
    # This week's stats
    week_start = datetime.utcnow() - timedelta(days=7)
    week_alerts = db.query(models.Alert).filter(models.Alert.timestamp >= week_start).all()
    
    # Calculate distributions
    today_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for alert in today_alerts:
        level = alert.threat_level
        if level in today_distribution:
            today_distribution[level] += 1
        else:
            # Handle potential unknown levels safely
            today_distribution[level] = 1
    
    uptime = _get_current_uptime()
    
    return {
        "today": {
            "total": len(today_alerts),
            "distribution": today_distribution,
        },
        "week": {
            "total": len(week_alerts),
        },
        "uptime_seconds": uptime,
    }

@app.get("/api/video/feed")
async def video_feed():
    """Stream video feed as MJPEG"""
    async def generate():
        while True:
            frame_bytes = detection_service.get_current_frame()
            
            if frame_bytes is None:
                # Send a black frame if camera not available
                black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(black_frame, "Camera Offline", (180, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(black_frame, "Click 'Start Detection' to begin", (150, 280),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                _, buffer = cv2.imencode('.jpg', black_frame)
                frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            await asyncio.sleep(0.04)  # ~25 FPS
    
    return StreamingResponse(
        generate(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )

@app.post("/api/alerts/create", response_model=schemas.AlertResponse)
async def create_alert(alert: schemas.AlertCreate, db: Session = Depends(database.get_db)):
    """Create new alert (called by detection system)"""
    db_alert = models.Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # Broadcast to all WebSocket clients
    await manager.broadcast({
        "type": "alert",
        "data": {
            "id": db_alert.id,
            "timestamp": db_alert.timestamp.isoformat(),
            "threat_level": db_alert.threat_level,
            "confidence": db_alert.confidence,
            "description": db_alert.description,
            "sms_sent": db_alert.sms_sent,
        }
    })
    
    return db_alert

@app.post("/api/alerts/test")
async def test_alert(db: Session = Depends(database.get_db)):
    """Send a test SMS alert to verify the system is working"""
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        from sms_alerts import SMSAlertSystem
        sms = SMSAlertSystem()
        if sms.enabled:
            result = sms.test_alert()
            sms_status = "sent" if result else "failed"
        else:
            sms_status = "disabled - missing Twilio credentials"
    except Exception as e:
        sms_status = f"error: {str(e)}"

    # Save a test alert record in DB
    db_alert = models.Alert(
        threat_level="LOW",
        confidence=100.0,
        description="Test alert triggered manually",
        sms_sent=sms_status == "sent",
        sms_status=sms_status,
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "alert",
        "data": {
            "id": db_alert.id,
            "timestamp": db_alert.timestamp.isoformat(),
            "threat_level": db_alert.threat_level,
            "confidence": db_alert.confidence,
            "description": db_alert.description,
            "sms_sent": db_alert.sms_sent,
        }
    })

    return {"status": "ok", "sms_status": sms_status, "message": "Test alert sent"}

# ============ WebSocket Endpoint ============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            try:
                data = await websocket.receive_text()
                # Check if it's JSON
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong", "data": {}}))
                except json.JSONDecodeError:
                    # Not JSON, just echo back if needed or ignore
                    pass
            except Exception as e:
                # Could be a connection reset or other issue
                print(f"WebSocket receive error: {e}")
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Startup/Shutdown is handled by the lifespan context manager above.