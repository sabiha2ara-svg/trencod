@echo off
cd /d "%~dp0"
title Trencod
if exist ".venv\Scripts\python.exe" goto packages
echo Setting up Trencod. First setup needs an internet connection.
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 -m venv .venv
) else (
  python -m venv .venv
)
if not exist ".venv\Scripts\python.exe" (
  echo.
  echo Python 3.10 or newer is needed. Tell ChatGPT the message shown above.
  pause
  exit /b 1
)
:packages
.venv\Scripts\python.exe -c "import flask, waitress" >nul 2>nul
if %errorlevel% neq 0 (
  echo Installing Trencod's web server packages...
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Setup failed. Check your internet connection and try again.
    pause
    exit /b 1
  )
)
echo Opening Trencod. Keep this window open while using the website.
.venv\Scripts\python.exe server.py
pause
