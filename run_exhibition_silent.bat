@echo off
REM Silent Exhibition Mode - No console window
REM Double-click this to launch without any visible windows (except projector)

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Launch with pythonw.exe (no console)
start /B pythonw.exe main.py

REM Exit batch file immediately (don't keep window open)
exit
