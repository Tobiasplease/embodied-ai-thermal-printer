"""
eSpeak NG TTS with built-in whisper mode support
"""
import time
from typing import Optional
import logging

try:
    from espeakng import ESpeakNG
    ESPEAK_AVAILABLE = True
except ImportError:
    ESPEAK_AVAILABLE = False
    logging.warning("py-espeak-ng not installed")

class ESpeakTTS:
    """eSpeak NG text-to-speech with whisper support"""
    
    def __init__(
        self,
        voice: str = "en-us",
        speed: int = 150,  # Words per minute (default 175)
        pitch: int = 50,   # 0-99 (default 50)
        use_whisper: bool = False,
        volume: int = 100  # 0-200 (default 100)
    ):
        """
        Initialize eSpeak TTS
        
        Args:
            voice: Voice name (e.g., "en-us", "en-gb", "af" for female)
            speed: Words per minute (80-450, default 175)
            pitch: Pitch (0-99, default 50)
            use_whisper: Use whisper variant (+whisper)
            volume: Volume (0-200, default 100)
        """
        if not ESPEAK_AVAILABLE:
            raise RuntimeError("py-espeak-ng not installed. Run: pip install py-espeak-ng")
        
        self.speaker = ESpeakNG()
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
        self.use_whisper = use_whisper
        self.volume = volume
        
        # Apply settings
        self._update_voice()
        
        logging.info(f"✅ eSpeak TTS initialized: {voice}" + 
                    (" +whisper" if use_whisper else ""))
    
    def _update_voice(self):
        """Update voice settings"""
        # Set base voice
        voice_id = self.voice
        
        # Add whisper variant if enabled
        if self.use_whisper:
            voice_id = f"{self.voice}+whisper"
        
        self.speaker.voice = voice_id
        self.speaker.speed = self.speed
        self.speaker.pitch = self.pitch
        self.speaker.volume = self.volume
    
    def speak(self, text: str, use_whisper: Optional[bool] = None) -> bool:
        """
        Speak text using eSpeak
        
        Args:
            text: Text to speak
            use_whisper: Override instance whisper setting (optional)
        
        Returns:
            True if successful
        """
        if not text or not text.strip():
            return False
        
        try:
            # Temporarily override whisper if specified
            original_whisper = self.use_whisper
            if use_whisper is not None:
                self.use_whisper = use_whisper
                self._update_voice()
            
            # Speak the text
            self.speaker.say(text)
            
            # Restore original whisper setting
            if use_whisper is not None:
                self.use_whisper = original_whisper
                self._update_voice()
            
            return True
            
        except Exception as e:
            logging.error(f"eSpeak error: {e}")
            return False
    
    def set_whisper(self, enabled: bool):
        """Enable or disable whisper mode"""
        if self.use_whisper != enabled:
            self.use_whisper = enabled
            self._update_voice()
            logging.info(f"Whisper mode: {'enabled' if enabled else 'disabled'}")
    
    def set_voice(self, voice: str):
        """Change voice"""
        self.voice = voice
        self._update_voice()
        logging.info(f"Voice changed to: {voice}")
    
    def list_voices(self):
        """List available voices"""
        try:
            # Get voices from speaker instance
            return self.speaker.voices
        except Exception as e:
            logging.error(f"Error listing voices: {e}")
            return []


if __name__ == "__main__":
    # Test the eSpeak TTS
    print("\n🔊 Testing eSpeak TTS\n")
    
    if not ESPEAK_AVAILABLE:
        print("❌ py-espeak-ng not installed")
        print("Install with: pip install py-espeak-ng")
        exit(1)
    
    print("Available voices:")
    test_speaker = ESpeakNG()
    voices = test_speaker.voices if hasattr(test_speaker, 'voices') else []
    
    # Show available voices if any
    if voices:
        print(f"Found {len(voices)} voices")
        for v in list(voices)[:10]:
            print(f"  {v}")
    else:
        print("Voice list not available, but eSpeak is working")
    
    print("\n" + "="*60)
    print("Testing normal speech vs whisper mode")
    print("="*60 + "\n")
    
    # Test 1: Normal speech
    print("Test 1: Normal speech (en-us, speed 150)")
    tts = ESpeakTTS(voice="en-us", speed=150, use_whisper=False)
    tts.speak("Hello, this is normal eSpeak voice.")
    time.sleep(1)
    
    # Test 2: Whisper mode
    print("\nTest 2: WHISPER mode (en-us+whisper, speed 130)")
    tts.set_whisper(True)
    tts.set_voice("en-us")
    tts.speaker.speed = 130  # Slower for whisper
    tts.speak("Now I am whispering. This is the built-in whisper variant.")
    time.sleep(1)
    
    # Test 3: Female voice normal
    print("\nTest 3: Female voice normal (en-us+f2)")
    tts_female = ESpeakTTS(voice="en-us+f2", speed=150, use_whisper=False)
    tts_female.speak("This is a female voice variant.")
    time.sleep(1)
    
    # Test 4: Female whisper
    print("\nTest 4: Female WHISPER (en-us+f2+whisper)")
    tts_female.set_whisper(True)
    tts_female.speak("And now I am whispering with a female voice.")
    time.sleep(1)
    
    # Test 5: Toggle on the fly
    print("\nTest 5: Toggling whisper on and off")
    tts.set_whisper(False)
    tts.speak("Normal voice again")
    time.sleep(0.5)
    tts.set_whisper(True)
    tts.speak("Back to whispering")
    
    print("\n✅ All tests complete!")
    print("\nYou can use variants like:")
    print("  en-us+whisper   - Male whisper")
    print("  en-us+f2        - Female voice")
    print("  en-us+f2+whisper - Female whisper")
    print("  en-us+croak     - Croaky voice")
    print("  en-gb+whisper   - British whisper")
