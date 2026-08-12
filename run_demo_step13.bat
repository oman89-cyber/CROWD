@echo off
echo ======================================================================
echo CROWDSHIELD AI — STEP 13 LIVE DEMO
echo Live Crowd → Automatic Route Re-evaluation
echo ======================================================================
echo.
echo This demo shows the complete closed-loop system:
echo   Real Video → ML Detection → Zone Intelligence → Route Re-evaluation
echo.
echo Prerequisites:
echo   1. Backend running (uvicorn main:app --reload)
echo   2. Frontend running (npm run dev) [optional]
echo.
echo Demo Flow:
echo   1. Live video processing creates crowd intelligence
echo   2. Route monitoring detects high-risk zones
echo   3. Routes automatically recalculated when needed
echo   4. Frontend shows route updates
echo.
pause
echo.
echo Starting Live Pipeline with Demo Mode...
echo.
backend\.venv\Scripts\python.exe -m ml.live_pipeline --fps 2 --display