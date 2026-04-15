@echo off
cd /d "%~dp0backend"
python -m pip install -r requirements.txt -q
echo Starting Sentinel AI backend at http://127.0.0.1:8000
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
