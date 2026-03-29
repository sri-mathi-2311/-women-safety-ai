# gemini_analyzer.py - Gemini AI Scene Analysis
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import cv2

load_dotenv()

class GeminiAnalyzer:
    def __init__(self):
        """Initialize Gemini AI"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️ No Gemini API key found")
            self.enabled = False
            return
        
        print("🔄 Initializing Gemini AI...")
        self.client = genai.Client(api_key=api_key)
        self.enabled = True
        print("✅ Gemini AI ready")
    
    def analyze_scene(self, frame, detection_data):
        """
        Analyze scene with Gemini AI
        
        detection_data should contain:
        - persons_count: int
        - distress_signals: list
        - distress_score: int
        - threats: list (detected weapons/objects)
        """
        if not self.enabled:
            return self._fallback_analysis(detection_data)
        
        try:
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            img_bytes = buffer.tobytes()
            
            # Create prompt
            prompt = f"""You are a women's safety AI system. Analyze this scene for potential threats.

Detection Data:
- Persons detected: {detection_data.get('persons_count', 0)}
- Distress signals: {', '.join(detection_data.get('distress_signals', [])) or 'None'}
- Distress score: {detection_data.get('distress_score', 0)}/100
- Threat objects: {', '.join(detection_data.get('threats', [])) or 'None'}

Analyze the image and data to determine:
1. Is there a genuine safety threat? (YES/NO)
2. Threat level (LOW/MEDIUM/HIGH/CRITICAL)
3. Brief description of the situation (max 30 words)
4. Recommended action (max 20 words)

Respond in this exact format:
THREAT: [YES/NO]
LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
SITUATION: [description]
ACTION: [recommendation]"""

            # Send to Gemini - CORRECT SYNTAX
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type='image/jpeg',
                                data=img_bytes
                            )
                        )
                    ]
                )
            )
            
            # Parse response
            return self._parse_response(response.text, detection_data)
            
        except Exception as e:
            # Silent fallback - don't spam console
            return self._fallback_analysis(detection_data)
    
    def _parse_response(self, text, detection_data):
        """Parse Gemini response"""
        lines = text.strip().split('\n')
        result = {
            'threat_detected': False,
            'threat_level': 'LOW',
            'situation': 'Unknown',
            'action': 'Monitor',
            'confidence': 0
        }
        
        for line in lines:
            if line.startswith('THREAT:'):
                result['threat_detected'] = 'YES' in line.upper()
            elif line.startswith('LEVEL:'):
                result['threat_level'] = line.split(':')[1].strip()
            elif line.startswith('SITUATION:'):
                result['situation'] = line.split(':', 1)[1].strip()
            elif line.startswith('ACTION:'):
                result['action'] = line.split(':', 1)[1].strip()
        
        # Calculate confidence based on distress score and AI decision
        if result['threat_detected']:
            result['confidence'] = min(50 + detection_data.get('distress_score', 0) // 2, 95)
        
        return result
    
    def _fallback_analysis(self, detection_data):
        """Rule-based fallback when Gemini unavailable"""
        distress_score = detection_data.get('distress_score', 0)
        threats = detection_data.get('threats', [])
        
        # Simple rule-based logic
        threat_detected = distress_score >= 50 or len(threats) > 0
        
        if len(threats) > 0:
            level = 'CRITICAL'
            situation = f"Weapon detected: {', '.join(threats)}"
            action = "Immediate intervention required"
        elif distress_score >= 70:
            level = 'HIGH'
            situation = f"Distress signals detected: {', '.join(detection_data.get('distress_signals', []))}"
            action = "Alert authorities"
        elif distress_score >= 50:
            level = 'MEDIUM'
            situation = "Possible distress behavior"
            action = "Continue monitoring closely"
        else:
            level = 'LOW'
            situation = "Normal activity"
            action = "Routine monitoring"
        
        return {
            'threat_detected': threat_detected,
            'threat_level': level,
            'situation': situation,
            'action': action,
            'confidence': distress_score
        }

# Test function
if __name__ == "__main__":
    print("Testing Gemini Analyzer...")
    analyzer = GeminiAnalyzer()
    
    # Test with dummy data
    test_data = {
        'persons_count': 2,
        'distress_signals': ['Hands raised above head', 'Crouched posture'],
        'distress_score': 65,
        'threats': []
    }
    
    # Test without image (fallback mode)
    print("\n📊 Testing fallback analysis...")
    result = analyzer._fallback_analysis(test_data)
    print(f"Threat: {result['threat_detected']}")
    print(f"Level: {result['threat_level']}")
    print(f"Situation: {result['situation']}")
    print(f"Action: {result['action']}")
    print(f"Confidence: {result['confidence']}%")
