"""
Duck Consciousness - Exhibition Launcher
Double-click this file to start the installation
- No console window
- Subtitle projector opens in fullscreen automatically
- Background audio plays automatically
"""
import subprocess
import sys
import os
import time

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the script directory
os.chdir(script_dir)

# Activate virtual environment if it exists
venv_python = os.path.join(script_dir, '.venv', 'Scripts', 'python.exe')
if os.path.exists(venv_python):
    python_exe = venv_python
else:
    # Use system python
    python_exe = sys.executable
    if python_exe.endswith('python.exe'):
        python_exe = python_exe.replace('python.exe', 'pythonw.exe')
    elif python_exe.endswith('pythonw.exe'):
        pass  # Already pythonw
    else:
        # Fallback
        python_exe = 'pythonw.exe'

# Path to main.py
main_script = os.path.join(script_dir, "main.py")

# Launch main.py with hidden console
if sys.platform == 'win32':
    # Windows - use STARTUPINFO to hide console
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    # Set environment variable to signal fullscreen mode
    env = os.environ.copy()
    env['EXHIBITION_MODE'] = '1'

    subprocess.Popen(
        [python_exe, main_script],
        startupinfo=startupinfo,
        cwd=script_dir,
        env=env
    )
else:
    # Unix-like systems
    subprocess.Popen(
        [python_exe, main_script],
        cwd=script_dir
    )
