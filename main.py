"""
Embodied AI v2 - Clean Main Loop
================================

Simple integration of camera + personality + hand control with stable threading.
Avoids the threading pitfalls of the original machine.py system.

Key design principles:
1. Single main thread for camera loop
2. Hand control runs in separate process (not thread)
3. AI processing on intervals, not constant threads
4. Simple state file communication between components
5. Clean shutdown handling
"""
import cv2
import time
import signal
import sys
import io
import traceback
import threading
import textwrap
import queue
from datetime import datetime

# Fix Windows emoji encoding issues by forcing UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from camera import Camera
from personality import PersonalityAI
from hand_control_integration import HandControlInterface, personality_to_hand_emotion
from thermal_integration import create_thermal_printer
from config import (
    AI_PROCESS_INTERVAL, DEBUG_CAMERA, DEBUG_AI, DEBUG_MOTOR,
    VERBOSE_OUTPUT, CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, SHOW_CAMERA_PREVIEW,
    PREVIEW_WIDTH, PREVIEW_HEIGHT, THERMAL_PRINTER_ENABLED,
    VOICE_ENABLED, VOICE_ENGINE, VOICE_MODEL, VOICE_ALL_THOUGHTS, VOICE_INTERVAL,
    WINDOWS_TTS_RATE, WINDOWS_TTS_VOLUME, WINDOWS_TTS_GENDER,
    ESPEAK_VOICE, ESPEAK_SPEED, ESPEAK_PITCH,
    LIPSYNC_ENABLED, LIPSYNC_PORT, LIPSYNC_BAUD,
    LIGHTBULB_ENABLED, LIGHTBULB_PORT, LIGHTBULB_BAUD,
    SUBTITLE_PROJECTOR_ENABLED, SUBTITLE_PROJECTOR_FONT_SIZE, SUBTITLE_PROJECTOR_COLOR,
    OLLAMA_URL
)

# Import lip sync FIRST (optional) - direct audio version
if LIPSYNC_ENABLED:
    try:
        from lipsync_direct_audio import DirectAudioLipSync
    except ImportError as e:
        print(f"[WARN] Lip sync not available: {e}")
        LIPSYNC_ENABLED = False

# Import voice system (optional)
VOICE_AVAILABLE = False
if VOICE_ENABLED:
    try:
        if VOICE_ENGINE == "espeak" and LIPSYNC_ENABLED:
            # Use integrated eSpeak with lip sync
            from espeak_tts_with_lipsync import ESpeakWithLipSync as VoiceSystem
            VOICE_AVAILABLE = True
        elif VOICE_ENGINE == "espeak":
            from espeak_tts_simple import ESpeakTTS as VoiceSystem
            VOICE_AVAILABLE = True
        elif VOICE_ENGINE == "windows":
            from windows_tts import WindowsTTS as VoiceSystem
            VOICE_AVAILABLE = True
        else:  # piper
            from voice import VoiceSystem
            VOICE_AVAILABLE = True
    except ImportError as e:
        print(f"[WARN] Voice system not available: {e}")
        VOICE_AVAILABLE = False

# Import subtitle projector (optional)
PROJECTOR_AVAILABLE = False
if SUBTITLE_PROJECTOR_ENABLED:
    try:
        from subtitle_projector import SubtitleProjectorClient
        PROJECTOR_AVAILABLE = True
    except ImportError as e:
        print(f"[WARN] Subtitle projector not available: {e}")
        PROJECTOR_AVAILABLE = False

