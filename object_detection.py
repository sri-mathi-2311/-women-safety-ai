# object_detection.py - YOLO11/YOLOv8 Person & Object Detection
from ultralytics import YOLO
import cv2
import torch
import ultralytics.nn.tasks
import os

# Fix for PyTorch >= 2.6 unpickling security restrictions on older ultralytics versions
_original_load = torch.load
def safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = safe_load

class ObjectDetector:
    def __init__(self, model_path=None):
        """Initialize detector with YOLO11-first strategy."""
        requested_model = model_path or os.getenv("YOLO_MODEL", "yolo11n.pt")
        fallback_models = [requested_model, "yolo11n.pt"]
        if os.getenv("YOLO_ALLOW_V8_FALLBACK", "0") == "1":
            fallback_models.append("yolov8n.pt")

        self.model = None
        loaded_model_name = None
        for candidate in fallback_models:
            try:
                print(f"[...] Loading detector model: {candidate}")
                self.model = YOLO(candidate)
                loaded_model_name = candidate
                break
            except Exception:
                continue

        if self.model is None:
            raise RuntimeError(
                "Failed to load any YOLO model. Tried: " + ", ".join(fallback_models)
            )
        print(f"[OK] Detector ready using model: {loaded_model_name}")
        
        # Classes we care about for safety
        self.threat_objects = {
            'knife': 0.6,
            'scissors': 0.6,
            'gun': 0.7,  # May not be in COCO dataset
        }
        
    def detect(self, frame):
        """Run detection on a frame"""
        results = self.model(frame, conf=0.5, verbose=False)
        return results[0]
    
    def get_persons(self, results):
        persons = []
        for box in results.boxes:
            class_id = int(box.cls[0])
            if class_id == 0:
                persons.append({
                    'bbox': box.xyxy[0].cpu().numpy(),
                    'confidence': float(box.conf[0])
                })
        return persons

    def detect_persons(self, frame):
        results = self.detect(frame)
        persons = self.get_persons(results)
        boxes = []
        for person in persons:
            x1, y1, x2, y2 = person['bbox']
            boxes.append((int(x1), int(y1), int(x2), int(y2)))
        return boxes
    
    def get_threats(self, results):
        """Detect potential threat objects"""
        threats = []
        for box in results.boxes:
            class_name = results.names[int(box.cls[0])]
            if class_name in self.threat_objects:
                confidence = float(box.conf[0])
                if confidence >= self.threat_objects[class_name]:
                    threats.append({
                        'object': class_name,
                        'bbox': box.xyxy[0].cpu().numpy(),
                        'confidence': confidence
                    })
        return threats

# Test function
if __name__ == "__main__":
    print("Testing Object Detection...")
    detector = ObjectDetector()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect
        results = detector.detect(frame)
        persons = detector.get_persons(results)
        
        # Draw boxes
        annotated = results.plot()
        cv2.putText(annotated, f"Persons: {len(persons)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Object Detection Test', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
