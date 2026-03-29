# pose_analysis.py - MediaPipe Pose Analysis for Distress Detection
import os
import warnings

# Suppress distracting Protobuf and MediaPipe C++ warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['GLOG_minloglevel'] = '2'

import mediapipe as mp
import cv2
import numpy as np
from datetime import datetime

class PoseAnalyzer:
    def __init__(self):
        """Initialize MediaPipe Pose"""
        print("[...] Loading MediaPipe Pose...")
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        print("[OK] MediaPipe Pose loaded")
        
    def analyze(self, frame, person_bbox=None):
        """Analyze pose in frame"""
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # If person bbox provided, crop to that region
        if person_bbox is not None:
            x1, y1, x2, y2 = map(int, person_bbox)
            cropped = rgb_frame[y1:y2, x1:x2]
            results = self.pose.process(cropped)
        else:
            results = self.pose.process(rgb_frame)
        
        return results
    
    def detect_distress_signals(self, landmarks, is_cropped=False):
        """Analyze pose for distress indicators"""
        if not landmarks:
            return None
        
        distress_score = 0
        signals = []
        
        # Get key landmarks
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
        
        # 1. Hands raised above head (defensive/surrender pose)
        if left_wrist.y < nose.y and right_wrist.y < nose.y:
            distress_score += 30
            signals.append("Hands raised above head")
        
        # 2. Hands covering face/head (protective pose)
        if (abs(left_wrist.x - nose.x) < 0.1 and abs(left_wrist.y - nose.y) < 0.15) or \
           (abs(right_wrist.x - nose.x) < 0.1 and abs(right_wrist.y - nose.y) < 0.15):
            distress_score += 40
            signals.append("Hands near face (protective)")
        
        # 3. Crouching/hunched posture (fear response)
        # Only valid if we're looking at the full frame, or if we have a very loose crop.
        if not is_cropped:
            shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2
            if shoulder_midpoint_y > 0.65:  # Shoulders significantly low in frame
                distress_score += 25
                signals.append("Crouched posture")
        
        # 4. Asymmetric arm position (struggling/resisting)
        arm_asymmetry = abs(left_wrist.y - right_wrist.y)
        if arm_asymmetry > 0.35:
            distress_score += 20
            signals.append("Asymmetric arm position")
        
        return {
            'distress_score': min(distress_score, 100),
            'signals': signals,
            'is_distressed': distress_score >= 50
        }
    
    def draw_pose(self, frame, results):
        """Draw pose landmarks on frame"""
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
        return frame

# Test function
if __name__ == "__main__":
    print("Testing Pose Analysis...")
    analyzer = PoseAnalyzer()
    
    cap = cv2.VideoCapture(0)
    print("Testing pose detection (Press 'q' to quit)")
    print("Try these poses to test distress detection:")
    print("  - Raise hands above head")
    print("  - Cover your face with hands")
    print("  - Crouch down")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Analyze pose
        results = analyzer.analyze(frame)
        
        # Detect distress
        if results.pose_landmarks:
            distress = analyzer.detect_distress_signals(results.pose_landmarks.landmark)
            
            # Draw pose
            frame = analyzer.draw_pose(frame, results)
            
            # Display distress info
            if distress:
                color = (0, 0, 255) if distress['is_distressed'] else (0, 255, 0)
                cv2.putText(frame, f"Distress Score: {distress['distress_score']}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                y_offset = 60
                for signal in distress['signals']:
                    cv2.putText(frame, f"• {signal}", (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    y_offset += 25
                
                if distress['is_distressed']:
                    cv2.putText(frame, "🚨 DISTRESS DETECTED!", (10, frame.shape[0] - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
        cv2.imshow('Pose Analysis Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()