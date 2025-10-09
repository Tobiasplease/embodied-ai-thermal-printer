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
from config import (
    AI_PROCESS_INTERVAL, DEBUG_CAMERA, DEBUG_AI, DEBUG_MOTOR, 
    VERBOSE_OUTPUT, CAMERA_WIDTH, CAMERA_HEIGHT, SHOW_CAMERA_PREVIEW,
    PREVIEW_WIDTH, PREVIEW_HEIGHT
)


class EmbodiedAI:
    """Main embodied AI system - clean single-threaded design"""
    
    def __init__(self):
        self.running = False
        self.camera = None
        self.personality = None
        self.hand_control = None
        
        # Timing controls - avoid threading issues
        self.last_ai_process_time = 0
        self.last_motor_update_time = 0
        self.last_status_time = 0
        
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
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        if VERBOSE_OUTPUT:
            print("🤖 Embodied AI v2 initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Shutdown signal received ({signum})")
        self.shutdown()
        sys.exit(0)
    
    def initialize(self):
        """Initialize all components"""
        try:
            # Skip Camera class initialization - we'll use direct cv2 access
            if DEBUG_CAMERA:
                print("📷 Will initialize camera directly in main loop...")
            self.camera = None  # Don't use Camera class to avoid threading issues
            
            # Initialize AI personality
            if DEBUG_AI:
                print("🧠 Initializing AI personality...")
            self.personality = PersonalityAI()
            
            # Initialize hand control
            if DEBUG_MOTOR:
                print("🤖 Initializing hand control...")
            self.hand_control = HandControlInterface()
            
            # Launch hand control process (optional)
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
            # EXACT machine.py camera pattern - direct VideoCapture
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            while self.running:
                # EXACT machine.py pattern: ret, frame = cap.read() every loop
                ret, frame = cap.read()
                if not ret:
                    continue
                
                current_time = time.time()
                self.frame_count += 1
                
                # AI processing in SEPARATE THREAD (EXACT machine.py pattern)
                if current_time - self.last_ai_process_time >= AI_PROCESS_INTERVAL:
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
            response = self.personality.analyze_image(frame)
            
            if response:
                # Clean caption (no truncation!)
                clean_caption = response.strip()
                if clean_caption.lower().startswith("caption:"):
                    clean_caption = clean_caption[len("caption:"):].strip()
                
                # Thread-safe live captioning subtitle update
                with self.subtitle_lock:
                    self.current_subtitle = clean_caption
                    
                    # Create sentence-based chunks (like live captioning)
                    self.subtitle_chunks = self._create_smart_chunks(clean_caption)
                    
                    # Reset to first chunk
                    self.current_chunk_index = 0
                    self.subtitle_start_time = time.time()
                    self.last_chunk_change_time = time.time()
                    
                    # Calculate dynamic duration for first chunk
                    if self.subtitle_chunks:
                        first_chunk = self.subtitle_chunks[0]
                        word_count = len(first_chunk.split())
                        self.chunk_display_duration = self._calculate_chunk_duration(word_count)
                
                # Show output with timestamp
                timestamp_str = time.strftime("%H:%M:%S")
                print(f"[{timestamp_str}] {clean_caption}")
                
                if self.subtitle_chunks:
                    chunk_count = len(self.subtitle_chunks)
                    word_count = len(clean_caption.split())
                    print(f"[{timestamp_str}] 💭 New thought cycling through {chunk_count} chunks...")
        
        except Exception as e:
            if DEBUG_AI:
                print(f"AI thread error: {e}")
                print(traceback.format_exc())
    
    def _create_smart_chunks(self, text):
        """Break text into sentence-based chunks for live captioning flow"""
        import re
        
        # Split into sentences using regex (more robust than simple punctuation)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for sentence in sentences:
            # Don't split sentences that are reasonable length (max ~8 words)
            if len(sentence.split()) <= 8:
                chunks.append(sentence)
            else:
                # Split long sentences at natural breaks (commas, conjunctions)
                parts = re.split(r'[,;]|\s+(?:and|but|or|so|yet|for)\s+', sentence)
                for part in parts:
                    if part.strip():
                        chunks.append(part.strip())
        
        return chunks
    
    def _calculate_chunk_duration(self, word_count):
        """Calculate how long to show a chunk based on natural speech speed"""
        speaking_speed = 3.0  # words per second (natural speech)
        min_duration = 1.5
        max_duration = 4.0
        
        base_time = word_count / speaking_speed
        return max(min_duration, min(max_duration, base_time))
    
    def _draw_live_caption_overlay(self, frame):
        """Draw live captioning-style overlay with organic chunk progression and 4-second max display"""
        current_time = time.time()
        
        with self.subtitle_lock:
            if not self.subtitle_chunks or self.current_chunk_index >= len(self.subtitle_chunks):
                return frame
            
            # Calculate how long current chunk has been displayed
            chunk_display_time = current_time - self.last_chunk_change_time
            
            # Hide chunk after 4 seconds maximum (important silence periods)
            if chunk_display_time >= 4.0:
                if DEBUG_CAMERA:
                    print(f"🔇 Chunk hidden after 4s - entering silence period")
                return frame  # Show blank space - silence is important
            
            # Check if it's time to advance to next chunk (but only if we haven't hit 4-second limit)
            if (chunk_display_time >= self.chunk_display_duration and 
                self.current_chunk_index < len(self.subtitle_chunks) - 1):
                
                # Advance to next chunk
                self.current_chunk_index += 1
                self.last_chunk_change_time = current_time
                
                # Calculate duration for new chunk
                if self.current_chunk_index < len(self.subtitle_chunks):
                    chunk = self.subtitle_chunks[self.current_chunk_index]
                    word_count = len(chunk.split())
                    self.chunk_display_duration = self._calculate_chunk_duration(word_count)
                    
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