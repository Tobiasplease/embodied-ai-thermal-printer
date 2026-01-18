# Duck Consciousness Launcher with Turbo Mode
# Sets Windows power mode to "Best performance" then launches the brain

Write-Host "Setting power mode to Best Performance (Turbo)..." -ForegroundColor Cyan

# Set power mode to best performance using powercfg
# GUIDs: Balanced = 381b4222-f694-41f0-9685-ff5bb260df2e
#        High Performance = 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

Write-Host "Power mode set to High Performance" -ForegroundColor Green
Write-Host ""
Write-Host "Launching Duck Consciousness..." -ForegroundColor Yellow
Write-Host ""

# Get the script directory (where this .ps1 file is located)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change to that directory
Set-Location $scriptDir

# Set exhibition mode for fullscreen projector
$env:EXHIBITION_MODE = "1"

# Launch Python with the launcher
& ".venv\Scripts\python.exe" "launcher.py"

Write-Host ""
Write-Host "Duck stopped. Returning to balanced power mode..." -ForegroundColor Cyan
powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
Write-Host "Power mode restored to Balanced" -ForegroundColor Green
