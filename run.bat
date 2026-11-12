@echo off
title Simple Honeypot
cd /d "%~dp0"
python --version >nul 2>&1
if errorlevel 1 (
  echo Python was not found. Install Python 3.9+ and select "Add Python to PATH".
  pause
  exit /b 1
)
python honeypot.py
pause
