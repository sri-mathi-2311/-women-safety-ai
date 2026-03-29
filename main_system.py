# main_system.py - Women Safety AI - Ultra-Optimized Version
import cv2
import time
from object_detection import ObjectDetector
from pose_analysis import PoseAnalyzer
from sms_alerts import SMSAlertSystem
from agentic_decision import AgenticDecisionMaker
import threading

class WomenSafetyAI:
    def __init__(self):
        """Initialize all systems"""
        print("🚀 Initializing Women Safety AI System...")
        print("=" * 50)
        
        self.detector = ObjectDetector()
        self.pose_analyzer = PoseAnalyzer()
        self.sms = SMSAlertSystem()
        self.decision_maker = AgenticDecisionMaker(history_size=16)
        
        # Alert cooldown (seconds) - prevent spam
        self.alert_cooldown = 30
        self.last_alert_time = 0
        
        # Threat detection threshold
        self.threat_threshold = 80
        
        # Threading for async processing
        self.processing = False
        self.current_analysis = {
            'threat_detected': False,
            'threat_level': 'LOW',
            'situation': 'Initializing...',
            'action': 'Starting up',
            'confidence': 0
        }
        self.current_persons = []
        
        print("=" * 50)
        print("✅ All systems ready!")
    
    def process_frame_async(self, frame):
        """Process frame in background thread"""
        if self.processing:
            return  # Skip if already processing
        
        self.processing = True
        
        try:
            # 1. Detect persons and objects
            yolo_results = self.detector.detect(frame)
            persons = self.detector.get_persons(yolo_results)
            threats = self.detector.get_threats(yolo_results)
            
            # 2. Analyze pose ONLY if person detected
            distress_data = None
            if len(persons) > 0:
                person_bbox = persons[0]['bbox']
                pose_results = self.pose_analyzer.analyze(frame, person_bbox)
                
                if pose_results.pose_landmarks:
                    distress_data = self.pose_analyzer.detect_distress_signals(
                        pose_results.pose_landmarks.landmark
                    )
            
            # 3. Prepare detection data
            detection_data = {
                'frame': frame,
                'persons_count': len(persons),
                'person_boxes': [tuple(map(int, p['bbox'])) for p in persons],
                'distress_signals': distress_data['signals'] if distress_data else [],
                'distress_score': distress_data['distress_score'] if distress_data else 0,
                'threats': [t['object'] for t in threats]
            }
            
            # 4. Multi-agent decision fusion
            decision = self.decision_maker.analyze(detection_data)
            analysis = {
                'threat_detected': decision['threat_detected'],
                'threat_level': decision['threat_level'],
                'situation': decision['summary'],
                'action': decision['action'],
                'confidence': decision['confidence'],
            }
            
            # 5. Check if alert needed
            should_alert = (
                analysis['threat_detected'] and 
                analysis['confidence'] >= self.threat_threshold and
                (time.time() - self.last_alert_time) > self.alert_cooldown
            )
            
            if should_alert:
                self._send_alert(analysis)
                self.last_alert_time = time.time()
            
            # Update shared state
            self.current_analysis = analysis
            self.current_persons = persons
            
        finally:
            self.processing = False
    
    def _send_alert(self, analysis):
        """Send SMS alert in background"""
        def send():
            self.sms.send_alert(
                threat_type=analysis['threat_level'],
                confidence=analysis['confidence'],
                location="Camera 1",
                details=analysis['situation']
            )
            print(f"\n🚨 ALERT SENT: {analysis['situation']}")
        
        # Send in background thread
        threading.Thread(target=send, daemon=True).start()
    
    def _draw_ui(self, frame):
        """Draw UI elements on frame"""
        h, w = frame.shape[:2]
        
        # Draw person boxes
        for person in self.current_persons:
            x1, y1, x2, y2 = map(int, person['bbox'])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Status panel background
        cv2.rectangle(frame, (10, 10), (350, 150), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (350, 150), (255, 255, 255), 2)
        
        # System info
        y_pos = 35
        cv2.putText(frame, "Women Safety AI", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        y_pos += 30
        cv2.putText(frame, f"Persons: {len(self.current_persons)}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        y_pos += 25
        distress_score = self.current_analysis.get('confidence', 0)
        distress_color = (0, 0, 255) if distress_score >= 50 else (0, 255, 0)
        cv2.putText(frame, f"Threat: {distress_score}%", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, distress_color, 2)
        
        y_pos += 25
        threat_colors = {
            'LOW': (0, 255, 0),
            'MEDIUM': (0, 255, 255),
            'HIGH': (0, 165, 255),
            'CRITICAL': (0, 0, 255)
        }
        level = self.current_analysis.get('threat_level', 'LOW')
        color = threat_colors.get(level, (255, 255, 255))
        cv2.putText(frame, f"Level: {level}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Alert status
        if self.current_analysis.get('threat_detected', False):
            cv2.putText(frame, "THREAT DETECTED!", (20, h - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def run(self, source=0):
        """Run the system with maximum performance"""
        print(f"\n🎥 Starting video stream from source: {source}")
        print("Press 'q' to quit, 's' to take screenshot")
        
        cap = cv2.VideoCapture(source)
        
        # Maximum optimization settings
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer lag
        
        if not cap.isOpened():
            print("❌ Failed to open video source!")
            return
        
        print("✅ Video source opened successfully!")
        frame_count = 0
        last_process_time = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Process every 10th frame OR every 0.5 seconds (whichever is slower)
                current_time = time.time()
                if frame_count % 10 == 0 and (current_time - last_process_time) > 0.5:
                    # Start processing in background thread
                    threading.Thread(
                        target=self.process_frame_async, 
                        args=(frame.copy(),),
                        daemon=True
                    ).start()
                    last_process_time = current_time
                
                # Always draw UI (very fast)
                self._draw_ui(frame)
                
                # Show frame
                cv2.imshow('Women Safety AI System', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    filename = f"screenshot_{int(time.time())}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot saved: {filename}")
                
                frame_count += 1
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("\n✅ System shutdown complete")

# Main entry point
if __name__ == "__main__":
    system = WomenSafetyAI()
    system.run(source=0)