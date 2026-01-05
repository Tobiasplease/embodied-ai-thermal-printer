@echo off
echo ==========================================
echo DEBUG MODE - Audio Troubleshooting
echo ==========================================
echo.
echo This will show all projector output including
echo audio initialization messages.
echo.
echo Look for lines like:
echo   [AUDIO] Initializing audio system...
echo   [AUDIO OK] Playing: drone.wav
echo.
pause

cd /d "%~dp0"

REM Enable debug output
set DEBUG_PROJECTOR=1

REM Run main.py with output visible
python main.py

pause
