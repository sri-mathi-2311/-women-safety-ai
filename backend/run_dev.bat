@echo off
cd /d "%~dp0"
..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 ^
  --reload-exclude "*.db" ^
  --reload-exclude "*.db-wal" ^
  --reload-exclude "*.db-shm" ^
  --reload-exclude "**/*.db" ^
  --reload-exclude "safety_dashboard.db" ^
  --reload-exclude "*.jsonl"
