# sms_alerts.py - SMS Alert System
import os
from twilio.rest import Client
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SMSAlertSystem:
    def __init__(self):
        # Twilio credentials
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.to_number = os.getenv('ALERT_PHONE_NUMBER')
        
        # Initialize Twilio client
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
            print("[OK] SMS Alert System initialized")
        else:
            self.client = None
            self.enabled = False
            print("[WARN] SMS disabled - Missing Twilio credentials")
    
    def send_alert(self, threat_type, confidence, location="Camera 1", details=None):
        """Send SMS alert for detected threat"""
        if not self.enabled:
            print(f"[SMS DISABLED] Would send: {threat_type}")
            return False
        
        try:
            # Short message for Trial account (under 160 chars)
            timestamp = datetime.now().strftime("%H:%M")
            message = f"ALERT: {threat_type} ({confidence}%) at {location}, {timestamp}. Take action!"
            
            # Send SMS
            sms = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            
            print(f"[OK] SMS Alert sent! SID: {sms.sid}")
            return True
            
        except Exception as e:
            print(f"[ERR] SMS failed: {e}")
            return False
    
    def test_alert(self):
        """Send a test SMS to verify setup"""
        return self.send_alert(
            threat_type="TEST",
            confidence=100,
            location="System",
            details="Test"
        )

# Quick test function
if __name__ == "__main__":
    print("Testing SMS Alert System...")
    sms = SMSAlertSystem()
    
    if sms.enabled:
        print("\nSending test SMS...")
        sms.test_alert()
    else:
        print("\n[WARN] Set up Twilio credentials first!")