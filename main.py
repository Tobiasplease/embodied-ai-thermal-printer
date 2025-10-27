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
import traceback
import threading
import textwrap
from datetime import datetime

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
    ESPEAK_VOICE, ESPEAK_SPEED, ESPEAK_PITCH
)

# Import voice system (optional)
VOICE_AVAILABLE = False
if VOICE_ENABLED:
    try:
        if VOICE_ENGINE == "espeak":
            from espeak_tts_simple import ESpeakTTS as VoiceSystem
            VOICE_AVAILABLE = True
        elif VOICE_ENGINE == "windows":
            from windows_tts import WindowsTTS as VoiceSystem
            VOICE_AVAILABLE = True
        else:  # piper
            from voice import VoiceSystem
            VOICE_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ Voice system not available: {e}")
        VOICE_AVAILABLE = False

def clear_print_queue_preemptive():
    """Clear Windows print queue aggressively with admin elevation"""
    try:
        import subprocess
        import os
        import sys
        print("🗑️ Aggressively clearing Windows print spooler...")
        
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
        print("🔐 Running spooler clear with admin privileges...")
        try:
            # Method 1: Try to run with elevated privileges
            result = subprocess.run([
                'powershell', '-Command', 
                f'Start-Process -FilePath "{batch_path}" -Verb RunAs -Wait -WindowStyle Hidden'
            ], capture_output=True, timeout=15, text=True)
            
            if result.returncode == 0:
                print("✅ Print spooler cleared with admin privileges")
            else:
                raise Exception("Admin elevation failed")
                
        except Exception:
            # Method 2: Fallback - try without elevation
            print("⚠️ Admin elevation failed, trying without privileges...")
            subprocess.run(['net', 'stop', 'spooler'], capture_output=True, shell=True)
            subprocess.run(['net', 'start', 'spooler'], capture_output=True, shell=True)
            print("✅ Print spooler restarted (limited permissions)")
        
        # Clean up batch file
        try:
            os.remove(batch_path)
        except:
            pass
            
    except Exception as e:
        print(f"⚠️ Could not clear print queue: {e}")
        print("💡 Manual solution: Run as Administrator and execute:")
        print("   net stop spooler && del /q C:\\Windows\\System32\\spool\\PRINTERS\\*.* && net start spooler")
