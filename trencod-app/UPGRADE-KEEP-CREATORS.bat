@echo off
cd /d "%~dp0"
echo Close your old Trencod server window first.
echo Select your OLD trencod-app folder in the window that opens.
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 upgrade.py
) else (
  python upgrade.py
)
pause
