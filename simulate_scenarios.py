import csv
import time
from datetime import datetime
import json
import os
import requests
import sys

# Add the project root to sys path so we can import internal modules
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from sms_alerts import SMSAlertSystem

# Simulating deep MediaPipe skeleton data, facial emotion analysis, and Agent summaries
scenarios = [
    {
        "threat_level": "CRITICAL",
        "confidence": 98.7,
        "location": "Campus Stairwell B",
        "description": "Critical Incident: Physical assault detected.",
        "pose_data": {
            "distress_signals": ["violent_struggle", "pinned_against_wall", "hands_raised_defense"],
            "reason_codes": ["abnormal_proximity", "forceful_contact", "distress_pose_detected"],
            "agent_scores": {"pose_agent": 98, "proximity_agent": 99, "emotion_agent": 95},
            "mediapipe_skel_data": {
                "aggressor_male": {
                    "bounding_box": [120, 45, 230, 310],
                    "posture": "leaning_forward_aggressively",
                    "left_wrist": {"x": 0.45, "y": 0.60, "z": -0.12},
                    "right_wrist": {"x": 0.52, "y": 0.30, "z": -0.25},
                    "facial_emotion": "Angry / Aggressive"
                },
                "victim_female": {
                    "bounding_box": [140, 50, 200, 305],
                    "posture": "cornered_defensive",
                    "left_wrist": {"x": 0.48, "y": 0.25, "z": -0.05},
                    "right_wrist": {"x": 0.50, "y": 0.22, "z": -0.08},
                    "facial_emotion": "Fear / Extreme Distress"
                }
            },
            "agent_summarized_report": "Agent Analysis: The male subject has closed the distance aggressively (Proximity Alert: 0.05m). The female subject is pressed against a structural boundary. Facial analysis confirms high fear indexing on the female subject and hostile expressions on the male. The male's right arm (x: 0.52) is intersecting the female's personal bounding box rapidly. Immediate intervention is required."
        }
    },
    {
        "threat_level": "CRITICAL",
        "confidence": 95.2,
        "location": "Parking Lot Sector 4",
        "description": "Critical Incident: Unwanted physical restraint detected.",
        "pose_data": {
            "distress_signals": ["wrist_grab", "shoving", "attempted_escape_blocked"],
            "reason_codes": ["rapid_movement", "cornered_geometry", "asymmetric_posture"],
            "agent_scores": {"pose_agent": 94, "proximity_agent": 97, "emotion_agent": 92},
            "mediapipe_skel_data": {
                "aggressor_male": {
                    "bounding_box": [400, 150, 520, 410],
                    "posture": "blocking_path",
                    "left_wrist": {"x": 0.75, "y": 0.45, "z": -0.15},
                    "right_wrist": {"x": 0.80, "y": 0.50, "z": -0.10},
                    "facial_emotion": "Determined / Hostile"
                },
                "victim_female": {
                    "bounding_box": [450, 160, 510, 400],
                    "posture": "pulling_away",
                    "left_wrist": {"x": 0.75, "y": 0.45, "z": -0.05}, 
                    "right_wrist": {"x": 0.70, "y": 0.55, "z": -0.02},
                    "facial_emotion": "Panic / Anxiety"
                }
            },
            "agent_summarized_report": "Agent Analysis: The male subject's left wrist coordinates perfectly overlap the female subject's left wrist indicating a forceful grab/restraint. The female's skeleton center of gravity indicates pulling away/fleeing but velocity is 0 due to the restraint. Facial models indicate Panic. High likelihood of escalation."
        }
    },
    {
        "threat_level": "HIGH",
        "confidence": 88.0,
        "location": "Library 2nd Floor Quiet Zone",
        "description": "High Threat: Verbal escalating to physical intimidation.",
        "pose_data": {
            "distress_signals": ["looming_posture", "defensive_backing_away", "hands_covering_face"],
            "reason_codes": ["aggressive_approach", "sustained_tracking", "fear_response_pose"],
            "agent_scores": {"pose_agent": 89, "proximity_agent": 85, "emotion_agent": 90},
            "mediapipe_skel_data": {
                "aggressor_male": {
                    "bounding_box": [300, 100, 400, 380],
                    "posture": "looming_over_target",
                    "left_wrist": {"x": 0.55, "y": 0.70, "z": 0.10},
                    "right_wrist": {"x": 0.60, "y": 0.75, "z": 0.05},
                    "facial_emotion": "Angry / Shouting"
                },
                "victim_female": {
                    "bounding_box": [340, 150, 390, 320],
                    "posture": "cowering_seated",
                    "left_wrist": {"x": 0.52, "y": 0.40, "z": -0.20},
                    "right_wrist": {"x": 0.54, "y": 0.40, "z": -0.20},
                    "facial_emotion": "Shock / Fear"
                }
            },
            "agent_summarized_report": "Agent Analysis: Detected a seated female subject exhibiting a cowering posture with hands raised near the face. A male subject is standing and looming directly over her space. Distance is rapidly decreasing. Male facial analysis indicates shouting/anger, while the female exhibits shock. Tracking sustained harassment."
        }
    }
]

def run():
    print("Initializing SMS Alert System...")
    sms = SMSAlertSystem()
    csv_file = "detailed_incidents_log.csv"
    
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Threat Level", "Confidence", "Location", 
                "Description", "Male Emotion", "Female Emotion", 
                "Agent Summary", "Full JSON Payload", "SMS Status"
            ])
        
        for idx, scenario in enumerate(scenarios):
            print(f"\n--- Triggering Comprehensive Scenario {idx+1} ---")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pose_data = scenario["pose_data"]
            skel = pose_data["mediapipe_skel_data"]
            
            male_emotion = skel["aggressor_male"]["facial_emotion"]
            female_emotion = skel["victim_female"]["facial_emotion"]
            agent_summary = pose_data["agent_summarized_report"]
            
            sms_msg = f"{scenario['threat_level']} Alert! {scenario['location']}. Analysis: {agent_summary[:80]}..."
            
            # Send SMS
            sms_result = sms.send_alert(
                threat_type=scenario["threat_level"],
                confidence=scenario["confidence"],
                location=scenario["location"],
                details=sms_msg
            )
            
            sms_status = "Sent" if sms_result else "Failed/Disabled"
            
            # Write expansive CSV record
            writer.writerow([
                timestamp,
                scenario["threat_level"],
                scenario["confidence"],
                scenario["location"],
                scenario["description"],
                male_emotion,
                female_emotion,
                agent_summary,
                json.dumps(pose_data),
                sms_status
            ])
            
            # Send to backend dashboard
            try:
                # The dashboard uses JSON serialization to display the metadata column
                alert_payload = {
                    "threat_level": scenario["threat_level"],
                    "confidence": float(scenario["confidence"]),
                    "description": scenario["description"],
                    "pose_data": json.dumps(scenario["pose_data"]),
                    "sms_sent": bool(sms_result),
                    "sms_status": sms_status,
                }
                response = requests.post("http://127.0.0.1:8000/api/alerts/create", json=alert_payload)
                if response.ok:
                    print(f"Dashboard Updated. Male: {male_emotion} | Female: {female_emotion}")
            except Exception as e:
                print(f"Failed to update dashboard: {e}")
                
            time.sleep(2)  # Pause between scenarios

    print(f"\nAll comprehensive scenarios processed. Data appended to {os.path.abspath(csv_file)}")

if __name__ == '__main__':
    run()
