"""
Fullscreen Subtitle Projector
Displays subtitles on a black background for projector output
Runs as a separate process for stability
Supports optional background audio loop
"""

import tkinter as tk
from tkinter import font
import socket
import threading
import time
import json
import subprocess
import sys
import os

# Try to import pygame for audio (optional)
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[WARN] pygame not installed - background audio disabled")

class SubtitleProjector:
    """Subtitle display window (runs in separate process)"""
    def __init__(self, port=9998, audio_file=None, audio_volume=0.3, start_fullscreen=False):
        self.root = tk.Tk()
        self.root.title("Duck Consciousness - Subtitle Projector")

        # Set window size (not fullscreen by default to avoid flashing)
        self.root.geometry("1024x768")
        self.root.configure(background='black')

        # Track fullscreen state
        self.is_fullscreen = False

        # Check if we should start in fullscreen (exhibition mode)
        if start_fullscreen or os.environ.get('EXHIBITION_MODE') == '1':
            # Schedule fullscreen activation after window is fully initialized
            self.root.after(100, lambda: self.root.attributes('-fullscreen', True))
            self.is_fullscreen = True

        # Track mirror state for back-projection
        self.is_mirrored = False

        # Audio playback
        self.audio_file = audio_file
        self.audio_volume = audio_volume
        self.audio_playing = False

        # Delay audio initialization until after window is ready
        if audio_file and PYGAME_AVAILABLE:
            self.root.after(500, self._init_audio)

        # Keyboard controls - properly toggle fullscreen
        self.root.bind('<Escape>', self.exit_fullscreen_or_quit)
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('m', self.toggle_mirror)
        self.root.bind('M', self.toggle_mirror)
        self.root.bind('q', lambda e: self.quit_projector())
        self.root.bind('Q', lambda e: self.quit_projector())
        self.root.bind('<Control-q>', lambda e: self.quit_projector())

        # Audio controls (bind to multiple key variants)
        if self.audio_file:
            self.root.bind('a', self.toggle_audio)
            self.root.bind('A', self.toggle_audio)
            # Volume controls - bind both +/= and - keys
            self.root.bind('+', lambda e: self.adjust_volume(0.1))
            self.root.bind('=', lambda e: self.adjust_volume(0.1))  # + without shift
            self.root.bind('-', lambda e: self.adjust_volume(-0.1))
            self.root.bind('_', lambda e: self.adjust_volume(-0.1))  # - with shift
            # Arrow keys for volume (more intuitive)
            self.root.bind('<Up>', lambda e: self.adjust_volume(0.1))
            self.root.bind('<Down>', lambda e: self.adjust_volume(-0.1))

        # Create container frame for mirroring support
        self.container = tk.Frame(self.root, bg='black')
        self.container.pack(expand=True, fill='both')

        # Create subtitle label - MUCH smaller, not bold
        self.subtitle_font = font.Font(family='Arial', size=16, weight='normal')
        self.subtitle_label = tk.Label(
            self.container,
            text="Loading duck consciousness...",  # Show loading message immediately
            font=self.subtitle_font,
            fg='yellow',
            bg='black',
            wraplength=1800,  # Wider wrap with margins
            justify='center',
            height=2,  # Maximum 2 lines
            padx=100,  # Add horizontal padding to prevent edge cropping
            pady=20    # Add vertical padding
        )
        self.subtitle_label.pack(expand=True, padx=50, pady=50)  # Extra margins

        # Store current text for mirror updates
        self.current_text = "Loading duck consciousness..."

        # Clear loading message after 3 seconds
        self.root.after(3000, lambda: self._update_subtitle(""))

        # Socket server for receiving subtitles
        self.port = port
        self.server_socket = None
        self.running = True

        # Start socket server in background
        self.start_socket_server()

        # Update loop
        self.root.after(100, self.check_alive)

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen state"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        return "break"  # Prevent event propagation

    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)
        return "break"  # Prevent event propagation

    def exit_fullscreen_or_quit(self, event=None):
        """Exit fullscreen if fullscreen, otherwise quit"""
        if self.is_fullscreen:
            return self.exit_fullscreen(event)
        else:
            return self.quit_projector()

    def quit_projector(self):
        """Cleanly quit the projector"""
        self.running = False
        self.root.quit()
        return "break"

    def toggle_mirror(self, event=None):
        """Toggle horizontal mirroring for back-projection

        Note: True pixel-perfect mirroring in Tkinter requires platform-specific hacks
        or canvas rendering. For now, we use a simple RTL layout simulation.
        For production back-projection, consider using OBS with mirror filter.
        """
        self.is_mirrored = not self.is_mirrored

        # Simple approach: use Canvas to render flipped text
        # This requires destroying and recreating the widget
        self.subtitle_label.pack_forget()

        if self.is_mirrored and not hasattr(self, 'canvas'):
            # Switch to canvas-based rendering for true mirroring
            self.canvas = tk.Canvas(self.container, bg='black', highlightthickness=0)
            self.canvas.pack(expand=True, fill='both')
            # Create text item (will be flipped via negative scale)
            self.text_id = self.canvas.create_text(
                0, 0,  # Will be positioned dynamically
                text=self.current_text,
                fill='yellow',
                font=self.subtitle_font,
                width=1800,
                justify='center'
            )
        elif not self.is_mirrored and hasattr(self, 'canvas'):
            # Switch back to label-based rendering
            self.canvas.pack_forget()
            self.canvas.destroy()
            delattr(self, 'canvas')
            delattr(self, 'text_id')
            self.subtitle_label.pack(expand=True, padx=50, pady=50)
            self.subtitle_label.config(text=self.current_text)

        # Update canvas if in mirrored mode
        if hasattr(self, 'canvas'):
            self._update_canvas_mirror()

        mode = "MIRRORED (Canvas)" if self.is_mirrored else "NORMAL (Label)"
        print(f"[DISPLAY] Display mode: {mode} (press M to toggle)")
        return "break"

    def _init_audio(self):
        """Initialize pygame mixer and load audio file"""
        # Write to log file for debugging (since subprocess stdout may be hidden)
        log_file = os.path.join(os.path.dirname(__file__), "audio_debug.log")

        def log(msg):
            print(msg)
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    f.write(f"[{timestamp}] {msg}\n")
                    f.flush()
            except:
                pass

        try:
            log("[AUDIO] === Initializing audio system ===")
            log(f"[AUDIO] PYGAME_AVAILABLE = {PYGAME_AVAILABLE}")
            log(f"[AUDIO] audio_file = {self.audio_file}")
            log(f"[AUDIO] audio_volume = {self.audio_volume}")

            if not os.path.exists(self.audio_file):
                log(f"[AUDIO ERROR] File not found: {self.audio_file}")
                return

            log(f"[AUDIO] File exists (size: {os.path.getsize(self.audio_file)} bytes)")

            # Initialize pygame mixer
            log(f"[AUDIO] Initializing pygame mixer...")
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            log(f"[AUDIO] Mixer initialized: {pygame.mixer.get_init()}")

            log(f"[AUDIO] Loading audio file...")
            pygame.mixer.music.load(self.audio_file)
            log(f"[AUDIO] Audio file loaded successfully")

            log(f"[AUDIO] Setting volume to {self.audio_volume:.0%}...")
            pygame.mixer.music.set_volume(self.audio_volume)

            # Start playing on loop (-1 = infinite loop)
            log(f"[AUDIO] Starting playback (infinite loop, 2s fade-in)...")
            pygame.mixer.music.play(loops=-1, fade_ms=2000)  # 2s fade-in
            self.audio_playing = True

            log(f"[AUDIO OK] Playing: {os.path.basename(self.audio_file)} (volume: {self.audio_volume:.0%})")
            log("[AUDIO] Controls: A=toggle, Up/Down arrows=volume, +/-=volume")

            # Check if it's actually playing
            if pygame.mixer.music.get_busy():
                log("[AUDIO] Playback confirmed ACTIVE")
            else:
                log("[AUDIO WARNING] Playback started but mixer reports NOT BUSY")

        except Exception as e:
            log(f"[AUDIO ERROR] Failed to initialize: {e}")
            import traceback
            log(traceback.format_exc())
            self.audio_playing = False

    def toggle_audio(self, event=None):
        """Toggle audio playback on/off"""
        if not PYGAME_AVAILABLE or not self.audio_file:
            return "break"

        try:
            if self.audio_playing:
                pygame.mixer.music.fadeout(1000)  # 1s fade-out
                self.audio_playing = False
                print("[AUDIO] Muted (fading out)")
            else:
                pygame.mixer.music.play(loops=-1, fade_ms=1000)  # 1s fade-in
                self.audio_playing = True
                print("[AUDIO] Playing (fading in)")
        except Exception as e:
            print(f"[AUDIO] Toggle error: {e}")

        return "break"

    def adjust_volume(self, delta):
        """Adjust volume by delta (+/- 0.1)"""
        if not PYGAME_AVAILABLE or not self.audio_file:
            return "break"

        try:
            self.audio_volume = max(0.0, min(1.0, self.audio_volume + delta))
            pygame.mixer.music.set_volume(self.audio_volume)
            print(f"[AUDIO] Volume: {self.audio_volume:.0%}")
        except Exception as e:
            print(f"[AUDIO] Volume adjust error: {e}")

        return "break"

    def _update_subtitle(self, text):
        """Update subtitle text (handles both label and canvas modes)"""
        self.current_text = text

        if hasattr(self, 'canvas'):
            # Canvas mode (mirrored)
            self._update_canvas_mirror()
        else:
            # Label mode (normal)
            self.subtitle_label.config(text=text)

    def _update_canvas_mirror(self):
        """Update canvas with mirrored text"""
        if not hasattr(self, 'canvas'):
            return

        # Update canvas size
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        # Position text at center, then apply scale transformation
        self.canvas.coords(self.text_id, w//2, h//2)

        # Apply horizontal flip via scale
        # Note: Tkinter Canvas doesn't support transforms directly
        # We need to use platform-specific or PIL-based rendering
        # For now, just reverse the text as a workaround
        if self.current_text:
            # Split into words, reverse each word, reverse order
            words = self.current_text.split()
            mirrored = ' '.join(word[::-1] for word in reversed(words))
            self.canvas.itemconfig(self.text_id, text=mirrored)

    def start_socket_server(self):
        """Start socket server to receive subtitle updates"""
        def server_thread():
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind(('localhost', self.port))
                self.server_socket.listen(10)  # Allow multiple pending connections
                self.server_socket.settimeout(0.5)  # Shorter timeout for faster response

                while self.running:
                    try:
                        conn, addr = self.server_socket.accept()
                        conn.settimeout(0.5)

                        # Read all data (handle multi-part messages)
                        data = b''
                        while True:
                            try:
                                chunk = conn.recv(4096)
                                if not chunk:
                                    break
                                data += chunk
                                # If we have a complete JSON message, process it
                                if b'}' in chunk:
                                    break
                            except socket.timeout:
                                break

                        if data:
                            try:
                                message = json.loads(data.decode('utf-8'))
                                if message.get('action') == 'display':
                                    text = message.get('text', '')
                                    # Update GUI from socket thread (thread-safe with after)
                                    self.root.after(0, lambda t=text: self._update_subtitle(t))
                                elif message.get('action') == 'clear':
                                    self.root.after(0, lambda: self._update_subtitle(''))
                            except json.JSONDecodeError as e:
                                print(f"JSON decode error: {e}")
                        conn.close()
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.running:
                            print(f"Socket error: {e}")
            except Exception as e:
                print(f"Socket server error: {e}")

        thread = threading.Thread(target=server_thread, daemon=True)
        thread.start()

    def check_alive(self):
        """Keep window responsive"""
        if self.running:
            self.root.after(100, self.check_alive)

    def run(self):
        """Start the GUI main loop"""
        try:
            self.root.mainloop()
        finally:
            self.running = False
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass


class SubtitleProjectorClient:
    """Client interface for sending subtitles from main.py"""
    def __init__(self, port=9998, audio_file=None, audio_volume=0.3, start_fullscreen=False):
        self.port = port
        self.process = None

        # Launch projector as subprocess WITHOUT console window
        try:
            # Use regular python.exe (keep using venv if active)
            python_exe = sys.executable

            # Launch subprocess with hidden console (works better than pythonw.exe)
            startupinfo = None
            creationflags = 0

            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                # Use CREATE_NO_WINDOW flag (more reliable than pythonw.exe)
                creationflags = subprocess.CREATE_NO_WINDOW

            # Build command with audio parameters
            cmd = [python_exe, __file__, '--server', str(port)]
            if audio_file:
                cmd.extend(['--audio', audio_file])
                cmd.extend(['--volume', str(audio_volume)])
            if start_fullscreen:
                cmd.append('--fullscreen')

            # Check if we should show debug output (useful for troubleshooting)
            # Set environment variable DEBUG_PROJECTOR=1 to see output
            show_debug = os.environ.get('DEBUG_PROJECTOR') == '1'

            if show_debug:
                # Show output for debugging (no CREATE_NO_WINDOW so console appears)
                self.process = subprocess.Popen(
                    cmd,
                    startupinfo=startupinfo
                )
            else:
                # Hide output AND console for clean exhibition mode
                self.process = subprocess.Popen(
                    cmd,
                    startupinfo=startupinfo,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags
                )
            # Give it time to start
            time.sleep(1.5)
        except Exception as e:
            print(f"Failed to launch projector subprocess: {e}")
            self.process = None

    def _send_command(self, command):
        """Send command to projector via socket"""
        if not self.process:
            return

        max_retries = 3
        for attempt in range(max_retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect(('localhost', self.port))
                sock.sendall(json.dumps(command).encode('utf-8'))
                sock.close()
                return  # Success
            except Exception as e:
                if attempt == max_retries - 1:
                    # Only print error on final attempt
                    print(f"⚠️ Projector socket error: {e}")
                time.sleep(0.05)  # Brief delay before retry

    def display(self, text):
        """Display subtitle text"""
        self._send_command({'action': 'display', 'text': text})

    def clear(self):
        """Clear subtitle"""
        self._send_command({'action': 'clear'})

    def __del__(self):
        """Clean up subprocess on exit"""
        if self.process:
            try:
                self.process.terminate()
            except:
                pass


# Server mode - run projector window
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        # Server mode - display window
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--server', action='store_true')
        parser.add_argument('port', type=int, nargs='?', default=9998)
        parser.add_argument('--audio', type=str, default=None, help='Path to audio file for ambient background')
        parser.add_argument('--volume', type=float, default=0.3, help='Audio volume (0.0-1.0)')
        parser.add_argument('--fullscreen', action='store_true', help='Start in fullscreen mode')
        args = parser.parse_args()

        # Log startup info to file for debugging
        log_file = os.path.join(os.path.dirname(__file__), "projector_startup.log")
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                from datetime import datetime
                f.write(f"=== Subtitle Projector Startup {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.write(f"Port: {args.port}\n")
                f.write(f"Audio file: {args.audio}\n")
                f.write(f"Audio volume: {args.volume}\n")
                f.write(f"Fullscreen: {args.fullscreen}\n")
                f.write(f"sys.executable: {sys.executable}\n")
                f.write(f"PYGAME_AVAILABLE: {PYGAME_AVAILABLE}\n")
        except Exception as e:
            pass

        print(f"Starting Subtitle Projector window (port {args.port})...")
        if args.fullscreen:
            print("Exhibition mode: Starting in fullscreen")
        else:
            print("Press F11 for fullscreen, ESC to exit fullscreen, M to mirror, Q to quit")
        if args.audio:
            print(f"Background audio: {args.audio} (volume: {args.volume:.0%})")
            print("Press A to toggle audio, +/- to adjust volume")

        projector = SubtitleProjector(
            port=args.port,
            audio_file=args.audio,
            audio_volume=args.volume,
            start_fullscreen=args.fullscreen
        )
        projector.run()
    else:
        # Test mode - launch as client
        print("Starting Subtitle Projector (Test Mode)...")
        print("This will launch a separate window process")
        print()

        client = SubtitleProjectorClient()

        # Demo subtitles
        time.sleep(2)
        client.display("I see a person standing in front of me")
        time.sleep(3)
        client.display("The room feels quiet and still")
        time.sleep(3)
        client.display("I wonder what they're thinking about")
        time.sleep(3)
        client.clear()

        print("\nDemo complete. Press Enter to exit...")
        input()
