"""
Creates a desktop shortcut for the exhibition launcher
Run this once to create "Duck Consciousness.lnk" on your desktop
"""
import os
import sys
import winshell
from win32com.client import Dispatch

def create_shortcut():
    """Create desktop shortcut for START_EXHIBITION.pyw"""

    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    launcher_path = os.path.join(script_dir, "START_EXHIBITION.pyw")
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, "Duck Consciousness.lnk")

    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = launcher_path
    shortcut.WorkingDirectory = script_dir
    shortcut.Description = "Duck Consciousness - Exhibition Installation"

    # Optional: Set icon (you can create a .ico file and set it here)
    # shortcut.IconLocation = os.path.join(script_dir, "duck_icon.ico")

    shortcut.save()

    print(f"[OK] Desktop shortcut created: {shortcut_path}")
    print("\nGallery staff can now double-click 'Duck Consciousness' on the desktop to start the installation.")
    print("\nThe installation will:")
    print("  - Start with NO console window")
    print("  - Open subtitle projector in FULLSCREEN automatically")
    print("  - Play background audio automatically")
    print("\nTo stop: Press ESC then Q in the projector window")

if __name__ == "__main__":
    try:
        create_shortcut()
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        print("\nAlternative: Right-click START_EXHIBITION.pyw -> Send to -> Desktop (create shortcut)")
        input("\nPress Enter to exit...")
