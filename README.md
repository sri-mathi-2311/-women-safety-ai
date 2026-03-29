# Women Safety AI 🛡️

Women Safety AI is a real-time security platform combining YOLO, MediaPipe pose analysis, and a Multi-Agent reasoning engine to protect physical spaces. Critical threats instantly trigger automated SMS emergency alerts. Includes a FastAPI backend and a custom React operator console for live surveillance, triage, and metadata CSV export.

## 🚀 Key Features

- **Real-time Threat Detection:** Fuses YOLOv8/v11 object detection with MediaPipe skeletal pose analysis.
- **Multi-Agent Reasoning:** Asynchronous agents handle perception, reasoning, and action independently for high performance.
- **Emergency Alerts:** Automated SMS notifications via Twilio when confidence thresholds are met.
- **Operator Console:** Premium React-based dashboard for live monitoring and incident triage.
- **Advanced Metadata:** Deep incident reporting including facial emotion recognition and spatial coordinates.
- **Data Export:** Export detailed incident reports and reviewer labels to CSV for auditing and training.

## 🛠️ Technology Stack

- **Frontend:** React, Vite, Vanilla CSS (Modern Dark Mode UI)
- **Backend:** FastAPI, Python, Uvicorn, SQLite
- **AI/ML:** YOLO (Ultralytics), MediaPipe, OpenCV
- **Communication:** Twilio API (SMS Alerts), WebSockets (Real-time Video & Status)

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js & npm
- Twilio Account (for SMS alerts)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your `.env` file with Twilio credentials:
   ```env
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=your_twilio_number
   ALERT_PHONE_NUMBER=emergency_contact_number
   ```
4. Run the backend service:
   ```powershell
   .\run_dev.ps1
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## 📊 Incident Reports
The system automatically logs all critical incidents. You can view them in the **Reviewer Triage Queue** on the dashboard or export them via the **Export Incident Reports** button to a detailed CSV file.

## 📜 License
Internal Project / Private. (C) 2026 Women Safety AI Team.
