@echo off
echo Starting Time Tracker...
cd /d "%~dp0"
if exist "dist\TimeTracker.exe" (
    start "" "dist\TimeTracker.exe"
) else (
    echo TimeTracker.exe not found in dist folder!
    echo Please build the executable first using: python build.py
    pause
) 