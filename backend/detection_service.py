import cv2
import threading
import time
import requests
import json
import numpy as np
from datetime import datetime
import asyncio
import queue
from collections import deque
from websocket_manager import manager

import sys
import os

from safe_log import log as _log

_log(f"DEBUG: detection_service.py loading... PID={os.getpid()}")

# Windows: default MSMF backend often fails with some USB webcams; DirectShow is more reliable.

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

ObjectDetector = None
PoseAnalyzer = None
SMSAlert = None
AgenticDecisionMaker = None

class DetectionService:
    def __init__(self):
        self.running = False
        self.threads = []
        self.camera = None
        self.last_error = None
        
        # Detection components
        self.object_detector = None
        self.pose_analyzer = None
        self.sms_alert = None
        self.decision_maker = None
        
        # Inter-Agent Event Buses
        self.frame_queue = queue.Queue(maxsize=2)
        self.perception_queue = queue.Queue(maxsize=10)
        self.decision_queue = queue.Queue(maxsize=10)
        
        # State
        self.current_threat_level = "LOW"
        self.current_confidence = 0.0
        self.persons_detected = 0
        self.last_alert_time = 0
        self.alert_cooldown = 30  # seconds
        self.recent_confidences = deque(maxlen=8)
        self.calibration_log_path = os.getenv("SAFETY_CALIBRATION_LOG", "calibration_samples.jsonl")
        self.last_calibration_log_time = 0.0
        
        # Frame storage for video streaming
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
    def initialize_components(self):
        """Initialize detection components"""
        global ObjectDetector, PoseAnalyzer, SMSAlert, AgenticDecisionMaker
        
        # Avoid re-initialization if already done
        if self.object_detector and self.pose_analyzer:
            return True
            
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        _log(f"📁 Looking for detection modules in: {project_root}")
        
        try:
            try:
                import object_detection
                ObjectDetector = object_detection.ObjectDetector
                _log("  ✅ ObjectDetector imported")
                try:
                    self.object_detector = ObjectDetector()
                    _log("✅ Object detector initialized")
                except Exception as e:
                    _log(f"  ❌ Object detector initialization failed: {e}")
            except Exception as e:
                _log(f"  ❌ ObjectDetector failed: {e}")
            
            try:
                import pose_analysis
                PoseAnalyzer = pose_analysis.PoseAnalyzer
                _log("  ✅ PoseAnalyzer imported")
                try:
                    self.pose_analyzer = PoseAnalyzer()
                    _log("✅ Pose analyzer initialized")
                except Exception as e:
                    _log(f"  ❌ Pose analyzer initialization failed: {e}")
            except Exception as e:
                _log(f"  ❌ PoseAnalyzer failed: {e}")
            
            try:
                import sms_alerts
                SMSAlert = sms_alerts.SMSAlertSystem
                _log("  ✅ SMSAlert imported")
                try:
                    self.sms_alert = SMSAlert()
                    _log("✅ SMS alert initialized")
                except Exception as e:
                    _log(f"  ❌ SMS alert initialization failed: {e}")
            except Exception as e:
                _log(f"  ❌ SMSAlert failed: {e}")

            try:
                import agentic_decision
                AgenticDecisionMaker = agentic_decision.AgenticDecisionMaker
                _log("  ✅ AgenticDecisionMaker imported")
                try:
                    self.decision_maker = AgenticDecisionMaker(history_size=16)
                    _log("✅ Multi-agent decision maker initialized")
                except Exception as e:
                    _log(f"  ❌ AgenticDecisionMaker initialization failed: {e}")
            except Exception as e:
                _log(f"  ❌ AgenticDecisionMaker failed: {e}")
                
            return True
        except Exception as e:
            _log(f"❌ Failed to initialize components: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _open_camera(self):
        """
        Open a webcam with retries. On Windows, CAP_DSHOW is usually required for stable USB cameras.
        Env: SAFETY_CAMERA_INDEX (default 0), optional SAFETY_CAMERA_TRY_ALL=1 to scan 0..3.
        """
        self.last_error = None
        
        # --- VIRTUAL CAMERA FALLBACK ---
        if os.getenv("SAFETY_USE_VIRTUAL_CAMERA", "0") == "1":
            _log("🎬 Using virtual camera fallback (random noise)")
            self.camera = "VIRTUAL"
            return True

        preferred = int(os.getenv("SAFETY_CAMERA_INDEX", "0"))
        try_all = os.getenv("SAFETY_CAMERA_TRY_ALL", "").lower() in ("1", "true", "yes")
        if try_all:
            indices = list(range(4))
        else:
            indices = [preferred]
            for alt in (1, 0, 2, 3):
                if alt not in indices:
                    indices.append(alt)

        if sys.platform == "win32":
            # Try MSMF first on recent Windows; some devices only stabilize after warmup on MSMF.
            backends = [
                (cv2.CAP_MSMF, "Media Foundation"),
                (cv2.CAP_DSHOW, "DirectShow"),
            ]
        else:
            backends = [(None, "default")]

        for idx in indices:
            for backend_id, backend_name in backends:
                cap = None
                try:
                    if backend_id is None:
                        cap = cv2.VideoCapture(idx)
                    else:
                        cap = cv2.VideoCapture(idx, backend_id)
                    if not cap.isOpened():
                        if cap is not None:
                            cap.release()
                        continue
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

                    # USB / virtual cameras often return empty frames until the driver warms up.
                    frame = None
                    for _ in range(45):
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            break
                        time.sleep(0.04)
                    if frame is None or frame.size == 0:
                        _log(
                            f"⚠️ Camera index {idx} ({backend_name}) opened but no valid frame after warmup — trying next"
                        )
                        cap.release()
                        cap = None
                        continue

                    self.camera = cap
                    _log(f"✅ Camera ready: index={idx}, backend={backend_name}, shape={frame.shape}")
                    return True
                except Exception as e:
                    _log(f"⚠️ Camera index {idx} ({backend_name}): {e}")
                    if cap is not None:
                        try:
                            cap.release()
                        except Exception:
                            pass

        # If we got here, no hardware camera worked. 
        # For development/demo purposes, we can fallback to a virtual camera if the user didn't explicitly forbid it.
        if os.getenv("SAFETY_ALLOW_VIRTUAL_FALLBACK", "1") == "1":
            _log("⚠️ No hardware camera found. Falling back to VIRTUAL CAMERA for demo.")
            self.camera = "VIRTUAL"
            return True

        self.last_error = (
            "Could not open a working camera. Tried indices "
            + ", ".join(str(i) for i in indices)
            + ". On Windows: allow Camera access in Settings → Privacy → Camera; close Zoom/Teams "
            "using the device; try SAFETY_CAMERA_INDEX=1 or SAFETY_CAMERA_TRY_ALL=1. "
            "WSL/remote servers usually have no webcam unless configured."
        )
        _log(f"❌ {self.last_error}")
        return False

    def start(self):
        """Start multi-agent detection system"""
        if self.running:
            _log("⚠️ Detection already running")
            return False
        
        try:
            _log("🚀 Starting multi-agent detection service...")
            if not self.initialize_components():
                _log("❌ Component initialization failed, but continuing with camera...")
            
            _log("📹 Opening camera...")
            if not self._open_camera():
                return False
            
            self.running = True
            
            # Start isolated agent threads (The Multi-Agent Event Bus Architecture)
            self.threads = [
                threading.Thread(target=self._camera_agent, daemon=True, name="CameraAgent"),
                threading.Thread(target=self._perception_agent, daemon=True, name="PerceptionAgent"),
                threading.Thread(target=self._reasoning_agent, daemon=True, name="ReasoningAgent"),
                threading.Thread(target=self._action_agent, daemon=True, name="ActionAgent")
            ]
            
            for t in self.threads:
                t.start()
            
            _log("✅ Multi-Agent Detection service started")
            return True
        except Exception as e:
            self.last_error = f"Service start failed: {str(e)}"
            _log(f"❌ {self.last_error}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop(self):
        """Stop detection system. Safe to call multiple times (idempotent)."""
        if not self.running and self.camera is None:
            return True

        _log("[STOP] Stopping detection service...")
        self.running = False

        # Give threads a short moment to exit loops naturally
        time.sleep(0.5)

        threads = getattr(self, "threads", None) or []
        for t in threads:
            if t.is_alive():
                _log(f"[STOP] Joining {t.name}...")
                t.join(timeout=2.0)

        if self.camera:
            try:
                if hasattr(self.camera, "release"):
                    _log("[STOP] Releasing camera...")
                    self.camera.release()
            except Exception as e:
                _log(f"[WARN] Error releasing camera: {e}")
            self.camera = None

        with self.frame_lock:
            self.current_frame = None

        self.threads = []
        _log("[OK] Detection service stopped")
        return True
    
    def _camera_agent(self):
        """THREAD 1: Camera Agent - Reads frames natively without blocking AI"""
        _log("👁️ Camera Agent running")
        while self.running:
            if self.camera is None:
                break
            
            if self.camera == "VIRTUAL":
                # Generate a static-like noise frame for demo
                frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "VIRTUAL CAMERA FALLBACK", (150, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                ret = True
            else:
                ret, frame = self.camera.read()
            
            if not ret:
                time.sleep(0.1)
                continue
            
            with self.frame_lock:
                self.current_frame = frame.copy()
                
            try:
                self.frame_queue.put_nowait(frame.copy())
            except queue.Full:
                pass # Drop frame if perception is busy to avoid lag
                
            time.sleep(0.01)

    def _perception_agent(self):
        """THREAD 2: Perception Agent - Runs YOLO & MediaPipe independently"""
        _log("🧠 Perception Agent running")
        process_interval = 0.5
        last_process_time = 0
        
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1.0)
            except queue.Empty:
                continue
                
            current_time = time.time()
            if current_time - last_process_time < process_interval:
                continue
                
            last_process_time = current_time
            
            try:
                # 1. Object Detection
                persons_boxes = []
                threats_list = []
                if self.object_detector:
                    results = self.object_detector.detect(frame)
                    persons_list = self.object_detector.get_persons(results)
                    threats = self.object_detector.get_threats(results)
                    persons_boxes = [(int(p['bbox'][0]), int(p['bbox'][1]), int(p['bbox'][2]), int(p['bbox'][3])) for p in persons_list]
                    threats_list = [t['object'] for t in threats]
                
                self.persons_detected = len(persons_boxes)
                
                if len(persons_boxes) == 0 and len(threats_list) == 0:
                    self.current_threat_level = "LOW"
                    self.current_confidence = 0.0
                    self._broadcast_state_update()
                    continue
                
                # 2. Pose Analysis
                threat_score = 0.0
                distress_signals = []
                
                if self.pose_analyzer:
                    for person_box in persons_boxes:
                        # We pass the bbox to focus on the person, but we tell the analyzer it's cropped
                        pose_results = self.pose_analyzer.analyze(frame, person_box)
                        if pose_results and pose_results.pose_landmarks:
                            distress_data = self.pose_analyzer.detect_distress_signals(
                                pose_results.pose_landmarks.landmark, 
                                is_cropped=True
                            )
                            if distress_data:
                                if distress_data.get('distress_score', 0) > threat_score:
                                    threat_score = distress_data['distress_score']
                                distress_signals.extend(distress_data.get('signals', []))
                
                # Deduplicate signals
                distress_signals = list(set(distress_signals))
                
                # Bundle perception data
                perception_data = {
                    'frame': frame,
                    'persons_count': len(persons_boxes),
                    'person_boxes': persons_boxes,
                    'threats': threats_list,
                    'distress_score': threat_score,
                    'distress_signals': distress_signals
                }
                
                # Send to Reasoning Agent
                try:
                    self.perception_queue.put_nowait(perception_data)
                except queue.Full:
                    pass
                    
            except Exception as e:
                _log(f"❌ Perception Agent Error: {e}")
                
    def _reasoning_agent(self):
        """THREAD 3: Reasoning Agent - Analyzes perception data for threats"""
        _log("🤔 Reasoning Agent running")
        while self.running:
            try:
                data = self.perception_queue.get(timeout=1.0)
            except queue.Empty:
                continue
                
            try:
                if self.decision_maker:
                    decision = self.decision_maker.analyze(data)
                    self.current_confidence = float(decision["confidence"])
                    self.current_threat_level = decision["threat_level"]
                else:
                    # Safety fallback if decision maker is unavailable
                    distress_score = float(data.get('distress_score', 0.0))
                    threats = data.get('threats', [])
                    persons_count = int(data.get('persons_count', 0))
                    weapon_bonus = min(len(threats) * 35, 70)
                    crowd_risk_bonus = 10 if persons_count >= 4 else 0
                    raw_score = min(100.0, distress_score + weapon_bonus + crowd_risk_bonus)
                    self.recent_confidences.append(raw_score)
                    smoothed_score = sum(self.recent_confidences) / len(self.recent_confidences)
                    self.current_confidence = round(smoothed_score, 2)
                    if len(threats) > 0 and smoothed_score >= 90:
                        self.current_threat_level = "CRITICAL"
                    elif smoothed_score >= 80:
                        self.current_threat_level = "HIGH"
                    elif smoothed_score >= 50:
                        self.current_threat_level = "MEDIUM"
                    else:
                        self.current_threat_level = "LOW"
                    decision = {
                        "threat_detected": self.current_threat_level in ["MEDIUM", "HIGH", "CRITICAL"],
                        "threat_type": "fallback",
                        "threat_level": self.current_threat_level,
                        "confidence": self.current_confidence,
                        "action": "alert" if self.current_threat_level in ["HIGH", "CRITICAL"] else "log",
                        "summary": "fallback scoring",
                        "reason_codes": [],
                        "agent_scores": {},
                    }

                self._log_calibration_sample(data, decision)
                
                self._broadcast_state_update()
                
                # If critical, send directly to Action Agent
                if self.current_threat_level in ["HIGH", "CRITICAL"]:
                    action_payload = {
                        'threat_level': self.current_threat_level,
                        'confidence': self.current_confidence,
                        'pose_data': data['distress_signals'],
                        'reason_codes': decision.get("reason_codes", []) if self.decision_maker else [],
                        'agent_scores': decision.get("agent_scores", {}) if self.decision_maker else {},
                    }
                    try:
                        self.decision_queue.put_nowait(action_payload)
                    except queue.Full:
                        pass
                        
            except Exception as e:
                _log(f"❌ Reasoning Agent Error: {e}")

    def _action_agent(self):
        """THREAD 4: Action Agent - Performs independent API calls and logs"""
        _log("🚨 Action Agent running")
        while self.running:
            try:
                action_data = self.decision_queue.get(timeout=1.0)
            except queue.Empty:
                continue
                
            current_time = time.time()
            if current_time - self.last_alert_time < self.alert_cooldown:
                continue
                
            self.last_alert_time = current_time
            confidence = action_data['confidence']
            threat_level = action_data['threat_level']
            pose_data = action_data['pose_data']
            reason_codes = action_data.get("reason_codes", [])
            agent_scores = action_data.get("agent_scores", {})
            
            _log(f"🚨 ACTION: {threat_level} threat detected ({confidence:.1f}%)")
            
            alert_payload = {
                "threat_level": threat_level,
                "confidence": float(confidence),
                "description": f"{threat_level} threat detected",
                "pose_data": json.dumps({
                    "distress_signals": pose_data,
                    "reason_codes": reason_codes,
                    "agent_scores": agent_scores,
                }) if (pose_data or reason_codes or agent_scores) else None,
                "sms_sent": False,
                "sms_status": None,
            }
            
            # 1. SMS Alert API Call (Doesn't block video!)
            if self.sms_alert and float(confidence) >= 80:
                try:
                    sms_result = self.sms_alert.send_alert(
                        threat_type=threat_level,
                        confidence=round(float(confidence), 1),
                        location="Laptop Webcam",
                        details=f"Pose signals: {pose_data}" if pose_data else "No pose signals"
                    )
                    alert_payload["sms_sent"] = bool(sms_result)
                    alert_payload["sms_status"] = "sent" if sms_result else "failed"
                    _log(f"📱 SMS sent: {alert_payload['sms_status']}")
                except Exception as e:
                    _log(f"❌ SMS failed: {e}")
                    alert_payload["sms_status"] = f"failed: {str(e)}"
            
            # 2. Database API Call
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/api/alerts/create",
                    json=alert_payload,
                    timeout=5
                )
                if response.ok:
                    _log(f"✅ Alert sent to dashboard")
            except Exception as e:
                _log(f"❌ Failed to reach backend: {e}")

    def _broadcast_state_update(self):
        """Helper to safely broadcast status via WebSockets from background threads."""
        try:
            status_data = {
                "type": "status",
                "data": {
                    "current_threat_level": self.current_threat_level,
                    "current_confidence": self.current_confidence,
                    "persons_detected": self.persons_detected,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            }
            loop = getattr(self, "loop", None)
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(manager.broadcast(status_data), loop)
        except Exception:
            pass

    def _log_calibration_sample(self, perception_data, decision):
        """
        Persist anonymized samples for threshold calibration.
        No image bytes are stored.
        """
        try:
            now = time.time()
            # Prevent writing too many near-duplicate rows.
            if (now - self.last_calibration_log_time) < 1.0:
                return

            confidence = float(decision.get("confidence", 0.0))
            if confidence < 25 and int(perception_data.get("persons_count", 0)) == 0:
                return

            self.last_calibration_log_time = now
            sample = {
                "event_id": f"evt_{int(now * 1000)}",
                "timestamp": datetime.utcnow().isoformat(),
                "environment": os.getenv("SAFETY_ENV", "campus").lower(),
                "score": confidence,
                "threat_level": decision.get("threat_level", "LOW"),
                "threat_type": decision.get("threat_type", "none"),
                "persons_count": int(perception_data.get("persons_count", 0)),
                "threats_count": len(perception_data.get("threats", [])),
                "distress_score": float(perception_data.get("distress_score", 0.0)),
                "reason_codes": decision.get("reason_codes", []),
                "agent_scores": decision.get("agent_scores", {}),
                # Human reviewer should set this later (0/1).
                "label": None,
            }

            with open(self.calibration_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(sample) + "\n")
        except Exception:
            # Logging should never break live detection.
            pass

    def get_current_frame(self):
        """Get the current frame as JPEG for streaming"""
        with self.frame_lock:
            if self.current_frame is None:
                return None
            frame = self._draw_overlays(self.current_frame.copy())
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret: return None
            return buffer.tobytes()
            
    def _draw_overlays(self, frame):
        color = (0, 255, 0)
        if self.current_threat_level == "MEDIUM": color = (0, 255, 255)
        elif self.current_threat_level == "HIGH": color = (0, 165, 255)
        elif self.current_threat_level == "CRITICAL": color = (0, 0, 255)
        
        cv2.rectangle(frame, (0, 0), (640, 40), (0, 0, 0), -1)
        cv2.putText(frame, f"Threat: {self.current_threat_level}", (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Confidence: {self.current_confidence:.1f}%", (240, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Persons: {self.persons_detected}", (500, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return frame

detection_service = DetectionService()
