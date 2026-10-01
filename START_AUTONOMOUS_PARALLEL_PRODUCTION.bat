@echo off
title The Naughty Duo - Autonomous Multi-Account Parallel Production Engine
color 0a
echo ======================================================================
echo    THE NAUGHTY DUO - AUTONOMOUS MULTI-ACCOUNT PARALLEL ENGINE (AUTO-MODE)
echo ======================================================================
echo.
echo [*] Working Directory: C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine
echo [*] Project Lock: 'The Naughty Duo' Enforced
echo [*] Character Lock: Pinki, Kaartik, Kaavya Enforced
echo [*] P0 Incomplete Recovery Engine: Active
echo.
cd /d "C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine"

rem 1. Launch Control Center Dashboard on http://127.0.0.1:8088 if not already running
start "" /b python "apps\dashboard\control_center.py"

rem 2. Launch Autonomous Auto-Pilot Parallel Engine
python -u "scripts\autonomous_auto_runner.py"

pause
