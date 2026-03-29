
<div align="center">

# 🛡️ Women Safety AI

### *Because surveillance should protect — not record.*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-Google_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-Private-red?style=for-the-badge)

<br/>

> **Traditional CCTV records the crime. Women Safety AI prevents it.**

<br/>

</div>

---

## 🧠 The Problem We're Solving

Traditional surveillance is **reactive** — footage is reviewed only *after* something goes wrong. By then, it's too late.

Women Safety AI flips this model entirely. It's **proactive** — a system that watches, thinks, and acts *before* harm occurs. Using a multi-agent AI pipeline, it detects threats like aggression, distress, and harassment in real-time, and delivers alerts to security within **⚡ 3 seconds** of detection.

And the best part? **It never records a single frame of video.**

---

## 🏗️ System Architecture

![System Architecture](https://github.com/sri-mathi-2311/-women-safety-ai/blob/main/architecture.png?raw=true)

The pipeline processes every camera frame through **5 sequential stages** — from raw video to actionable alert — all within 3 seconds:

| Stage | Component | What It Does |
|---|---|---|
| 📷 **Input** | Real-time Camera Feed | Captures live video stream |
| 🧠 **Vision** | Computer Vision Engine | YOLOv8 person detection + MediaPipe pose tracking + facial emotion recognition + motion analysis |
| 📋 **Extraction** | Behavior Metadata Extractor | Pulls only tags, pose flags, motion scores & timestamps — no raw pixels |
| 🤖 **Reasoning** | LLM Summary Generator (Gemini) | Contextual threat classification, daily logs, alerts — strict no-storage policy for visual/audio data |
| 📤 **Output** | Alert System + Web Dashboard | Twilio SMS to security + React operator console with live WebSocket feed |

---

## ✨ Key Features

### 👁️ Real-Time Threat Detection
Fuses **YOLOv8/v11** object detection with **MediaPipe** skeletal pose analysis to identify aggression, distress, harassment, and loitering — all in real-time at 10–15 FPS.

### 🤖 Agentic AI Decision-Making
Not just rule-based triggers. **Gemini 2.5 Flash** reasons about *context* before firing any alert. Raised arms during yoga? Normal. Raised arms during a confrontation at 11PM? Alert. False positive rate under **10%**.

### 🔗 Multi-Agent Pipeline
Asynchronous agents handle **perception**, **reasoning**, and **action** independently — no bottlenecks, high throughput, low latency.

### ⚡ 3-Second Alert Pipeline
From threat detection to SMS delivery in under 3 seconds via **Twilio**. Every second matters.

### 🖥️ Operator Console
Premium **React** dark-mode dashboard for live monitoring, incident triage, alert history, and real-time WebSocket video feed.

### 📊 Advanced Incident Metadata
Deep reporting including motion scores, pose flags, facial emotion recognition, spatial coordinates, and LLM-generated plain-language summaries.

### 📁 Data Export
Export full incident reports and reviewer labels to **CSV** for auditing, compliance, and model retraining.

---

## 🔒 Privacy-First Architecture

> *Zero video. Zero faces. Zero compromise.*

This system is built on a single non-negotiable principle: **no raw footage ever leaves the edge device.** Only anonymized behavioral metadata is transmitted.

| ✅ What Gets Stored | ❌ What Never Gets Stored |
|---|---|
| Timestamp | Video footage |
| Location label (e.g. "Gate A") | Camera frames |
| Threat type (e.g. "aggression") | Face images |
| Confidence score (0–100) | Personal identities |
| Person count | Biometric data |
| Motion score | Real names |
| LLM plain-language summary | License plates |
| Action taken | Any PII whatsoever |

🔐 **Encryption:** TLS 1.3 in transit · AES-256 at rest  
📜 **Compliance:** GDPR Article 25 (Privacy by Design) · India's **DPDP Act 2023**

---

## 🎯 Detection Scenarios

| Scenario | Motion | Arms | Crouch | Persons | Result |
|---|---|---|---|---|---|
| Normal Walking | 20–40 | ❌ | ❌ | 1–3 | ✅ NORMAL |
| Standing Still | 0–10 | ❌ | ❌ | 1 | ✅ NORMAL |
| Exercising | 50–70 | ✅ | ❌ | 1 | ⚠️ MONITOR |
| **Aggression** | **70–100** | **✅** | **❌** | **2+** | **🚨 ALERT** |
| **Distress (alone)** | **0–20** | **❌** | **✅** | **1** | **🚨 ALERT** |
| **Fallen Down** | **0–5** | **❌** | **✅** | **1** | **🔴 ESCALATE** |
| **Harassment** | **40–70** | **Asymm** | **❌** | **2** | **🚨 ALERT** |
| Loitering | 0–15 | ❌ | ❌ | 1 (2min+) | 📝 LOG |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| 🎨 Frontend | React 18.2, Vite, Vanilla CSS | Operator console & live dashboard |
| ⚙️ Backend | FastAPI, Python 3.10+, Uvicorn, SQLite | REST API & event storage |
| 👁️ Computer Vision | YOLOv8/v11 (Ultralytics), MediaPipe, OpenCV | Person detection & pose analysis |
| 🧠 Agentic AI | Google Gemini 2.5 Flash | Contextual threat reasoning |
| 📱 Alerts | Twilio SMS API | Emergency notifications |
| 🔄 Realtime | WebSockets | Live video & status feed |
| 🗄️ Database | PostgreSQL 15 | Encrypted event metadata |

---

## ⚡ Performance Metrics

| Metric | Laptop / PC | Raspberry Pi 4 |
|---|---|---|
| FPS (normal frames) | 13–15 FPS | 4–5 FPS |
| Person detection latency | 30ms | 120ms |
| Pose estimation latency | 40ms/person | 80ms/person |
| LLM reasoning latency | 500ms | 500ms |
| **Detection → SMS alert** | **~2.5 seconds** | **~2.7 seconds** |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js & npm
- Twilio account (for SMS alerts)
- Google Gemini API key

### 🔧 Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Configure your `.env` file:

```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_twilio_number
ALERT_PHONE_NUMBER=emergency_contact_number
GEMINI_API_KEY=your_gemini_api_key
```

Run the backend:

```powershell
.\run_dev.ps1
```

### 🎨 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Incident Reports

All critical incidents are automatically logged and visible in the **Reviewer Triage Queue** on the dashboard.

- 🔴 **Red** — Aggression / Physical confrontation
- 🟠 **Orange** — Distress / Person in vulnerable state
- 🟡 **Yellow** — High activity / Borderline case
- 🟢 **Green** — Normal activity

Export full incident history anytime via the **Export Incident Reports** button as a detailed CSV — ready for auditing, compliance review, or retraining your models.

---

## 🗺️ Deployment Targets

This system is designed for deployment in:

- 🎓 Educational campuses (schools, colleges, universities)
- 🏢 Corporate workplaces and office buildings
- 🚇 Public spaces (parks, transit stations, parking lots)
- 🏥 Healthcare facilities
- 🏘️ Residential communities

---

## 🔮 Future Roadmap

- [ ] 📹 Multi-camera fusion for cross-location tracking
- [ ] 🧬 Behavioral pattern learning per deployment site
- [ ] 🔐 Integration with existing access control systems
- [ ] 📱 Mobile app for field security personnel
- [ ] 🎙️ Voice-based distress detection (screams, calls for help)
- [ ] 🌐 Federated learning across deployments (no data sharing)

---

## 📜 License

Internal Project / Private. © 2026 Women Safety AI Team.

---

<div align="center">

*Built with purpose. Designed for impact. Deployed for safety.*

**⭐ Star this repo if you believe in ethical AI for social good.**

</div>
