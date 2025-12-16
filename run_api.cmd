@echo off
setlocal

cd /d "C:\Users\Arthur.Struik\Documents\RPIGui"
set "PY=C:\Users\Arthur.Struik\Documents\RPIGui\.venv\Scripts\python.exe"

REM sanity check (uses venv python)
"%PY%" -c "import sys; print(sys.executable)"

REM start API
"%PY%" -m uvicorn NucApi:app --host 0.0.0.0 --port 8000 --log-level info

endlocal
