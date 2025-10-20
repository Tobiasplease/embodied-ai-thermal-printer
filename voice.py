"""
Lightweight TTS system for embodied AI voice output
Uses Piper TTS for fast, local text-to-speech
"""

import os
import subprocess
import tempfile
import threading
import queue
import time
from pathlib import Path

# Debug flag
DEBUG_VOICE = True

class VoiceSystem:
    """Manages text-to-speech output for AI consciousness"""
    
    def __init__(self, voice_model="en_US-lessac-medium"):
        """
        Initialize voice system
        
        Args:
            voice_model: Piper voice model to use
                Options: 
                - en_US-lessac-medium (female, clear)
                - en_US-ryan-high (male, expressive)
                - en_US-amy-medium (female, natural)
        """
        self.voice_model = voice_model
        self.piper_exe = None
        self.model_path = None
        
        # Speech queue for async processing
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.should_stop = False
        
        # Voice style settings
        self.whisper_mode = False
        self.speech_rate = 1.0  # 1.0 = normal, 0.5 = 2x faster, 2.0 = 2x slower
        
        # Worker thread
        self.worker_thread = None
        
        # Check if Piper is available
        self._check_piper_installation()
        
    def _check_piper_installation(self):
        """Check if Piper TTS is installed and available"""
        # Check common installation paths
        possible_paths = [
            Path("piper/piper.exe"),  # Local install
            Path("C:/Program Files/piper/piper.exe"),
            Path.home() / "piper" / "piper.exe"
        ]
        
        for path in possible_paths:
            if path.exists():
                self.piper_exe = str(path)
                if DEBUG_VOICE:
                    print(f"✅ Found Piper at: {self.piper_exe}")
                break
        
        if not self.piper_exe:
            print("⚠️ Piper TTS not found. Voice will be disabled.")
            print("   Download from: https://github.com/rhasspy/piper/releases")
            print("   Extract to './piper/' directory")
            return False
        
        # Check for model file
        model_dir = Path(self.piper_exe).parent / "models"
        model_file = model_dir / f"{self.voice_model}.onnx"
        
        if model_file.exists():
            self.model_path = str(model_file)
            if DEBUG_VOICE:
                print(f"✅ Found voice model: {self.voice_model}")
        else:
            print(f"⚠️ Voice model not found: {model_file}")
            print(f"   Download {self.voice_model}.onnx and .json to {model_dir}")
            return False
        
        return True
    
    def start(self):
        """Start the voice worker thread"""
        if not self.piper_exe or not self.model_path:
            if DEBUG_VOICE:
                print("🔇 Voice system disabled (Piper not available)")
            return False
        
        self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)
        self.worker_thread.start()
        
        if DEBUG_VOICE:
            print("🔊 Voice system started")
        return True
    
    def set_whisper_mode(self, enabled=True):
        """Enable or disable whisper mode"""
        self.whisper_mode = enabled
        if DEBUG_VOICE:
            print(f"🤫 Whisper mode: {'ON' if enabled else 'OFF'}")
    
    def set_speech_rate(self, rate=1.0):
        """
        Set speech rate
        
        Args:
            rate: Speech speed multiplier (1.0 = normal, 0.5 = 2x faster, 2.0 = 2x slower)
        """
        self.speech_rate = max(0.5, min(2.0, rate))  # Clamp between 0.5 and 2.0
        if DEBUG_VOICE:
            print(f"⏱️ Speech rate set to: {self.speech_rate}x")
    
    def speak(self, text, priority=False, whisper=None):
        """
        Queue text for speech output
        
        Args:
            text: Text to speak
            priority: If True, clear queue and speak immediately
            whisper: Override whisper mode for this speech (True/False/None)
        """
        if not self.piper_exe:
            return
        
        # Clean text for speech
        text = self._clean_for_speech(text)
        
        # Determine whisper mode for this speech
        use_whisper = whisper if whisper is not None else self.whisper_mode
        
        if priority:
            # Clear queue for urgent speech
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
        
        self.speech_queue.put((text, use_whisper))
        
        if DEBUG_VOICE:
            queue_size = self.speech_queue.qsize()
            print(f"🎙️ Queued speech: {text[:50]}... (queue: {queue_size})")
    
    def _clean_for_speech(self, text):
        """Clean text for natural speech output"""
        import re
        
        # Remove timestamps
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)
        
        # Remove emoji and special characters
        text = re.sub(r'[🎯🧹🚫🔄✅👁️🧠🎭💭🖨️📝]', '', text)
        
        # Remove debug markers
        text = re.sub(r'\[(?:DEBUG|System|Tone)[^\]]*\]', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _voice_worker(self):
        """Worker thread that processes speech queue"""
        while not self.should_stop:
            try:
                # Get text and whisper flag from queue (blocking with timeout)
                item = self.speech_queue.get(timeout=0.5)
                
                if item:
                    # Unpack tuple (text, whisper_mode)
                    if isinstance(item, tuple):
                        text, use_whisper = item
                    else:
                        # Backwards compatibility
                        text = item
                        use_whisper = self.whisper_mode
                    
                    self._synthesize_and_play(text, use_whisper)
                    
            except queue.Empty:
                continue
            except Exception as e:
                if DEBUG_VOICE:
                    print(f"❌ Voice worker error: {e}")
    
    def _synthesize_and_play(self, text, use_whisper=False):
        """Synthesize speech and play it"""
        self.is_speaking = True
        
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                wav_path = temp_file.name
            
            # Configure Piper parameters based on mode
            if use_whisper:
                # Whisper settings: breathier, slower, more variation
                noise_scale = 0.9      # Higher = breathier, more air sound
                length_scale = 1.3     # Slower, more deliberate
                noise_w = 1.0          # More phoneme variation
            else:
                # Normal speech settings
                noise_scale = 0.667    # Default
                length_scale = self.speech_rate  # Use configured rate
                noise_w = 0.8          # Default
            
            # Run Piper to generate speech
            cmd = [
                self.piper_exe,
                "--model", self.model_path,
                "--output_file", wav_path,
                "--noise_scale", str(noise_scale),
                "--length_scale", str(length_scale),
                "--noise_w", str(noise_w),
                "--sentence_silence", "0.3"  # Slightly longer pauses
            ]
            
            if DEBUG_VOICE:
                mode_indicator = "🤫" if use_whisper else "🎤"
                print(f"{mode_indicator} Synthesizing: {text[:60]}...")
            
            # Send text to Piper via stdin
            result = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Play the audio file with volume adjustment
                self._play_audio(wav_path, whisper=use_whisper)
            else:
                if DEBUG_VOICE:
                    print(f"❌ Piper synthesis failed: {result.stderr.decode()}")
            
            # Clean up temp file
            try:
                os.unlink(wav_path)
            except:
                pass
                
        except Exception as e:
            if DEBUG_VOICE:
                print(f"❌ Speech synthesis error: {e}")
        finally:
            self.is_speaking = False
    
    def _play_audio(self, wav_path, whisper=False):
        """Play audio file using Windows sound with optional volume adjustment"""
        try:
            # For whisper mode, we could reduce system volume, but that affects everything
            # Instead, we'll rely on the synthesis parameters to create a quieter effect
            # The breathier sound naturally sounds quieter
            
            import winsound
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
            
        except ImportError:
            # Fallback to command line player
            try:
                subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync()'], 
                             check=True, capture_output=True, timeout=30)
            except:
                if DEBUG_VOICE:
                    print("❌ Could not play audio")
    
    def stop(self):
        """Stop the voice system"""
        self.should_stop = True
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        
        if DEBUG_VOICE:
            print("🔇 Voice system stopped")
    
    def clear_queue(self):
        """Clear all pending speech"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break


# Test function
if __name__ == "__main__":
    print("Testing Voice System...")
    
    voice = VoiceSystem()
    
    if voice.start():
        # Test speech
        voice.speak("Hello, I am the embodied AI. I can see through the camera and speak my thoughts.")
        
        time.sleep(2)
        
        voice.speak("This is a test of the text to speech system.")
        
        # Wait for speech to finish
        time.sleep(10)
        
        voice.stop()
    else:
        print("Voice system not available. Install Piper TTS first.")
