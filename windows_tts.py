"""
Simple Windows TTS system - instant, no downloads needed
Classic robotic voice with full control over pitch, rate, volume
"""
import threading
import queue

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("⚠️ pyttsx3 not installed. Run: pip install pyttsx3")

DEBUG_VOICE = True

class WindowsTTS:
    """Classic Windows text-to-speech system"""
    
    def __init__(self):
        """Initialize Windows TTS engine"""
        self.engine = None
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.should_stop = False
        self.worker_thread = None
        
        # Voice parameters (adjustable!)
        self.rate = 150        # Words per minute (default ~200, range 0-400)
        self.volume = 0.9      # Volume 0.0-1.0
        self.voice_gender = "female"  # "male" or "female"
        
        if not PYTTSX3_AVAILABLE:
            print("❌ Windows TTS not available - install pyttsx3")
            return
        
        try:
            self.engine = pyttsx3.init()
            self._configure_voice()
            if DEBUG_VOICE:
                print("✅ Windows TTS initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Windows TTS: {e}")
            self.engine = None
    
    def _configure_voice(self):
        """Configure voice parameters"""
        if not self.engine:
            return
        
        # Set rate (speed)
        self.engine.setProperty('rate', self.rate)
        
        # Set volume
        self.engine.setProperty('volume', self.volume)
        
        # Try to set voice gender
        voices = self.engine.getProperty('voices')
        
        # Windows usually has David (male) and Zira (female)
        for voice in voices:
            if self.voice_gender == "female" and "zira" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
            elif self.voice_gender == "male" and "david" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        if DEBUG_VOICE:
            print(f"   Rate: {self.rate} wpm")
            print(f"   Volume: {self.volume}")
            print(f"   Voice: {self.voice_gender}")
    
    def set_rate(self, rate):
        """
        Set speech rate (words per minute)
        
        Args:
            rate: 0-400, typical range:
                  100 = very slow
                  150 = slow/measured
                  200 = normal
                  250 = fast
                  300 = very fast
        """
        self.rate = max(50, min(400, rate))
        if self.engine:
            self.engine.setProperty('rate', self.rate)
        if DEBUG_VOICE:
            print(f"⏱️ Speech rate: {self.rate} wpm")
    
    def set_volume(self, volume):
        """
        Set volume level
        
        Args:
            volume: 0.0 (silent) to 1.0 (max)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty('volume', self.volume)
        if DEBUG_VOICE:
            print(f"🔊 Volume: {int(self.volume * 100)}%")
    
    def set_voice_gender(self, gender):
        """
        Set voice gender
        
        Args:
            gender: "male" or "female"
        """
        self.voice_gender = gender
        self._configure_voice()
        if DEBUG_VOICE:
            print(f"🎭 Voice gender: {gender}")
    
    def start(self):
        """Start the voice worker thread"""
        if not self.engine:
            return False
        
        self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)
        self.worker_thread.start()
        
        if DEBUG_VOICE:
            print("🔊 Windows TTS started")
        return True
    
    def speak(self, text, priority=False):
        """
        Queue text for speech output
        
        Args:
            text: Text to speak
            priority: If True, clear queue and speak immediately
        """
        if not self.engine:
            return
        
        # Clean text
        text = self._clean_for_speech(text)
        
        if priority:
            # Clear queue for urgent speech
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
            # Stop current speech
            if self.is_speaking:
                self.engine.stop()
        
        self.speech_queue.put(text)
        
        if DEBUG_VOICE:
            queue_size = self.speech_queue.qsize()
            print(f"🎙️ Queued: {text[:50]}... (queue: {queue_size})")
    
    def _clean_for_speech(self, text):
        """Clean text for speech output"""
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
                # Get text from queue (blocking with timeout)
                text = self.speech_queue.get(timeout=0.5)
                
                if text:
                    self._synthesize_and_play(text)
                    
            except queue.Empty:
                continue
            except Exception as e:
                if DEBUG_VOICE:
                    print(f"❌ Voice worker error: {e}")
    
    def _synthesize_and_play(self, text):
        """Synthesize and play speech"""
        self.is_speaking = True
        
        try:
            if DEBUG_VOICE:
                print(f"🤖 Speaking: {text[:60]}...")
            
            # Windows TTS speaks synchronously
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            if DEBUG_VOICE:
                print(f"❌ Speech error: {e}")
        finally:
            self.is_speaking = False
    
    def stop(self):
        """Stop the voice system"""
        self.should_stop = True
        if self.engine:
            self.engine.stop()
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        
        if DEBUG_VOICE:
            print("🔇 Windows TTS stopped")
    
    def clear_queue(self):
        """Clear all pending speech"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break


# Test function
if __name__ == "__main__":
    import time
    
    print("Testing Windows TTS...")
    print()
    
    if not PYTTSX3_AVAILABLE:
        print("❌ Please install pyttsx3:")
        print("   pip install pyttsx3")
        exit(1)
    
    tts = WindowsTTS()
    
    if tts.start():
        # Test different rates
        print("Test 1: Different speeds")
        
        tts.set_rate(100)
        tts.speak("Very slow speech. Each word is deliberate.")
        time.sleep(5)
        
        tts.set_rate(200)
        tts.speak("Normal speed speech. This is the default.")
        time.sleep(4)
        
        tts.set_rate(300)
        tts.speak("Fast speech. Words come quickly now.")
        time.sleep(3)
        
        print()
        print("Test 2: Volume control")
        
        tts.set_rate(150)
        tts.set_volume(0.5)
        tts.speak("Quieter voice. Half volume.")
        time.sleep(3)
        
        tts.set_volume(1.0)
        tts.speak("Full volume. Maximum loudness.")
        time.sleep(3)
        
        print()
        print("Test 3: Gender switching")
        
        tts.set_voice_gender("male")
        tts.speak("Male voice. David speaking.")
        time.sleep(3)
        
        tts.set_voice_gender("female")
        tts.speak("Female voice. Zira speaking.")
        time.sleep(3)
        
        print()
        print("⏳ Waiting for speech to complete...")
        time.sleep(5)
        
        tts.stop()
        
        print()
        print("✅ Test complete!")
        print()
        print("Classic robotic Windows TTS - instant and controllable!")
    else:
        print("❌ Windows TTS not available")
