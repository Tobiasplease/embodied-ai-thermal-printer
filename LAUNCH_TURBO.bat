@echo off
REM Duck Consciousness - Turbo Mode Launcher
REM Double-click this to launch with maximum performance

echo Starting Duck Consciousness in Turbo Mode...
echo.

REM Run the PowerShell script with execution policy bypass
powershell.exe -ExecutionPolicy Bypass -File "%~dp0launch_turbo.ps1"

echo.
pause