def clear_print_queue_preemptive():
    """Clear Windows print queue aggressively with admin elevation"""
    try:
        import subprocess
        import os
        import sys
        print("[TRASH] Aggressively clearing Windows print spooler...")
        
        # Create a batch file to run as admin
        batch_content = '''
@echo off
echo Stopping print spooler...
net stop spooler
echo Clearing spooler files...
del /q "C:\\Windows\\System32\\spool\\PRINTERS\\*.*" 2>nul
echo Starting print spooler...
net start spooler
echo Print spooler cleared successfully!
'''
        
        # Write batch file
        batch_path = os.path.join(os.getcwd(), "clear_spooler.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        # Run batch file with admin privileges using runas
        print("[LOCK] Running spooler clear with admin privileges...")
        try:
            # Method 1: Try to run with elevated privileges
            result = subprocess.run([
                'powershell', '-Command', 
                f'Start-Process -FilePath "{batch_path}" -Verb RunAs -Wait -WindowStyle Hidden'
            ], capture_output=True, timeout=15, text=True)
            
            if result.returncode == 0:
                print("[OK] Print spooler cleared with admin privileges")
            else:
                raise Exception("Admin elevation failed")
                
        except Exception:
            # Method 2: Fallback - try without elevation
            print("[WARN] Admin elevation failed, trying without privileges...")
            subprocess.run(['net', 'stop', 'spooler'], capture_output=True, shell=True)
            subprocess.run(['net', 'start', 'spooler'], capture_output=True, shell=True)
            print("[OK] Print spooler restarted (limited permissions)")
        
        # Clean up batch file
        try:
            os.remove(batch_path)
        except:
            pass
            
    except Exception as e:
        print(f"[WARN] Could not clear print queue: {e}")
        print("[LIGHT] Manual solution: Run as Administrator and execute:")
        print("   net stop spooler && del /q C:\\Windows\\System32\\spool\\PRINTERS\\*.* && net start spooler")

class UrgentReactionQueue:
    """Thread-safe queue for urgent reactions (person arrivals/departures)"""

    def __init__(self):
        self.queue = queue.Queue(maxsize=1)  # Only keep most urgent reaction
        self.lock = threading.Lock()

    def add_reaction(self, text, urgency, context=None):
        """Add reaction, replacing existing if more urgent"""
        with self.lock:
            try:
                # Try to get existing reaction
                existing = self.queue.get_nowait()
                # Put back the more urgent one
                if urgency > existing['urgency']:
                    self.queue.put({'text': text, 'urgency': urgency, 'context': context or {}})
                else:
                    self.queue.put(existing)  # Keep existing
            except queue.Empty:
                # No existing reaction - add this one
                self.queue.put({'text': text, 'urgency': urgency, 'context': context or {}})

    def get_if_urgent(self, threshold=0.6):
        """Get reaction if urgency >= threshold, otherwise leave in queue"""
        try:
            with self.lock:
                reaction = self.queue.get_nowait()
                if reaction['urgency'] >= threshold:
                    return reaction  # Remove from queue and return
                else:
                    self.queue.put(reaction)  # Put back - not urgent enough yet
                    return None
        except queue.Empty:
            return None

    def clear(self):
        """Clear all queued reactions"""
        with self.lock:
            try:
                while True:
                    self.queue.get_nowait()
            except queue.Empty:
                pass

class EmbodiedAI:
    """Main embodied AI system - clean single-threaded design"""
    
    def __init__(self):
        self.running = False
        self.camera = None
        self.personality = None
        self.hand_control = None
        self.thermal_printer = None
        self.voice_system = None
        self.lipsync = None
        self.subtitle_projector = None

        # Timing controls - avoid threading issues
        self.last_ai_process_time = 0
        self.last_motor_update_time = 0
        self.last_status_time = 0
        self.last_voice_time = 0  # Track last voice output
        self.ai_processing_lock = threading.Lock()  # Prevent concurrent AI processing

        # Dynamic pacing based on scene activity
        self.current_ai_interval = AI_PROCESS_INTERVAL
        self.last_face_position = None
        self.face_movement_detected = False
        
        # Frame processing
        self.frame_count = 0
        self.start_time = time.time()
        
        # Live captioning subtitle system (thread-safe)
        self.current_subtitle = ""
        self.subtitle_chunks = []
        self.chunk_ready_flags = []  # Track when each chunk's jaw has moved
        self.current_chunk_index = 0
        self.subtitle_start_time = 0
        self.chunk_display_duration = 0  # Dynamic duration per chunk
        self.last_chunk_change_time = 0
        self.recent_spoken_chunks = []  # Remember last few spoken chunks across captions
        self.subtitle_lock = threading.Lock()
        self.caption_version = 0  # Track caption changes to prevent old chunks from speaking
        self.pending_caption = None  # Queue next caption to start after current chunk finishes

        # URGENT REACTION QUEUE (thread-safe, for person arrivals/departures)
        self.urgent_reaction_queue = UrgentReactionQueue()
        self.last_urgent_reaction_time = 0  # Cooldown to prevent spamming

        # Silence period tracking
        self.in_silence_period = False
        self.silence_start_time = 0

        # Arm SIGINT/SIGTERM handling only after init completes to avoid stray signals during startup
        self.signals_armed = False
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        if VERBOSE_OUTPUT:
            print("[BOT] Embodied AI v2 initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        if not getattr(self, "signals_armed", False):
            return  # Ignore early signals during startup
        print(f"\n[STOP] Shutdown signal received ({signum}ö")
        self.shutdown()
        sys.exit(0)

    def _normalize_chunk_text(self, text):
        """Normalize chunk text for dedupe comparisons."""
        if not text:
            return ""
        return " ".join(text.strip().lower().split())

    def _remember_spoken_chunk(self, text):
        """Track spoken chunks to avoid repeating openings."""
        normalized = self._normalize_chunk_text(text)
        if not normalized:
            return
        self.recent_spoken_chunks.append(normalized)
        if len(self.recent_spoken_chunks) > 6:
            self.recent_spoken_chunks.pop(0)
    
    def initialize(self):
        """Initialize all components"""
        try:
            # FIRST: Pre-load vision model into VRAM for faster inference
            if VOICE_ENABLED:  # Only print if we have output enabled
                print("[AI] Pre-loading vision model into VRAM...")
            try:
                import requests
                from config import SINGLE_MODEL_MODE, SINGLE_MULTIMODAL_MODEL
                if SINGLE_MODEL_MODE:
                    # Warm up LLaVA and keep it in VRAM permanently (keep_alive=-1)
                    # This prevents 10+ second load times on each observation
                    requests.post(
                        f"{OLLAMA_URL}/api/generate",
                        json={
                            'model': SINGLE_MULTIMODAL_MODEL,
                            'prompt': 'warm up',
                            'keep_alive': -1  # Keep loaded forever
                        },
                        timeout=30
                    )
                    print(f"[OK] {SINGLE_MULTIMODAL_MODEL} locked in VRAM (4.4x faster)")
            except Exception as e:
                print(f"[WARN] Could not pre-load model: {e}")

            # SECOND: Clear any stuck print jobs before connecting printer
            clear_print_queue_preemptive()

            # State persistence now enabled - DO NOT delete personality_state.json
            
            # Skip Camera class initialization - we'll use direct cv2 access
            if DEBUG_CAMERA:
                print("[CAMERA] Will initialize camera directly in main loop...")
            self.camera = None  # Don't use Camera class to avoid threading issues
            
            # Initialize AI personality
            if DEBUG_AI:
                print("[AI] Initializing AI personality...")
            self.personality = PersonalityAI()

            # Initialize thermal printer for subtitle printing
            print("[PRINT] Initializing thermal printer...")
            self.thermal_printer = create_thermal_printer(enabled=THERMAL_PRINTER_ENABLED)
            self.thermal_printer.start()

            # Initialize lip sync FIRST (if needed for eSpeak)
            if LIPSYNC_ENABLED and VOICE_ENGINE == "espeak":
                try:
                    print("[LIPSYNC] Initializing direct audio lip sync...")
                    self.lipsync = DirectAudioLipSync(
                        port=LIPSYNC_PORT,
                        baud=LIPSYNC_BAUD,
                        enabled=True,
                        lightbulb_port=LIGHTBULB_PORT if LIGHTBULB_ENABLED else None,
                        lightbulb_baud=LIGHTBULB_BAUD if LIGHTBULB_ENABLED else 9600,
                        lightbulb_enabled=LIGHTBULB_ENABLED
                    )
                    print(f"[OK] Direct audio lip sync ready ({LIPSYNC_PORT})")
                    if LIGHTBULB_ENABLED:
                        print(f"[LIGHT] Lightbulb sync ready ({LIGHTBULB_PORT})")
                except Exception as e:
                    print(f"[WARN] Lip sync disabled: {e}")
                    self.lipsync = None
            else:
                self.lipsync = None

            # Initialize voice system (optional)
            if VOICE_ENABLED and VOICE_AVAILABLE:
                print("[AUDIO] Initializing voice system...")

                if VOICE_ENGINE == "espeak":
                    # eSpeak TTS with or without lip sync
                    try:
                        if LIPSYNC_ENABLED and self.lipsync:
                            # Use integrated version with lip sync
                            self.voice_system = VoiceSystem(
                                voice=ESPEAK_VOICE.split('+')[0],
                                speed=ESPEAK_SPEED,
                                pitch=ESPEAK_PITCH,
                                use_whisper='+whisper' in ESPEAK_VOICE,
                                lipsync_controller=self.lipsync
                            )
                            print(f"[OK] eSpeak TTS with lip sync ready (voice: {ESPEAK_VOICE}, {ESPEAK_SPEED} wpm)")
                        else:
                            # Regular eSpeak without lip sync
                            self.voice_system = VoiceSystem(
                                voice=ESPEAK_VOICE.split('+')[0],
                                speed=ESPEAK_SPEED,
                                pitch=ESPEAK_PITCH,
                                use_whisper='+whisper' in ESPEAK_VOICE
                            )
                            print(f"[OK] eSpeak TTS ready (voice: {ESPEAK_VOICE}, {ESPEAK_SPEED} wpm)")
                        if VOICE_ALL_THOUGHTS:
                            print("   [VOICE] Voice mode: EVERY thought")
                        else:
                            print(f"   [VOICE] Voice mode: Every {VOICE_INTERVAL}s")
                    except Exception as e:
                        print(f"[WARN] eSpeak TTS disabled: {e}")
                        self.voice_system = None
                        
                elif VOICE_ENGINE == "windows":
                    # Windows TTS
                    self.voice_system = VoiceSystem()
                    if self.voice_system.start():
                        self.voice_system.set_rate(WINDOWS_TTS_RATE)
                        self.voice_system.set_volume(WINDOWS_TTS_VOLUME)
                        self.voice_system.set_voice_gender(WINDOWS_TTS_GENDER)
                        
                        print(f"[OK] Windows TTS ready ({WINDOWS_TTS_GENDER}, {WINDOWS_TTS_RATE} wpm)")
                        if VOICE_ALL_THOUGHTS:
                            print("   [VOICE] Voice mode: EVERY thought")
                        else:
                            print(f"   [VOICE] Voice mode: Every {VOICE_INTERVAL}s")
                    else:
                        print("[WARN] Windows TTS disabled (not available)")
                        self.voice_system = None
                else:
                    # Piper TTS
                    self.voice_system = VoiceSystem(VOICE_MODEL)
                    if self.voice_system.start():
                        print(f"[OK] Piper TTS ready (model: {VOICE_MODEL})")
                        if VOICE_ALL_THOUGHTS:
                            print("   [VOICE] Voice mode: EVERY thought")
                        else:
                            print(f"   [VOICE] Voice mode: Every {VOICE_INTERVAL}s")
                    else:
                        print("[WARN] Piper TTS disabled (not found)")
                        self.voice_system = None
            else:
                if VOICE_ENABLED:
                    print("[MUTE] Voice system disabled (not available)")
                else:
                    print("[MUTE] Voice system disabled (config)")

            # Initialize subtitle projector (optional)
            if SUBTITLE_PROJECTOR_ENABLED and PROJECTOR_AVAILABLE:
                print("[PROJECT] Initializing subtitle projector...")
                try:
                    self.subtitle_projector = SubtitleProjectorClient()
                    print("[OK] Subtitle projector ready (fullscreen)")
                except Exception as e:
                    print(f"[WARN] Subtitle projector disabled: {e}")
                    self.subtitle_projector = None
            else:
                if SUBTITLE_PROJECTOR_ENABLED:
                    print("[PROJECT] Subtitle projector disabled (not available)")
                else:
                    print("[PROJECT] Subtitle projector disabled (config)")

            # Initialize hand control
            if DEBUG_MOTOR:
                print("[BOT] Initializing hand control...")
            self.hand_control = HandControlInterface()            # Launch hand control process (optional)
            # self.hand_control.launch_hand_controller(headless=True)

            print("[OK] All components initialized successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Initialization failed: {e}")
            if DEBUG_AI:
                print(traceback.format_exc())
            return False
    
    def run(self):
        """Main processing loop - single threaded, stable"""
        if not self.initialize():
            print("[ERROR] Initialization failed - cannot start")
            return

        # Enable signal handling after successful init
        self.signals_armed = True
        self.running = True
        print("[STOP] Embodied AI v2 starting main loop...")

        # Heartbeat tracking for crash detection
        self.last_heartbeat = time.time()
        self.frame_counter_for_heartbeat = 0
        self.memory_warning_shown = False
        
        try:
            # Direct VideoCapture using configured camera index
            print(f"[VIDEO] Opening Camera {CAMERA_INDEX} (0=built-in, 1=external)...")
            cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"[OK] Camera {CAMERA_INDEX} initialized: {actual_width}x{actual_height}")
            
            # Let camera stabilize before first AI processing (exposure/focus adjustment)
            print("[HOT] Camera warming up (2 seconds)...")
            warmup_start = time.time()
            while time.time() - warmup_start < 2.0:
                ret, frame = cap.read()  # Keep reading frames during warmup
                if ret and SHOW_CAMERA_PREVIEW:
                    display_frame = cv2.resize(frame, (PREVIEW_WIDTH, PREVIEW_HEIGHT))
                    cv2.imshow("[BOT] AI Inner Monologue", display_frame)
                    cv2.waitKey(1)
            print("[OK] Camera ready")
            
            while self.running:
                # EXACT machine.py pattern: ret, frame = cap.read() every loop
                ret, frame = cap.read()
                if not ret:
                    continue

                current_time = time.time()
                self.frame_count += 1

                # Heartbeat every 100 frames (~3 seconds at 30fps)
                self.frame_counter_for_heartbeat += 1
                if self.frame_counter_for_heartbeat >= 100:
                    self.last_heartbeat = current_time
                    self.frame_counter_for_heartbeat = 0
                    if DEBUG_AI:
                        print(f"💓 Heartbeat: frame {self.frame_count}, uptime {int(current_time - self.start_time)}s")

                # Detect face movement for dynamic pacing (every 5 frames to save CPU)
                if self.frame_count % 5 == 0:
                    self._detect_face_movement(frame)

                # === PERSON TRACKING - Run every 5 frames to reduce CPU load and improve stability with poor camera ===
                # Use cached data on non-tracking frames to avoid flicker
                person_events = []
                presence_state = None
                if self.frame_count % 5 == 0:
                    if self.personality and hasattr(self.personality, 'person_tracker'):
                        # DENOISING DISABLED: Causes memory allocation errors
                        # Use raw frame instead - person tracker is robust enough
                        # denoised_frame = cv2.bilateralFilter(frame, 5, 50, 50)
                        person_data = self.personality.person_tracker.analyze_frame(frame)
                        person_events = person_data.get('events', [])
                        presence_state = person_data.get('presence_state', None)

                        # Cache for use on non-tracking frames
                        self.cached_presence_state = presence_state

                        # Update personality tracking data for visualization
                        self.personality.last_person_positions = person_data.get('positions', [])
                        self.personality.last_detection_frame_size = (frame.shape[1], frame.shape[0])
                else:
                    # Use cached presence state on non-tracking frames (no events though)
                    presence_state = getattr(self, 'cached_presence_state', None)

                # === ACTIVITY DETECTION - Run every 2 frames to reduce CPU load ===
                activity_result = None
                if self.frame_count % 2 == 0:
                    if self.personality and hasattr(self.personality, 'activity_detector'):
                        activity_result = self.personality.activity_detector.analyze_frame(frame)
                        # Store for AI to use when processing
                        self.personality.last_activity_result = activity_result

                    # GENERATE AND QUEUE URGENT REACTIONS based on ACTUAL EVENTS (not just high urgency)
                    # Only generate when there's an actual arrival/departure/movement event
                    if presence_state and (presence_state.just_arrived or presence_state.just_left or
                                          (hasattr(presence_state, 'activity_changed') and presence_state.activity_changed)):
                        # Only queue reactions if enough time has passed (prevent spam)
                        time_since_last_reaction = current_time - self.last_urgent_reaction_time

                        # Reduced cooldown from 2.0s to 0.5s for more natural back-and-forth
                        if time_since_last_reaction > 0.5:
                            reaction = self._generate_contextual_reaction(presence_state)
                            if reaction:
                                urgency = presence_state.urgency_score if hasattr(presence_state, 'urgency_score') else 0.8
                                self.urgent_reaction_queue.add_reaction(
                                    reaction,
                                    urgency,
                                    context={'presence_duration': presence_state.presence_duration}
                                )
                                self.last_urgent_reaction_time = current_time
                                if DEBUG_AI:
                                    print(f"[TARGET] Queued contextual reaction: {reaction[:40]}...")

                # Calculate dynamic interval based on scene activity
                self.current_ai_interval = self._calculate_dynamic_interval()

                # IMMEDIATE AI trigger on major events (bypass interval)
                # Person events OR major visual activity (lights turning on, movement, etc)
                has_person_event = len(person_events) > 0

                # Use activity score for reactivity (frame-based, immediate)
                # High activity (>80) = major scene change happening NOW
                has_high_activity = (activity_result is not None and
                                    activity_result.get('activity_score', 0) > 80.0)

                force_ai_now = has_person_event or has_high_activity

                # AI processing in SEPARATE THREAD with dynamic interval
                should_process_ai = (current_time - self.last_ai_process_time >= self.current_ai_interval) or force_ai_now

                if should_process_ai:
                    # Only start new AI thread if previous one is complete
                    if self.ai_processing_lock.acquire(blocking=False):  # Non-blocking acquire
                        if DEBUG_AI:
                            if has_person_event:
                                print(f"[URGENT] PERSON EVENT - forcing immediate AI at frame {self.frame_count}")
                            elif has_high_activity:
                                print(f"[URGENT] HIGH ACTIVITY (score: {activity_result.get('activity_score', 0):.0f}) - forcing immediate AI at frame {self.frame_count}")
                            else:
                                print(f"[AI] Starting AI thread at frame {self.frame_count}")

                        # Start daemon thread for AI processing (machine.py pattern)
                        # Pass person_events for context-aware instant captions
                        ai_thread = threading.Thread(
                            target=self._ai_processing_thread,
                            args=(frame.copy(), current_time, person_events),
                            daemon=True
                        )
                        ai_thread.start()
                        self.last_ai_process_time = current_time
                    # Removed spammy AI processing messages
                
                # === DISPLAY OVERLAYS === (EXACT machine.py pattern)
                if SHOW_CAMERA_PREVIEW:
                    # Resize frame for preview (matching machine.py)
                    # Use INTER_NEAREST for faster resizing (less quality but much faster)
                    display_frame = cv2.resize(frame, (PREVIEW_WIDTH, PREVIEW_HEIGHT), interpolation=cv2.INTER_NEAREST)

                    # Draw person detection boxes every frame (uses cached positions from last tracking run)
                    display_frame = self._draw_person_detections(display_frame)

                    # Apply live captioning subtitle system
                    # DISABLED: Using projector only, camera overlay causes memory allocation errors
                    # if hasattr(self, 'current_subtitle') and self.current_subtitle:
                    #     display_frame = self._draw_live_caption_overlay(display_frame)

                    # DISPLAY (EXACT machine.py pattern)
                    cv2.imshow("[BOT] AI Inner Monologue", display_frame)

                    # Key handling (machine.py pattern)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print("[STOP] Quit key pressed")
                        break
                
                # Motor updates on interval 
                if current_time - self.last_motor_update_time >= 1.0:
                    self._update_motor_control(current_time)
                    self.last_motor_update_time = current_time
                
                # Status updates
                if VERBOSE_OUTPUT and current_time - self.last_status_time >= 10.0:
                    self._print_status(current_time)
                    self.last_status_time = current_time
                
        except KeyboardInterrupt:
            print("\n[STOP] Keyboard interrupt received")
        except Exception as e:
            print(f"[ERROR] Main loop error: {e}")
            print(f"[ERROR] Last heartbeat: {int(time.time() - self.last_heartbeat)}s ago")
            if DEBUG_AI:
                print(traceback.format_exc())
        finally:
            print(f"[SHUTDOWN] Main loop exited at frame {self.frame_count}")
            print(f"[SHUTDOWN] Total uptime: {int(time.time() - self.start_time)}s")

            # Clean up direct camera
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()
            self.shutdown()
    

    def _ai_processing_thread(self, frame, timestamp, person_events=None):
        """AI processing in separate thread (EXACT machine.py pattern)"""
        thread_start = time.time()
        try:
            if DEBUG_AI:
                print(f"[AI] AI thread processing frame at {timestamp}")

            # Pass person events to personality for instant captions
            if person_events:
                self.personality.pending_person_events = person_events

            # Call AI (this is the slow blocking operation)
            # Simple consciousness processing
            response = self.personality.analyze_image(frame)
            
            if DEBUG_AI:
                if response:
                    print(f"[BOT] AI processing complete - got response")
                else:
                    print(f"[STOP] AI choosing silence - no response")
            
            if response:
                if DEBUG_AI:
                    print(f"[TARGET] AI returned response: {response}")
                
                # Clean caption - remove debug markers and system text
                import re
                clean_caption = response.strip()
                
                # Light cleaning - just remove obvious prefixes
                prefixes_to_remove = ["caption:", "my thought:"]
                for prefix in prefixes_to_remove:
                    if clean_caption.lower().startswith(prefix):
                        clean_caption = clean_caption[len(prefix):].strip()
                
                # Remove any bracketed metadata (already done in personality.py but just in case)
                clean_caption = re.sub(r'\[(?:Tone|Internal|System|Visual)[^\]]*\]', '', clean_caption, flags=re.IGNORECASE)
                
                # Remove debug markers that might slip through (escape brackets for literal match)
                clean_caption = re.sub(r'(\[TARGET\]|\[CLEAN\]|\[BLOCKED\]|\[RETRY\]|\[OK\]|\[STOP\]|\[AI\]|\[THINK\]|\[PRINT\]|\[NOTE\])', '', clean_caption)
                
                # Replace TTS-unfriendly sounds
                clean_caption = re.sub(r'\bMmm+\b', 'Aah', clean_caption, flags=re.IGNORECASE)
                clean_caption = re.sub(r'\bHmm+\b', 'Huh', clean_caption, flags=re.IGNORECASE)

                # Clean up extra whitespace
                clean_caption = ' '.join(clean_caption.split())
                clean_caption = clean_caption.strip()

                if DEBUG_AI:
                    print(f"[CLEAN] Cleaned caption: {clean_caption[:100]}{'...' if len(clean_caption) > 100 else ''}")
                
                # Thread-safe live captioning subtitle update
                with self.subtitle_lock:
                    # INCREMENT VERSION - this invalidates all old chunk callbacks!
                    # Old chunks will check version and abort their callbacks
                    self.caption_version += 1

                    self.current_subtitle = clean_caption

                    # NOTE: Don't send to projector here - it will be updated per chunk
                    # This ensures projector shows chunks in sync with camera preview

                    # Create sentence-based chunks (like live captioning)
                    self.subtitle_chunks = self._create_smart_chunks(clean_caption)

                    # Remove consecutive duplicate chunks within this caption
                    if self.subtitle_chunks:
                        deduped_chunks = []
                        last_norm = None
                        for chunk in self.subtitle_chunks:
                            normalized = self._normalize_chunk_text(chunk)
                            if not normalized:
                                continue
                            if normalized == last_norm:
                                continue
                            deduped_chunks.append(chunk)
                            last_norm = normalized
                        if deduped_chunks:
                            self.subtitle_chunks = deduped_chunks

                    # Skip chunks that just played in the previous caption
                    if self.subtitle_chunks:
                        recent_norms = self.recent_spoken_chunks[-3:] if self.recent_spoken_chunks else []
                        filtered_chunks = []
                        for chunk in self.subtitle_chunks:
                            normalized = self._normalize_chunk_text(chunk)
                            if not normalized:
                                continue
                            if normalized in recent_norms:
                                if DEBUG_AI:
                                    print(f"[WARN] Skipping recently spoken chunk: '{chunk}'")
                                continue
                            filtered_chunks.append(chunk)
                        if filtered_chunks:
                            self.subtitle_chunks = filtered_chunks
                        else:
                            if DEBUG_AI:
                                print("[WARN] Caption skipped entirely (chunks already spoken).")
                            return

                    # DEBUG: Print all chunks that will be spoken
                    if DEBUG_AI:
                        print(f"[LIST] Created {len(self.subtitle_chunks)} chunks:")
                        for i, chunk in enumerate(self.subtitle_chunks):
                            print(f"   Chunk {i}: '{chunk}'")

                    # Initialize ready flags - all False (waiting for jaw movement)
                    self.chunk_ready_flags = [False] * len(self.subtitle_chunks)

                    # Reset to first chunk
                    self.current_chunk_index = 0
                    self.subtitle_start_time = time.time()
                    self.last_chunk_change_time = time.time()
                    
                    # Reset silence period when new content appears
                    if self.in_silence_period:
                        self.in_silence_period = False
                        if DEBUG_CAMERA:
                            print()  # New line after silence timer
                    
                    # Calculate dynamic duration for first chunk (based on TTS duration)
                    if self.subtitle_chunks:
                        first_chunk = self.subtitle_chunks[0]
                        word_count = len(first_chunk.split())
                        total_words = len(clean_caption.split())
                        self.chunk_display_duration = self._calculate_tts_duration(word_count)

                        # Speak first chunk with callback to mark it ready when jaw moves
                        if self.voice_system and VOICE_ALL_THOUGHTS:
                            if DEBUG_AI:
                                print(f"[VOICE] Speaking chunk 0/{len(self.subtitle_chunks)-1}: {first_chunk[:50]}...")

                            # Capture version AND chunk text for closure
                            chunk_0_version = self.caption_version
                            chunk_0_text = first_chunk

                            # Callback to mark chunk 0 as ready when jaw moves
                            def on_jaw_movement_chunk_0():
                                # Always update projector when jaw moves (show what's actually being spoken)
                                # Even if caption version changed, the TTS is playing so user should see it
                                print(f"[ANNOUNCE] Chunk 0 jaw moved!")
                                if self.subtitle_projector:
                                    try:
                                        self.subtitle_projector.display(chunk_0_text)
                                        if DEBUG_AI:
                                            print(f"[PROJECT] Projector: '{chunk_0_text[:50]}...'")
                                    except Exception as e:
                                        if DEBUG_AI:
                                            print(f"[WARN] Projector update error: {e}")

                                # Only update internal state if this is still the current caption
                                if self.caption_version == chunk_0_version:
                                    with self.subtitle_lock:
                                        if len(self.chunk_ready_flags) > 0:
                                            self.chunk_ready_flags[0] = True
                                            # Reset timer NOW (when jaw actually moves)
                                            self.last_chunk_change_time = time.time()
                                            self._remember_spoken_chunk(chunk_0_text)

                            # Callback when chunk 0 finishes - speak chunk 1
                            def on_chunk_0_finished():
                                if self.caption_version != chunk_0_version:
                                    return  # Old caption - ignore
                                print(f"\n[OK] Chunk 0 finished!")
                                self._speak_next_chunk(0, chunk_0_version)

                            self._speak_async(first_chunk, total_caption_words=total_words,
                                            on_start_callback=on_jaw_movement_chunk_0,
                                            on_end_callback=on_chunk_0_finished)

                # Show FIRST CHUNK with timestamp - other chunks will print as they speak
                timestamp_str = time.strftime("%H:%M:%S")
                if self.subtitle_chunks:
                    print(f"\n[{timestamp_str}] [THINK] {self.subtitle_chunks[0]}", end="", flush=True)

                # Send to thermal printer for rhythmic printing
                if self.thermal_printer:
                    if DEBUG_AI:
                        print(f"[PRINT] Sending to thermal printer: {clean_caption[:50]}...")
                    self.thermal_printer.print_subtitle(clean_caption)
                else:
                    if DEBUG_AI:
                        print(f"[ERROR] No thermal printer available")
            else:
                if DEBUG_AI:
                    print("[STOP] AI remained silent - extending pause before next query")
                self.last_ai_process_time = time.time()
                if not self.in_silence_period:
                    print()
                    self.in_silence_period = True
                    self.silence_start_time = time.time()
                    if self.subtitle_projector:
                        try:
                            self.subtitle_projector.clear()
                        except Exception as e:
                            if DEBUG_AI:
                                print(f"[WARN] Projector clear error during silence: {e}")
        
        except Exception as e:
            thread_time = time.time() - thread_start
            print(f"[ERROR] AI thread error after {thread_time:.1f}s: {e}")
            if DEBUG_AI:
                print(traceback.format_exc())
        finally:
            thread_time = time.time() - thread_start
            # Always release the AI processing lock
            self.ai_processing_lock.release()
            if DEBUG_AI:
                print(f"[UNLOCK] AI processing lock released (thread took {thread_time:.1f}s)")
    
    def _get_emotional_voice_params(self):
        """Get speed/pitch variations based on current emotion"""
        if not self.personality:
            return None, None

        emotion = self.personality.current_emotion

        # Emotion-based voice variations (whisper with emotional character)
        emotion_params = {
            'excited': {'speed': 170, 'pitch': 60},      # Faster, higher
            'curious': {'speed': 155, 'pitch': 55},      # Slightly faster, slightly higher
            'alert': {'speed': 165, 'pitch': 58},        # Fast, elevated
            'wondering': {'speed': 140, 'pitch': 48},    # Slower, contemplative
            'confused': {'speed': 135, 'pitch': 45},     # Slow, lower
            'contemplative': {'speed': 130, 'pitch': 42}, # Very slow, deeper
            'peaceful': {'speed': 140, 'pitch': 48},     # Calm, neutral
            'engaged': {'speed': 150, 'pitch': 50},      # Normal baseline
            'focused': {'speed': 145, 'pitch': 48},      # Steady
        }

        params = emotion_params.get(emotion, {'speed': 150, 'pitch': 50})
        return params['speed'], params['pitch']

    def _speak_next_chunk(self, just_finished_idx, expected_version):
        """Speak the next chunk after the current one finishes"""
        # Check version FIRST before acquiring lock
        if self.caption_version != expected_version:
            return  # Old caption - abort

        with self.subtitle_lock:
            # Double-check version inside lock
            if self.caption_version != expected_version:
                return  # Old caption - abort

            # Advance to next chunk
            next_idx = just_finished_idx + 1
            if next_idx >= len(self.subtitle_chunks):
                return  # No more chunks

            self.current_chunk_index = next_idx
            print(f"[SKIP]  Advanced to chunk {next_idx}")

            chunk = self.subtitle_chunks[next_idx]
            current_ver = self.caption_version

        # Print chunk to console
        print(f" {chunk}", end="", flush=True)

        # Capture the actual chunk text for the callback (not just the index!)
        chunk_text_for_callback = chunk

        # Callbacks for this chunk
        def on_jaw_movement():
            # Always update projector when jaw moves (show what's actually being spoken)
            # Even if caption version changed, the TTS is playing so user should see it
            print(f"\n[ANNOUNCE] Chunk {next_idx} jaw moved!")
            if self.subtitle_projector:
                try:
                    self.subtitle_projector.display(chunk_text_for_callback)
                    if DEBUG_AI:
                        print(f"[PROJECT] Projector: '{chunk_text_for_callback[:50]}...'")
                except Exception as e:
                    if DEBUG_AI:
                        print(f"[WARN] Projector update error: {e}")

            # Only update internal state if this is still the current caption
            if self.caption_version == expected_version:
                with self.subtitle_lock:
                    if next_idx < len(self.chunk_ready_flags):
                        self.chunk_ready_flags[next_idx] = True
                        self.last_chunk_change_time = time.time()
                        self._remember_spoken_chunk(chunk_text_for_callback)

        def on_finished():
            if self.caption_version != expected_version:
                return  # Old caption - ignore
            print(f"\n[OK] Chunk {next_idx} finished!")

            # CHECK FOR URGENT REACTIONS BEFORE CONTINUING CHUNK CHAIN
            urgent = self.urgent_reaction_queue.get_if_urgent(threshold=0.6)
            if urgent:
                # URGENT REACTION - interrupt caption chain
                if DEBUG_AI:
                    print(f"[URGENT] URGENT REACTION interrupting (urgency {urgent['urgency']:.2f}): {urgent['text']}")

                # Increment version to abort old caption chain
                with self.subtitle_lock:
                    self.caption_version += 1

                # Speak urgent reaction immediately
                self._speak_urgent_reaction(urgent['text'])
                return  # DON'T continue old caption chain

            # No urgent reaction - continue normal chunk chain
            self._speak_next_chunk(next_idx, expected_version)  # Recursive chain!

        # Speak it
        if self.voice_system and VOICE_ALL_THOUGHTS:
            self._speak_async(chunk, caption_version=current_ver,
                            on_start_callback=on_jaw_movement,
                            on_end_callback=on_finished)

    def _speak_async(self, text, total_caption_words=None, caption_version=None, on_start_callback=None, on_end_callback=None):
        """Speak text with emotional variation in a separate thread"""
        if not self.voice_system or not text:
            return

        speech_word_count = len(text.split())
        effective_word_count = total_caption_words or speech_word_count

        def speak_worker():
            try:
                # BEFORE speaking, check if caption is still current (abort if new caption arrived)
                if caption_version is not None and caption_version != self.caption_version:
                    # Old caption - silently abort (new caption is more important)
                    return

                # Get emotional voice variations
                emotion_speed, emotion_pitch = self._get_emotional_voice_params()

                # If this is part of a verbose caption, speed up further
                if effective_word_count and effective_word_count > 30:
                    speed = int(emotion_speed * 1.2) if emotion_speed else None
                else:
                    speed = emotion_speed

                # Use emotional variations with callbacks
                self.voice_system.speak(text, speed=speed, pitch=emotion_pitch, on_start_callback=on_start_callback, on_end_callback=on_end_callback)
                # Lip sync happens automatically via audio monitoring
            except Exception as e:
                if DEBUG_AI:
                    print(f"[WARN] TTS error: {e}")

        # Start speaking in background thread
        thread = threading.Thread(target=speak_worker, daemon=True)
        thread.start()

    def _speak_urgent_reaction(self, text):
        """Speak urgent reaction immediately (bypasses chunking, simple TTS)"""
        if not self.voice_system or not text:
            return

        if DEBUG_AI:
            print(f"[AUDIO] Speaking urgent reaction: {text}")

        # Print to console
        timestamp_str = time.strftime("%H:%M:%S")
        print(f"\n[{timestamp_str}] [URGENT] {text}")

        # ADD TO CONVERSATION HISTORY so next thought continues from this
        if self.personality:
            # DON'T add period - let conversation flow naturally
            # Greeting reactions should open into dialogue, not close off
            pass

            # UNIFIED SYSTEM: Record observation in focus engine (replaces _update_noun_tracking)
            if hasattr(self.personality, 'focus_engine') and hasattr(self.personality.focus_engine, 'record_observation'):
                current_focus = getattr(self.personality, 'current_focus_mode', 'VISUAL')
                self.personality.focus_engine.record_observation(text, current_focus)

            self.personality.recent_responses.append(text)
            # Keep list size manageable
            if len(self.personality.recent_responses) > self.personality.max_conversation_history:
                self.personality.recent_responses.pop(0)

        # Update projector
        if self.subtitle_projector:
            try:
                self.subtitle_projector.display(text)
            except Exception as e:
                if DEBUG_AI:
                    print(f"[WARN] Projector update error: {e}")

        # Speak it (no callbacks, simple immediate speech)
        def speak_worker():
            try:
                # Get emotional voice variations
                emotion_speed, emotion_pitch = self._get_emotional_voice_params()
                self.voice_system.speak(text, speed=emotion_speed, pitch=emotion_pitch)
            except Exception as e:
                if DEBUG_AI:
                    print(f"[WARN] TTS error: {e}")

        # Start speaking in background thread
        thread = threading.Thread(target=speak_worker, daemon=True)
        thread.start()

    def _create_smart_chunks(self, text):
        """Break text into sentence-based chunks for live captioning flow"""
        import re

        # If the whole thought is short (under 15 words), don't chunk at all
        total_words = len(text.split())
        if total_words <= 15:
            return [text.strip()]

        # Split into sentences using regex (more robust than simple punctuation)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        for sentence in sentences:
            # Don't split sentences that are reasonable length (max ~12 words for comfortable reading)
            if len(sentence.split()) <= 12:
                chunks.append(sentence)
            else:
                # Split long sentences at natural breaks - KEEP PUNCTUATION for clarity
                # Look for commas, semicolons (but keep them with the preceding text)
                split_pattern = r'[,;]\s+'
                last_end = 0
                parts = []

                for match in re.finditer(split_pattern, sentence):
                    # Get text INCLUDING the delimiter (comma/semicolon)
                    part = sentence[last_end:match.start() + 1].strip()  # +1 to include punctuation
                    if part and len(part.split()) >= 4:  # Only split if chunk has at least 4 words
                        parts.append(part)
                        last_end = match.end()

                # Add remaining text after last delimiter
                if last_end < len(sentence):
                    part = sentence[last_end:].strip()
                    if part:
                        parts.append(part)

                # If we got parts, use them; otherwise keep whole sentence
                if parts and len(parts) > 1:  # Only split if we got multiple meaningful chunks
                    chunks.extend(parts)
                else:
                    chunks.append(sentence)

        return chunks
    
    def _calculate_tts_duration(self, word_count):
        """Calculate how long TTS takes to speak a chunk based on eSpeak speed (130 wpm)"""
        words_per_minute = ESPEAK_SPEED  # 130 from config
        words_per_second = words_per_minute / 60.0
        base_duration = word_count / words_per_second
        
        # Add slight breathing room between chunks
        buffered_duration = base_duration + 0.5
        
        # Set reasonable bounds (lower min for short chunks)
        min_duration = 1.0
        max_duration = 8.0  # Longer max to accommodate full TTS playback
        
        return max(min_duration, min(max_duration, buffered_duration))
    
    def _draw_live_caption_overlay(self, frame):
        """Draw live captioning-style overlay with organic chunk progression and 4-second max display"""
        current_time = time.time()
        
        with self.subtitle_lock:
            if not self.subtitle_chunks or self.current_chunk_index >= len(self.subtitle_chunks):
                return frame
            
            # Calculate how long current chunk has been displayed
            chunk_display_time = current_time - self.last_chunk_change_time
            
            # Hide chunk after 6 seconds maximum (longer for reading)
            if chunk_display_time >= 6.0:
                if not self.in_silence_period:
                    # Just entered silence period - end the caption line
                    print()  # Newline to complete the caption
                    self.in_silence_period = True
                    self.silence_start_time = current_time

                    # Clear projector subtitle when entering silence
                    if self.subtitle_projector:
                        try:
                            self.subtitle_projector.clear()
                        except Exception as e:
                            if DEBUG_AI:
                                print(f"[WARN] Projector clear error: {e}")

                    if DEBUG_CAMERA:
                        print(f"[MUTE] Entering silence period...")
                elif DEBUG_CAMERA:
                    # Show countdown timer (update in place)
                    silence_duration = current_time - self.silence_start_time
                    # No specific end time for silence, just show duration
                    print(f"\r[MUTE] Silence: {silence_duration:.1f}s", end="", flush=True)
                return frame  # Show blank space - silence is important
            
            # Chunks now advance automatically when audio finishes (via on_chunk_finished callback)
            # No time-based advancement needed!
            
            # Get current chunk to display (only if jaw has moved for this chunk)
            if (self.current_chunk_index < len(self.chunk_ready_flags) and
                self.chunk_ready_flags[self.current_chunk_index]):
                current_chunk = self.subtitle_chunks[self.current_chunk_index]

                # NOTE: Projector is updated in jaw_movement callback, not here
                # This ensures immediate updates without waiting for display loop

                if DEBUG_CAMERA:
                    print(f"[OK] Chunk {self.current_chunk_index} ready - displaying: {current_chunk[:50]}")
            else:
                # Chunk not ready yet - jaw hasn't moved
                if DEBUG_CAMERA and self.current_chunk_index < len(self.chunk_ready_flags):
                    print(f"[WAIT] Chunk {self.current_chunk_index} not ready yet (flag={self.chunk_ready_flags[self.current_chunk_index]})")
                return frame

        # Draw subtitle overlay (legacy-style: smaller, fitted background)
        lines = textwrap.wrap(current_chunk, width=65)  # Slightly more characters for better flow
        if not lines:
            return frame
        
        # Smaller text like legacy system
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5  # Smaller like legacy
        font_color = (0, 255, 255)  # Yellow
        font_thickness = 1
        line_height = 22  # Tighter spacing
        padding = 10
        
        # Calculate text dimensions for fitted background
        frame_height, frame_width = frame.shape[:2]
        max_line_width = 0
        text_positions = []
        
        for line in lines:
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
            max_line_width = max(max_line_width, text_size[0])
            # Center text horizontally
            x_pos = (frame_width - text_size[0]) // 2
            text_positions.append((x_pos, text_size[0]))
        
        # Create fitted background overlay (not full width)
        overlay_width = max_line_width + (2 * padding)
        overlay_height = len(lines) * line_height + (2 * padding)
        overlay_x = (frame_width - overlay_width) // 2  # Center the background
        overlay_y = frame_height - overlay_height - 15  # Bottom margin
        
        # Draw fitted semi-transparent background
        try:
            overlay = frame.copy()
            cv2.rectangle(overlay,
                         (int(overlay_x), int(overlay_y)),
                         (int(overlay_x + overlay_width), int(overlay_y + overlay_height)),
                         (0, 0, 0), -1)
            frame = cv2.addWeighted(frame, 0.3, overlay, 0.7, 0)  # More subtle transparency
        except cv2.error as e:
            # Out of memory - skip transparency, just draw solid background
            if "memory" in str(e).lower():
                if not self.memory_warning_shown:
                    print("[WARN] Low memory detected - using simplified overlay")
                    print("[WARN] Consider restarting soon to free memory")
                    self.memory_warning_shown = True
                cv2.rectangle(frame,
                             (int(overlay_x), int(overlay_y)),
                             (int(overlay_x + overlay_width), int(overlay_y + overlay_height)),
                             (0, 0, 0), -1)
            else:
                raise
        
        # Draw text lines
        for i, line in enumerate(lines):
            x_pos = int(text_positions[i][0])
            y_pos = int(overlay_y + padding + 16 + (i * line_height))
            
            # Draw text with subtle outline
            cv2.putText(frame, line, (x_pos + 1, y_pos + 1), font, font_scale, (0, 0, 0), font_thickness + 1)
            cv2.putText(frame, line, (x_pos, y_pos), font, font_scale, font_color, font_thickness)
        
        return frame

    def _draw_person_detections(self, frame):
        """Draw person detection bounding boxes on the frame"""
        try:
            if not self.personality or not hasattr(self.personality, 'last_person_positions'):
                return frame

            # Get the original frame dimensions and display frame dimensions
            display_height, display_width = frame.shape[:2]

            # Get person positions from personality (these are in original frame coordinates)
            person_positions = self.personality.last_person_positions

            if not person_positions:
                return frame

            # Get actual detection frame size from personality
            original_width, original_height = self.personality.last_detection_frame_size

            # Calculate scaling factors
            scale_x = display_width / original_width
            scale_y = display_height / original_height

            # Draw each person detection
            for person in person_positions:
                bbox = person['bbox']  # [x1, y1, x2, y2] in original coordinates
                conf = person['confidence']

                # Scale bounding box to display coordinates
                x1 = int(bbox[0] * scale_x)
                y1 = int(bbox[1] * scale_y)
                x2 = int(bbox[2] * scale_x)
                y2 = int(bbox[3] * scale_y)

                # Draw bounding box (green)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Draw confidence label
                label = f"Person {conf:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]

                # Draw label background
                cv2.rectangle(frame,
                            (x1, y1 - label_size[1] - 4),
                            (x1 + label_size[0], y1),
                            (0, 255, 0), -1)

                # Draw label text
                cv2.putText(frame, label, (x1, y1 - 2),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # Draw person count overlay in top-right corner
            person_count = len(person_positions)
            if person_count > 0:
                count_text = f"People: {person_count}"
                text_size = cv2.getTextSize(count_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]

                # Position in top-right with margin
                text_x = display_width - text_size[0] - 10
                text_y = text_size[1] + 10

                # Draw background
                cv2.rectangle(frame,
                            (text_x - 5, text_y - text_size[1] - 5),
                            (text_x + text_size[0] + 5, text_y + 5),
                            (0, 0, 0), -1)

                # Draw text
                cv2.putText(frame, count_text, (text_x, text_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            return frame

        except Exception as e:
            if DEBUG_CAMERA:
                print(f"[WARN] Person detection drawing error: {e}")
            return frame

    def _update_motor_control(self, current_time):
        """Update motor control based on personality state"""
        try:
            if not self.personality or not self.hand_control:
                return
            
            # Get motor suggestion from personality
            motor_suggestion = self.personality.get_motor_suggestion()
            hand_emotion = personality_to_hand_emotion(motor_suggestion)
            
            # Update hand control
            mood_value = self.personality.mood
            success = self.hand_control.set_emotion(hand_emotion, mood_value)
            
            if success and DEBUG_MOTOR:
                print(f"[BOT] Motor updated: {hand_emotion} (mood: {mood_value:.2f})")
                
        except Exception as e:
            if DEBUG_MOTOR:
                print(f"Motor update error: {e}")
    
    
    def _detect_face_movement(self, frame):
        """Detect face and check if it moved significantly"""
        try:
            # Use OpenCV's Haar Cascade for face detection (built-in, fast)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) > 0:
                # Get first face position (x, y, w, h)
                x, y, w, h = faces[0]
                face_center = (x + w//2, y + h//2)

                # Check if face moved significantly
                if self.last_face_position:
                    dx = abs(face_center[0] - self.last_face_position[0])
                    dy = abs(face_center[1] - self.last_face_position[1])
                    movement = (dx + dy) / 2

                    # Consider movement significant if > 30 pixels
                    if movement > 30:
                        self.face_movement_detected = True
                        self.last_face_position = face_center
                        return True

                self.last_face_position = face_center
                return False
            else:
                # No face detected
                self.last_face_position = None
                return False
        except:
            return False

    def _generate_contextual_reaction_llm(self, event_type, presence_state):
        """Generate contextual reaction using llava with minimal prompt"""

        # Build event description
        events = {
            "arrival": "someone arrived",
            "departure": "someone left",
            "movement": "movement detected"
        }
        event = events.get(event_type, "change")

        # Ultra-minimal prompt for speed
        prompt = f"Duck sees: {event}. React (2 words):"

        try:
            import requests
            import base64
            from config import OLLAMA_URL, SINGLE_MULTIMODAL_MODEL

            # Get current frame for visual context
            image_b64 = None
            if hasattr(self, 'latest_frame_path') and self.latest_frame_path:
                try:
                    with open(self.latest_frame_path, 'rb') as f:
                        image_b64 = base64.b64encode(f.read()).decode('utf-8')
                except:
                    pass

            # Use same llava model as main thoughts but ultra-minimal prompt
            data = {
                "model": SINGLE_MULTIMODAL_MODEL,
                "prompt": prompt,
                "stream": False,
                "images": [image_b64] if image_b64 else [],
                "options": {
                    "temperature": 0.95,
                    "num_predict": 8  # Very short - force brief response
                }
            }

            response = requests.post(f"{OLLAMA_URL}/api/generate", json=data, timeout=8)  # Generous timeout
            if response.status_code == 200:
                result = response.json()
                reaction = result.get('response', '').strip()

            if reaction:
                    # Clean and validate
                    reaction = reaction.strip()
                    # Only filter out explicit AI/meta language - keep personality quirks
                    if any(bad in reaction.lower() for bad in ["as a duck", "as an ai", "i am an ai", "language model"]):
                        if DEBUG_AI:
                            print(f"[FILTER] Rejected meta AI response: {reaction[:50]}")
                        return None
                    return reaction
        except Exception as e:
            if DEBUG_AI:
                print(f"[ERROR] Contextual reaction generation failed: {e}")

        return None

    def _generate_contextual_reaction(self, presence_state):
        """Generate contextual reaction based on presence state - INSTANT FALLBACKS ONLY (skip LLM to avoid Ollama overload)"""
        import random

        # ARRIVAL reactions - use instant fallbacks to avoid concurrent llava calls
        if presence_state.just_arrived:
            if presence_state.presence_duration < 1.0:
                # Just arrived this moment - use simple interjections (no LLM call)
                return random.choice(["Oh", "Hello there", "Hi", "Hm"])
            else:
                # Already acknowledged - don't repeat
                return None

        # DEPARTURE reactions - disabled to avoid concurrent llava calls
        elif presence_state.just_left:
            # Skip LLM call - return None (no reaction needed for departures)
            return None

        # MOVEMENT reactions - disabled to avoid concurrent llava calls
        elif presence_state.activity_description in ["moving", "moving around"]:
            # Check if person was previously still (prevents spam)
            was_still = getattr(self, 'person_was_still', True)
            if was_still:
                self.person_was_still = False
                # Skip LLM call - return None (no reaction needed for movement)
                return None
            return None

        # Reset stillness flag when person becomes still again
        elif presence_state.activity_description == "still":
            self.person_was_still = True
            return None

        return None

    def _calculate_dynamic_interval(self):
        """Calculate AI process interval based on activity detection"""
        # Use activity detector's suggested delay if available
        if self.personality and hasattr(self.personality, 'suggested_check_delay'):
            interval = self.personality.suggested_check_delay

            # Override with faster response if face movement detected
            if self.face_movement_detected:
                interval = min(interval, 2.0)  # Cap at 2 seconds when face moving
        else:
            # Fallback to old system if activity detector not available
            static_duration = 0
            if self.personality and hasattr(self.personality, 'focus_engine'):
                static_duration = self.personality.focus_engine.static_duration

            if self.face_movement_detected:
                interval = 5.0
            elif static_duration < 15:
                interval = AI_PROCESS_INTERVAL
            elif static_duration < 30:
                interval = AI_PROCESS_INTERVAL * 1.3
            elif static_duration < 60:
                interval = AI_PROCESS_INTERVAL * 1.8
            else:
                interval = AI_PROCESS_INTERVAL * 2.5

        # Reset face movement flag
        self.face_movement_detected = False

        return interval

    def _print_status(self, current_time):
        """Print system status"""
        try:
            runtime = current_time - self.start_time
            fps = self.frame_count / runtime if runtime > 0 else 0
            
            # Get component status
            ai_status = self.personality.get_status() if self.personality else {}
            motor_status = self.hand_control.get_status() if self.hand_control else {}
            
            print(f"\n[STATS] Status (Runtime: {runtime:.1f}s, FPS: {fps:.1f}):")
            print(f"   [AI] AI: Mood={ai_status.get('mood', 0):.2f}, "
                  f"Beliefs={ai_status.get('beliefs', 0)}, "
                  f"Observations={ai_status.get('observations', 0)}")
            print(f"   [BOT] Motor: {motor_status.get('current_emotion', 'unknown')}, "
                  f"Running={motor_status.get('is_running', False)}")
            
        except Exception as e:
            print(f"Status error: {e}")
    
    def shutdown(self):
        """Clean shutdown of all components"""
        print("[RETRY] Shutting down embodied AI...")
        self.running = False
        
        try:
            # Cleanup components
            if self.personality:
                self.personality.save_state()
                print("[SAVE] AI state saved")
            
            if self.thermal_printer:
                self.thermal_printer.stop()
                print("[PRINT] Thermal printer stopped")

            if self.lipsync:
                self.lipsync.stop()
                print("[LIPSYNC] Lip sync stopped")

            if self.voice_system:
                self.voice_system.stop()
                print("[MUTE] Voice system stopped")

            if self.hand_control:
                self.hand_control.cleanup()
                print("[BOT] Hand control cleaned up")

            # Camera handled directly in main loop
            print("[CAMERA] Camera cleanup handled in main loop")
            
            print("[OK] Shutdown complete")
            
        except Exception as e:
            print(f"[WARN] Shutdown error: {e}")


def main():
    """Main entry point"""
    print("[BOT] Embodied AI v2 - Starting...")
    print(f"[LIST] Config: AI interval={AI_PROCESS_INTERVAL}s, Camera={CAMERA_WIDTH}x{CAMERA_HEIGHT}")
    
    # Create and run system
    ai_system = EmbodiedAI()
    ai_system.run()


if __name__ == "__main__":
    main()
