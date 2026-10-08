@echo off
echo Starting Apex RiskEngine Application on http://localhost:8000 ...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
