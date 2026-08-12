@echo off
REM CrowdShield AI - Live Pipeline Launcher
REM Usage: run_live_pipeline.bat [--fps 2] [--display]

backend\.venv\Scripts\python.exe -m ml.live_pipeline %*
