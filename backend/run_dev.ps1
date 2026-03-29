# Dev server with reload — excludes SQLite + logs so DB writes don't restart the process (and the camera).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = Join-Path (Resolve-Path "..").Path "venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

& $py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 `
  --reload-exclude "*.db" `
  --reload-exclude "*.db-wal" `
  --reload-exclude "*.db-shm" `
  --reload-exclude "**/*.db" `
  --reload-exclude "safety_dashboard.db" `
  --reload-exclude "*.jsonl"
