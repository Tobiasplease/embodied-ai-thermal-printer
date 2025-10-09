"""
Clean camera interface with live subtitle overlay capability
"""
import cv2
import numpy as np
import time
import textwrap
from collections import deque
from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, DEBUG_CAMERA


class Camera:
    """Camera interface with live subtitle overlay for AI inner monologue"""
    
    def __init__(self, show_preview=True, preview_width=800, preview_height=600):
        self.cap = None
        self.is_open = False
        self.show_preview = show_preview
        self.preview_width = preview_width
        self.preview_height = preview_height
        
        # Enhanced subtitle system for AI inner monologue
        self.subtitle_queue = deque(maxlen=15)  # Keep more captions for better flow
        self.current_subtitle = ""
        self.subtitle_start_time = 0
        
        # Live captioning-style timing system
        self.speaking_speed = 3.0    # Words per second (natural speech pace)
        self.min_duration = 1.5      # Minimum time to show any caption
        self.max_duration = 4.0      # Maximum time for long sentences
        self.pause_between_chunks = 0.8  # Brief pause between sentences
        
        self.last_caption_time = 0
        self.min_caption_interval = 0.5  # Allow rapid updates like live captions
        
        # Sentence-based chunking for live caption feel
        self.max_words_per_chunk = 8   # 1-2 sentences max (like live captions)
        self.current_text_parts = []   # For cycling through sentences
        self.current_part_index = 0
        self.chunk_start_time = 0      # For managing inter-chunk timing
        
        # Text formatting settings (matching your reference image)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6  # Slightly smaller for better fit
        self.font_color = (0, 255, 255)  # Yellow text (BGR format: Blue=0, Green=255, Red=255)
        self.font_thickness = 1  # Thinner text for cleaner look
        self.bg_color = (0, 0, 0)  # Black background
        self.bg_alpha = 0.8  # More opaque background like in reference
        self.line_height = 25  # Tighter line spacing
        self.max_chars_per_line = 60  # More characters per line for natural flow
        
    def start(self):
        """Initialize camera with error handling"""
        try:
            # Try DirectShow first (Windows), fallback to default
            self.cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
            
            if not self.cap.isOpened():
                if DEBUG_CAMERA:
                    print("DirectShow failed, trying default backend...")
                self.cap = cv2.VideoCapture(CAMERA_INDEX)
            
            if not self.cap.isOpened():
                raise Exception(f"Could not open camera {CAMERA_INDEX}")
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            # Verify settings
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            if DEBUG_CAMERA:
                print(f"Camera initialized: {actual_width}x{actual_height}")
            
            self.is_open = True
            return True
            
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False
    
    def get_frame(self):
        """Get current frame from camera"""
        if not self.is_open or not self.cap:
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            if DEBUG_CAMERA:
                print("Failed to capture frame")
            return None
    
    def test_frame(self):
        """Get a frame and return basic statistics for debugging"""
        frame = self.get_frame()
        if frame is not None:
            return {
                'shape': frame.shape,
                'min': frame.min(),
                'max': frame.max(),
                'mean': round(frame.mean(), 2),
                'status': 'OK'
            }
        else:
            return {'status': 'FAILED'}
    
    def add_subtitle(self, caption_text):
        """Add a new caption with intelligent chunking and dynamic timing"""
        current_time = time.time()
        
        # Rate limiting - don't accept captions too frequently
        if current_time - self.last_caption_time < self.min_caption_interval:
            if DEBUG_CAMERA:
                print(f"Caption ignored - too soon (need {self.min_caption_interval:.1f}s interval)")
            return False
        
        # Clean and format the caption
        clean_caption = self._format_caption(caption_text)
        if not clean_caption:
            return False
        
        # Smart text chunking for better readability
        text_chunks = self._create_smart_chunks(clean_caption)
        
        # Add each chunk to the queue with calculated duration
        for chunk in text_chunks:
            duration = self._calculate_dynamic_duration(chunk)
            self.subtitle_queue.append({
                'text': chunk,
                'timestamp': current_time,
                'duration': duration,
                'lines': self._wrap_text(chunk)
            })
        
        # Start showing the first chunk immediately
        if text_chunks and not self.current_subtitle:
            first_chunk = self.subtitle_queue[-len(text_chunks)]  # Get first added chunk
            self.current_subtitle = first_chunk['text']
            self.subtitle_start_time = current_time
            first_chunk['duration'] = self._calculate_dynamic_duration(first_chunk['text'])
            
        self.last_caption_time = current_time
        
        if DEBUG_CAMERA:
            chunk_count = len(text_chunks)
            total_words = len(clean_caption.split())
            print(f"💭 New subtitle: {chunk_count} chunks, {total_words} words -> {clean_caption[:40]}...")
        
        return True
    
    def _format_caption(self, text):
        """Clean and format caption text for subtitle display"""
        if not text:
            return ""
        
        # Remove common prefixes and timestamps
        prefixes_to_remove = ["[16:", "[15:", "[17:", "[18:", "[19:", "[20:", "[21:", "[22:", "[23:", "[00:", "[01:", "[02:", "[03:", "[04:", "[05:", "[06:", "[07:", "[08:", "[09:", "[10:", "[11:", "[12:", "[13:", "[14:"]
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                # Find the closing bracket and remove timestamp
                end_pos = text.find(']')
                if end_pos != -1:
                    text = text[end_pos + 1:].strip()
                break
        
        text = text.strip()
        if text.lower().startswith("caption:"):
            text = text[8:].strip()
        
        # Don't hard limit - let smart chunking handle long text
        return text
    
    def _create_smart_chunks(self, text):
        """Create sentence-based chunks like live captioning systems"""
        import re
        
        # First, split into sentences using regex for better sentence detection
        sentence_endings = r'[.!?]+(?:\s|$|\.\.\.)'
        sentences = re.split(sentence_endings, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If no clear sentences, fall back to punctuation splitting
        if len(sentences) <= 1:
            # Split on commas, semicolons, or natural pauses
            pause_markers = r'[,;—]+\s+'
            sentences = re.split(pause_markers, text)
            sentences = [s.strip() for s in sentences if s.strip()]
        
        # If still no good splits, create word-count based chunks
        if len(sentences) <= 1:
            words = text.split()
            sentences = []
            for i in range(0, len(words), self.max_words_per_chunk):
                chunk = ' '.join(words[i:i + self.max_words_per_chunk])
                sentences.append(chunk)
        
        # Further split any sentences that are too long (more than max_words_per_chunk)
        final_chunks = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) <= self.max_words_per_chunk:
                final_chunks.append(sentence)
            else:
                # Split long sentences into smaller chunks at natural breaks
                for i in range(0, len(words), self.max_words_per_chunk):
                    chunk = ' '.join(words[i:i + self.max_words_per_chunk])
                    final_chunks.append(chunk)
        
        return [chunk for chunk in final_chunks if chunk.strip()]
    
    def _calculate_dynamic_duration(self, text):
        """Calculate display duration like live captioning - based on natural speech timing"""
        word_count = len(text.split())
        
        # Base calculation using natural speaking speed
        base_time = word_count / self.speaking_speed
        
        # Add processing time for complex punctuation (pauses in speech)
        punctuation_weight = text.count(',') * 0.3 + text.count('.') * 0.5 + text.count('?') * 0.4 + text.count('!') * 0.4
        
        # Add slight pause for sentence endings
        if text.strip().endswith(('.', '!', '?')):
            base_time += 0.5
        
        # Apply realistic constraints
        duration = max(self.min_duration, min(self.max_duration, base_time + punctuation_weight))
        
        return duration

    def _draw_subtitle_with_pause_indicator(self, frame, duration, elapsed_time):
        """Draw subtitle with pause indicator during inter-chunk pauses"""
        if not self.current_subtitle:
            return frame
        
        # Get text lines and draw the main subtitle first
        lines = self._wrap_text(self.current_subtitle)
        if not lines:
            return frame
        
        # Calculate overlay position (bottom of frame)
        frame_height, frame_width = frame.shape[:2]
        overlay_height = len(lines) * self.line_height + 20  # 20px padding
        overlay_y = frame_height - overlay_height
        
        # Create semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, overlay_y), (frame_width, frame_height), self.bg_color, -1)
        frame = cv2.addWeighted(frame, 1 - self.bg_alpha, overlay, self.bg_alpha, 0)
        
        # Draw text lines
        for i, line in enumerate(lines):
            y_pos = overlay_y + 30 + (i * self.line_height)
            
            # Center text horizontally
            text_size = cv2.getTextSize(line, self.font, self.font_scale, self.font_thickness)[0]
            x_pos = (frame_width - text_size[0]) // 2
            
            # Draw text with outline for better readability
            cv2.putText(frame, line, (x_pos + 1, y_pos + 1), self.font, 
                       self.font_scale, (0, 0, 0), self.font_thickness + 1)  # Black outline
            cv2.putText(frame, line, (x_pos, y_pos), self.font, 
                       self.font_scale, self.font_color, self.font_thickness)  # White text
        
        # Add small pause dots to indicate "continuing..." like live captions
        if int(elapsed_time * 2) % 2:  # Blink effect
            dots_text = "..."
            text_size = cv2.getTextSize(dots_text, self.font, self.font_scale * 0.8, 1)[0]
            x_pos = frame_width - text_size[0] - 20
            y_pos = frame_height - 15
            cv2.putText(frame, dots_text, (x_pos, y_pos), self.font, self.font_scale * 0.8, 
                       (100, 100, 100), 1, cv2.LINE_AA)  # Gray dots
        
        return frame



    def _wrap_text(self, text):
        """Wrap text to multiple lines for subtitle display"""
        return textwrap.wrap(text, width=self.max_chars_per_line)
    
    def _draw_subtitle_overlay(self, frame):
        """Draw subtitle overlay on frame with dynamic timing"""
        if not self.current_subtitle:
            return frame
        
        current_time = time.time()
        
        # Get current subtitle's dynamic duration
        current_duration = self.max_duration  # fallback
        if self.subtitle_queue:
            current_sub = self.subtitle_queue[0]
            current_duration = current_sub.get('duration', self.max_duration)
        
        # Check if current subtitle should expire (with organic pause between chunks)
        time_since_start = current_time - self.subtitle_start_time
        
        if time_since_start > current_duration:
            # Add organic pause between chunks if there are more in queue
            if len(self.subtitle_queue) > 1:
                # Check if we've had enough pause time between chunks
                pause_needed = self.pause_between_chunks
                if time_since_start < current_duration + pause_needed:
                    # Still in pause period, keep showing current subtitle
                    return self._draw_subtitle_with_pause_indicator(frame, current_duration, time_since_start)
                
                # Pause period complete, move to next chunk
                self.subtitle_queue.popleft()
                if self.subtitle_queue:
                    next_subtitle = self.subtitle_queue[0]
                    self.current_subtitle = next_subtitle['text']
                    self.subtitle_start_time = current_time
                    if DEBUG_CAMERA:
                        next_duration = next_subtitle.get('duration', self.max_duration)
                        word_count = len(next_subtitle['text'].split())
                        print(f"🎬 Next chunk: {word_count} words, {next_duration:.1f}s -> {next_subtitle['text']}")
            else:
                # No more chunks, clear subtitle after brief pause
                if time_since_start > current_duration + 0.5:  # Brief final pause
                    self.current_subtitle = ""
                    return frame
        
        if not self.current_subtitle:
            return frame
        
        # Get text lines
        lines = self._wrap_text(self.current_subtitle)
        if not lines:
            return frame
        
        # Calculate overlay position (bottom of frame)
        frame_height, frame_width = frame.shape[:2]
        overlay_height = len(lines) * self.line_height + 20  # 20px padding
        overlay_y = frame_height - overlay_height
        
        # Create semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, overlay_y), (frame_width, frame_height), self.bg_color, -1)
        frame = cv2.addWeighted(frame, 1 - self.bg_alpha, overlay, self.bg_alpha, 0)
        
        # Draw text lines
        for i, line in enumerate(lines):
            y_pos = overlay_y + 30 + (i * self.line_height)
            
            # Center text horizontally
            text_size = cv2.getTextSize(line, self.font, self.font_scale, self.font_thickness)[0]
            x_pos = (frame_width - text_size[0]) // 2
            
            # Draw text with outline for better readability
            cv2.putText(frame, line, (x_pos + 1, y_pos + 1), self.font, 
                       self.font_scale, (0, 0, 0), self.font_thickness + 1)  # Black outline
            cv2.putText(frame, line, (x_pos, y_pos), self.font, 
                       self.font_scale, self.font_color, self.font_thickness)  # White text
        
        return frame
    
    def get_frame_with_overlay(self):
        """Get frame with subtitle overlay applied"""
        frame = self.get_frame()
        if frame is None or not self.show_preview:
            return frame
        
        # Resize frame for preview window
        if frame.shape[1] != self.preview_width or frame.shape[0] != self.preview_height:
            frame = cv2.resize(frame, (self.preview_width, self.preview_height))
        
        # Apply subtitle overlay
        frame = self._draw_subtitle_overlay(frame)
        
        return frame
    
    def show_frame_with_subtitles(self, window_name="AI Inner Monologue"):
        """Display frame with subtitles in a window"""
        if not self.show_preview:
            return False
        
        frame = self.get_frame_with_overlay()
        if frame is None:
            return False
        
        cv2.imshow(window_name, frame)
        return True
    
    def get_subtitle_status(self):
        """Get current subtitle system status with dynamic timing"""
        # Get current subtitle's dynamic duration
        current_duration = self.max_duration  # fallback
        if self.subtitle_queue and self.current_subtitle:
            current_sub = self.subtitle_queue[0]
            current_duration = current_sub.get('duration', self.max_duration)
        
        return {
            'current_subtitle': self.current_subtitle[:50] + "..." if len(self.current_subtitle) > 50 else self.current_subtitle,
            'queue_length': len(self.subtitle_queue),
            'time_remaining': max(0, current_duration - (time.time() - self.subtitle_start_time)) if self.current_subtitle else 0,
            'current_duration': current_duration if self.current_subtitle else 0,
            'last_caption_time': self.last_caption_time,
            'words_per_second': self.speaking_speed
        }
    
    def stop(self):
        """Clean camera shutdown"""
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()  # Close any preview windows
            self.is_open = False
            if DEBUG_CAMERA:
                print("Camera stopped")


def test_camera():
    """Standalone camera test"""
    print("Testing camera...")
    cam = Camera()
    
    if cam.start():
        print("✓ Camera started successfully")
        
        # Test frame capture
        stats = cam.test_frame()
        print(f"✓ Frame test: {stats}")
        
        # Test a few frames
        for i in range(3):
            frame = cam.get_frame()
            if frame is not None:
                print(f"✓ Frame {i+1}: {frame.shape}")
            else:
                print(f"✗ Frame {i+1}: Failed")
        
        cam.stop()
        print("✓ Camera stopped")
        return True
    else:
        print("✗ Camera failed to start")
        return False


if __name__ == "__main__":
    test_camera()