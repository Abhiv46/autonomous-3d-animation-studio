@echo off
title The Naughty Duo - Autonomous Content Operations Engine
color 0b
echo ======================================================================
echo    THE NAUGHTY DUO - AUTONOMOUS CONTENT OPERATIONS CONTROL CENTER
echo ======================================================================
echo.
echo [*] Initializing Production Environment...
cd /d "C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine"

rem Start local dashboard in background
start "" /b python "apps\dashboard\control_center.py"

rem Run safe startup recovery sequence
python -u "scripts\safe_startup_runner.py"

pause