class EmbodiedAI:
    """Main embodied AI system - clean single-threaded design"""
    
    def __init__(self):
        self.running = False
        self.camera = None
        self.personality = None
        self.hand_control = None
        self.thermal_printer = None
        self.voice_system = None
        
        # Timing controls - avoid threading issues
        self.last_ai_process_time = 0
        self.last_motor_update_time = 0
        self.last_status_time = 0
        self.last_voice_time = 0  # Track last voice output
        self.ai_processing_lock = threading.Lock()  # Prevent concurrent AI processing
        
        # Frame processing
        self.frame_count = 0
        self.start_time = time.time()
        
        # Live captioning subtitle system (thread-safe)
        self.current_subtitle = ""
        self.subtitle_chunks = []
        self.current_chunk_index = 0
        self.subtitle_start_time = 0
        self.chunk_display_duration = 0  # Dynamic duration per chunk
        self.last_chunk_change_time = 0
        self.subtitle_lock = threading.Lock()
        self.caption_version = 0  # Track caption changes to prevent old chunks from speaking
        
        # Silence period tracking
        self.in_silence_period = False
        self.silence_start_time = 0
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        if VERBOSE_OUTPUT:
            print("🤖 Embodied AI v2 initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Shutdown signal received ({signum}ö")
        self.shutdown()
        sys.exit(0)
    
    def initialize(self):
        """Initialize all components"""
        try:
            # FIRST: Clear any stuck print jobs before connecting printer
            clear_print_queue_preemptive()
            
            # Clear old personality state that has drawing machine references
            import os
            state_file = "personality_state.json"
            if os.path.exists(state_file):
                os.remove(state_file)
                print("🧹 Cleared old personality state with drawing machine references")
            
            # Skip Camera class initialization - we'll use direct cv2 access
            if DEBUG_CAMERA:
                print("📷 Will initialize camera directly in main loop...")
            self.camera = None  # Don't use Camera class to avoid threading issues
            
            # Initialize AI personality
            if DEBUG_AI:
                print("🧠 Initializing AI personality...")
            self.personality = PersonalityAI()

            # Initialize thermal printer for subtitle printing
            print("🖨️ Initializing thermal printer...")
            self.thermal_printer = create_thermal_printer(enabled=THERMAL_PRINTER_ENABLED)
            self.thermal_printer.start()

            # Initialize voice system (optional)
            if VOICE_ENABLED and VOICE_AVAILABLE:
                print("🔊 Initializing voice system...")
                
                if VOICE_ENGINE == "espeak":
                    # eSpeak TTS with whisper
                    try:
                        self.voice_system = VoiceSystem(
                            voice=ESPEAK_VOICE.split('+')[0],  # Base voice (e.g., "en-us")
                            speed=ESPEAK_SPEED,
                            pitch=ESPEAK_PITCH,
                            use_whisper='+whisper' in ESPEAK_VOICE
                        )
                        print(f"✅ eSpeak TTS ready (voice: {ESPEAK_VOICE}, {ESPEAK_SPEED} wpm)")
                        if VOICE_ALL_THOUGHTS:
                            print("   🎙️ Voice mode: EVERY thought")
                        else:
                            print(f"   🎙️ Voice mode: Every {VOICE_INTERVAL}s")
                    except Exception as e:
                        print(f"⚠️ eSpeak TTS disabled: {e}")
                        self.voice_system = None
                        
                elif VOICE_ENGINE == "windows":
                    # Windows TTS
                    self.voice_system = VoiceSystem()
                    if self.voice_system.start():
                        self.voice_system.set_rate(WINDOWS_TTS_RATE)
                        self.voice_system.set_volume(WINDOWS_TTS_VOLUME)
                        self.voice_system.set_voice_gender(WINDOWS_TTS_GENDER)
                        
                        print(f"✅ Windows TTS ready ({WINDOWS_TTS_GENDER}, {WINDOWS_TTS_RATE} wpm)")
                        if VOICE_ALL_THOUGHTS:
                            print("   🎙️ Voice mode: EVERY thought")
                        else:
                            print(f"   🎙️ Voice mode: Every {VOICE_INTERVAL}s")
                    else:
                        print("⚠️ Windows TTS disabled (not available)")
                        self.voice_system = None
                else:
                    # Piper TTS
                    self.voice_system = VoiceSystem(VOICE_MODEL)
                    if self.voice_system.start():
                        print(f"✅ Piper TTS ready (model: {VOICE_MODEL})")
                        if VOICE_ALL_THOUGHTS:
                            print("   🎙️ Voice mode: EVERY thought")
                        else:
                            print(f"   🎙️ Voice mode: Every {VOICE_INTERVAL}s")
                    else:
                        print("⚠️ Piper TTS disabled (not found)")
                        self.voice_system = None
            else:
                if VOICE_ENABLED:
                    print("🔇 Voice system disabled (not available)")
                else:
                    print("🔇 Voice system disabled (config)")

            # Initialize hand control
            if DEBUG_MOTOR:
                print("🤖 Initializing hand control...")
            self.hand_control = HandControlInterface()            # Launch hand control process (optional)
            # self.hand_control.launch_hand_controller(headless=True)
            
            print("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            if DEBUG_AI:
                print(traceback.format_exc())
            return False
    
    def run(self):
        """Main processing loop - single threaded, stable"""
        if not self.initialize():
            print("❌ Initialization failed - cannot start")
            return
        
        self.running = True
        print("🚀 Embodied AI v2 starting main loop...")
        
        try:
            # Direct VideoCapture using configured camera index
            print(f"🎥 Opening Camera {CAMERA_INDEX} (0=built-in, 1=external)...")
            cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"✅ Camera {CAMERA_INDEX} initialized: {actual_width}x{actual_height}")
            
            while self.running:
                # EXACT machine.py pattern: ret, frame = cap.read() every loop
                ret, frame = cap.read()
                if not ret:
                    continue
                
                current_time = time.time()
                self.frame_count += 1
                
                # AI processing in SEPARATE THREAD (EXACT machine.py pattern)
                if current_time - self.last_ai_process_time >= AI_PROCESS_INTERVAL:
                    # Only start new AI thread if previous one is complete
                    if self.ai_processing_lock.acquire(blocking=False):  # Non-blocking acquire
                        if DEBUG_AI:
                            print(f"🧠 Starting AI thread at frame {self.frame_count}")
                        
                        # Start daemon thread for AI processing (machine.py pattern)
                        ai_thread = threading.Thread(
                            target=self._ai_processing_thread,
                            args=(frame.copy(), current_time),
                            daemon=True
                        )
                        ai_thread.start()
                        self.last_ai_process_time = current_time
                    # Removed spammy AI processing messages
                
                # === DISPLAY OVERLAYS === (EXACT machine.py pattern)
                if SHOW_CAMERA_PREVIEW:
                    # Resize frame for preview (matching machine.py)
                    display_frame = cv2.resize(frame, (PREVIEW_WIDTH, PREVIEW_HEIGHT))
                    
                    # Apply live captioning subtitle system
                    if hasattr(self, 'current_subtitle') and self.current_subtitle:
                        display_frame = self._draw_live_caption_overlay(display_frame)
                    
                    # DISPLAY (EXACT machine.py pattern)
                    cv2.imshow("🤖 AI Inner Monologue", display_frame)
                    
                    # Key handling (machine.py pattern)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print("🛑 Quit key pressed")
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
            print("\n🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            if DEBUG_AI:
                print(traceback.format_exc())
        finally:
            # Clean up direct camera
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()
            self.shutdown()
    

    def _ai_processing_thread(self, frame, timestamp):
        """AI processing in separate thread (EXACT machine.py pattern)"""
        try:
            if DEBUG_AI:
                print(f"🧠 AI thread processing frame at {timestamp}")
            
            # Call AI (this is the slow blocking operation)
            # Simple consciousness processing
            response = self.personality.analyze_image(frame)
            
            if DEBUG_AI:
                if response:
                    print(f"🤖 AI processing complete - got response")
                else:
                    print(f"🤫 AI choosing silence - no response")
            
            if response:
                if DEBUG_AI:
                    print(f"🎯 AI returned response: {response[:100]}{'...' if len(response) > 100 else ''}")
                
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
                
                # Remove debug markers that might slip through
                clean_caption = re.sub(r'(🎯|🧹|🚫|🔄|✅|👁️|🧠|🎭|💭|🖨️|📝)', '', clean_caption)
                
                # Clean up extra whitespace
                clean_caption = ' '.join(clean_caption.split())
                clean_caption = clean_caption.strip()
                
                if DEBUG_AI:
                    print(f"🧹 Cleaned caption: {clean_caption[:100]}{'...' if len(clean_caption) > 100 else ''}")
                
                # Thread-safe live captioning subtitle update
                with self.subtitle_lock:
                    self.current_subtitle = clean_caption
                    
                    # Create sentence-based chunks (like live captioning)
                    self.subtitle_chunks = self._create_smart_chunks(clean_caption)
                    
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
                        
                        # Speak first chunk immediately if voice enabled (non-blocking)
                        if self.voice_system and VOICE_ALL_THOUGHTS:
                            if DEBUG_AI:
                                print(f"🎙️ Speaking chunk 0/{len(self.subtitle_chunks)-1}: {first_chunk[:50]}...")
                            self._speak_async(first_chunk, total_caption_words=total_words)
                
                # Show output with timestamp (clean, simple)
                timestamp_str = time.strftime("%H:%M:%S")
                print(f"\n[{timestamp_str}] 💭 {clean_caption}\n")

                # Send to thermal printer for rhythmic printing
                if self.thermal_printer:
                    if DEBUG_AI:
                        print(f"🖨️ Sending to thermal printer: {clean_caption[:50]}...")
                    self.thermal_printer.print_subtitle(clean_caption)
                else:
                    if DEBUG_AI:
                        print(f"❌ No thermal printer available")
        
        except Exception as e:
            if DEBUG_AI:
                print(f"AI thread error: {e}")
                print(traceback.format_exc())
        finally:
            # Always release the AI processing lock
            self.ai_processing_lock.release()
            if DEBUG_AI:
                print(f"🔓 AI processing lock released")
    
    def _speak_async(self, text, total_caption_words=None, caption_version=None):
        """Speak text in a separate thread to avoid blocking camera loop"""
        if not self.voice_system or not text:
            return
        
        def speak_worker():
            try:
                # BEFORE speaking, check if caption is still current (abort if new caption arrived)
                if caption_version is not None and caption_version != self.caption_version:
                    # Old caption - silently abort (new caption is more important)
                    return
                
                # If this is part of a verbose caption, speed up
                if total_caption_words and total_caption_words > 30:
                    # Save original speed
                    original_speed = self.voice_system.speed
                    # Speed up by 20% for long captions
                    self.voice_system.speed = int(original_speed * 1.2)
                    self.voice_system.speak(text)
                    # Restore original speed
                    self.voice_system.speed = original_speed
                else:
                    self.voice_system.speak(text)
            except Exception as e:
                if DEBUG_AI:
                    print(f"⚠️ TTS error: {e}")
        
        # Start speaking in background thread
        thread = threading.Thread(target=speak_worker, daemon=True)
        thread.start()
    
    def _create_smart_chunks(self, text):
        """Break text into sentence-based chunks for live captioning flow"""
        import re
        
        # Split into sentences using regex (more robust than simple punctuation)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for sentence in sentences:
            # Don't split sentences that are reasonable length (max ~10 words for comfortable reading)
            if len(sentence.split()) <= 10:
                chunks.append(sentence)
            else:
                # Split long sentences at natural breaks - use finditer to preserve text
                # Look for commas, semicolons, or conjunctions
                split_pattern = r'[,;]|\s+(?:and|but|or|so|yet|for)\s+'
                last_end = 0
                parts = []
                
                for match in re.finditer(split_pattern, sentence):
                    # Get text before the delimiter
                    part = sentence[last_end:match.start()].strip()
                    if part:
                        parts.append(part)
                    last_end = match.end()
                
                # Add remaining text after last delimiter
                if last_end < len(sentence):
                    part = sentence[last_end:].strip()
                    if part:
                        parts.append(part)
                
                # If we got parts, use them; otherwise keep whole sentence
                if parts:
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
                    # Just entered silence period
                    self.in_silence_period = True
                    self.silence_start_time = current_time
                    if DEBUG_CAMERA:
                        print(f"🔇 Entering silence period...")
                elif DEBUG_CAMERA:
                    # Show countdown timer (update in place)
                    silence_duration = current_time - self.silence_start_time
                    # No specific end time for silence, just show duration
                    print(f"\r🔇 Silence: {silence_duration:.1f}s", end="", flush=True)
                return frame  # Show blank space - silence is important
            
            # Check if it's time to advance to next chunk
            if (chunk_display_time >= self.chunk_display_duration and 
                self.current_chunk_index < len(self.subtitle_chunks) - 1):
                
                # Advance to next chunk
                self.current_chunk_index += 1
                self.last_chunk_change_time = current_time
                
                # Reset silence period when new content appears
                if self.in_silence_period:
                    self.in_silence_period = False
                    if DEBUG_CAMERA:
                        print()  # New line after silence timer
                
                # Calculate duration for new chunk (based on TTS)
                if self.current_chunk_index < len(self.subtitle_chunks):
                    chunk = self.subtitle_chunks[self.current_chunk_index]
                    word_count = len(chunk.split())
                    current_version = self.caption_version  # Capture current version
                    self.chunk_display_duration = self._calculate_tts_duration(word_count)
                    
                    # Speak this chunk if voice enabled (non-blocking)
                    if self.voice_system and VOICE_ALL_THOUGHTS:
                        if DEBUG_AI:
                            print(f"🎙️ Speaking chunk {self.current_chunk_index}/{len(self.subtitle_chunks)-1}: {chunk[:50]}...")
                        self._speak_async(chunk, caption_version=current_version)
                    
                    if DEBUG_CAMERA:
                        print(f"🎬 Next chunk: {word_count} words, {self.chunk_display_duration:.1f}s -> {chunk}")
            
            # Get current chunk to display (only if within 4-second window)
            current_chunk = self.subtitle_chunks[self.current_chunk_index]
        
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
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (int(overlay_x), int(overlay_y)), 
                     (int(overlay_x + overlay_width), int(overlay_y + overlay_height)), 
                     (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.3, overlay, 0.7, 0)  # More subtle transparency
        
        # Draw text lines
        for i, line in enumerate(lines):
            x_pos = int(text_positions[i][0])
            y_pos = int(overlay_y + padding + 16 + (i * line_height))
            
            # Draw text with subtle outline
            cv2.putText(frame, line, (x_pos + 1, y_pos + 1), font, font_scale, (0, 0, 0), font_thickness + 1)
            cv2.putText(frame, line, (x_pos, y_pos), font, font_scale, font_color, font_thickness)
        
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
                print(f"🤖 Motor updated: {hand_emotion} (mood: {mood_value:.2f})")
                
        except Exception as e:
            if DEBUG_MOTOR:
                print(f"Motor update error: {e}")
    
    
    def _print_status(self, current_time):
        """Print system status"""
        try:
            runtime = current_time - self.start_time
            fps = self.frame_count / runtime if runtime > 0 else 0
            
            # Get component status
            ai_status = self.personality.get_status() if self.personality else {}
            motor_status = self.hand_control.get_status() if self.hand_control else {}
            
            print(f"\n📊 Status (Runtime: {runtime:.1f}s, FPS: {fps:.1f}):")
            print(f"   🧠 AI: Mood={ai_status.get('mood', 0):.2f}, "
                  f"Beliefs={ai_status.get('beliefs', 0)}, "
                  f"Observations={ai_status.get('observations', 0)}")
            print(f"   🤖 Motor: {motor_status.get('current_emotion', 'unknown')}, "
                  f"Running={motor_status.get('is_running', False)}")
            
        except Exception as e:
            print(f"Status error: {e}")
    
    def shutdown(self):
        """Clean shutdown of all components"""
        print("🔄 Shutting down embodied AI...")
        self.running = False
        
        try:
            # Cleanup components
            if self.personality:
                self.personality.save_state()
                print("💾 AI state saved")
            
            if self.thermal_printer:
                self.thermal_printer.stop()
                print("🖨️ Thermal printer stopped")

            if self.voice_system:
                self.voice_system.stop()
                print("🔇 Voice system stopped")

            if self.hand_control:
                self.hand_control.cleanup()
                print("🤖 Hand control cleaned up")

            # Camera handled directly in main loop
            print("📷 Camera cleanup handled in main loop")
            
            print("✅ Shutdown complete")
            
        except Exception as e:
            print(f"⚠️ Shutdown error: {e}")


def main():
    """Main entry point"""
    print("🤖 Embodied AI v2 - Starting...")
    print(f"📋 Config: AI interval={AI_PROCESS_INTERVAL}s, Camera={CAMERA_WIDTH}x{CAMERA_HEIGHT}")
    
    # Create and run system
    ai_system = EmbodiedAI()
    ai_system.run()


if __name__ == "__main__":
    main()