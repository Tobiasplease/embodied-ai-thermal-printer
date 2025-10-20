"""
Simple eSpeak TTS using subprocess (works with any eSpeak installation)
"""
import subprocess
import os
import logging
from typing import Optional

class ESpeakTTS:
    """eSpeak NG text-to-speech with built-in whisper support"""
    
    def __init__(
        self,
        voice: str = "en-us",
        speed: int = 150,  # Words per minute
        pitch: int = 50,   # 0-99
        use_whisper: bool = False,
        espeak_path: Optional[str] = None
    ):
        """
        Initialize eSpeak TTS
        
        Args:
            voice: Voice name (e.g., "en-us", "en-gb", "en+f2" for female)
            speed: Words per minute (80-450, default 175)
            pitch: Pitch (0-99, default 50)
            use_whisper: Use built-in whisper variant (+whisper)
            espeak_path: Path to espeak-ng.exe (auto-detect if None)
        """
        # Find eSpeak executable
        if espeak_path and os.path.exists(espeak_path):
            self.espeak_path = espeak_path
        else:
            # Common installation paths
            common_paths = [
                r"C:\Program Files\eSpeak NG\espeak-ng.exe",
                r"C:\Program Files (x86)\eSpeak NG\espeak-ng.exe",
                r"espeak-ng.exe",  # If in PATH
                r"espeak.exe",  # Older version
            ]
            
            self.espeak_path = None
            for path in common_paths:
                if os.path.exists(path):
                    self.espeak_path = path
                    break
                elif path.endswith(".exe"):
                    # Try running it to see if it's in PATH
                    try:
                        subprocess.run([path, "--version"], 
                                      capture_output=True, 
                                      check=True,
                                      timeout=2)
                        self.espeak_path = path
                        break
                    except:
                        continue
        
        if not self.espeak_path:
            raise RuntimeError(
                "eSpeak NG not found!\n"
                "Download from: https://github.com/espeak-ng/espeak-ng/releases\n"
                "Or install via: winget install eSpeak-NG"
            )
        
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
        self.use_whisper = use_whisper
        
        logging.info(f"✅ eSpeak TTS initialized: {voice}" + 
                    (" +whisper" if use_whisper else ""))
        logging.info(f"   Using: {self.espeak_path}")
    
    def _get_voice_string(self) -> str:
        """Get the full voice string with variant"""
        voice_str = self.voice
        if self.use_whisper and "+whisper" not in voice_str:
            voice_str = f"{voice_str}+whisper"
        return voice_str
    
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
            # Determine which voice to use
            if use_whisper is not None:
                voice_str = self.voice + ("+whisper" if use_whisper else "")
            else:
                voice_str = self._get_voice_string()
            
            # Build command
            cmd = [
                self.espeak_path,
                "-v", voice_str,
                "-s", str(self.speed),
                "-p", str(self.pitch),
                text
            ]
            
            # Run eSpeak
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logging.error(f"eSpeak error: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"eSpeak error: {e}")
            return False
    
    def set_whisper(self, enabled: bool):
        """Enable or disable whisper mode"""
        self.use_whisper = enabled
        logging.info(f"Whisper mode: {'enabled' if enabled else 'disabled'}")
    
    def set_voice(self, voice: str):
        """Change voice"""
        self.voice = voice
        logging.info(f"Voice changed to: {voice}")
    
    def list_voices(self):
        """List available voices"""
        try:
            result = subprocess.run(
                [self.espeak_path, "--voices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout
        except Exception as e:
            logging.error(f"Error listing voices: {e}")
            return ""


if __name__ == "__main__":
    import time
    
    print("\n🔊 Testing eSpeak TTS with whisper mode\n")
    
    try:
        # Check if eSpeak is available
        print("Looking for eSpeak NG...")
        tts = ESpeakTTS(voice="en-us", speed=150, use_whisper=False)
        print(f"✅ Found eSpeak at: {tts.espeak_path}\n")
        
        # List voices
        print("="*60)
        print("Available voices:")
        print("="*60)
        voices = tts.list_voices()
        if voices:
            lines = voices.split('\n')[:15]  # First 15 lines
            for line in lines:
                print(line)
        print()
        
        print("="*60)
        print("Testing normal speech vs whisper mode")
        print("="*60 + "\n")
        
        # Test 1: Normal speech
        print("Test 1: Normal speech (en-us, speed 150)")
        tts.speak("Hello, this is normal eSpeak voice.")
        time.sleep(1)
        
        # Test 2: Whisper mode
        print("\nTest 2: WHISPER mode (en-us+whisper, speed 130)")
        tts.speed = 130
        tts.set_whisper(True)
        tts.speak("Now I am whispering. This is the built-in whisper variant.")
        time.sleep(1)
        
        # Test 3: Female voice normal
        print("\nTest 3: Female voice normal (en+f2)")
        tts_female = ESpeakTTS(voice="en+f2", speed=150, use_whisper=False)
        tts_female.speak("This is a female voice variant.")
        time.sleep(1)
        
        # Test 4: Female whisper
        print("\nTest 4: Female WHISPER (en+f2+whisper)")
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
        time.sleep(1)
        
        # Test 6: Croak variant
        print("\nTest 6: Bonus - CROAK variant (en-us+croak)")
        tts_croak = ESpeakTTS(voice="en-us+croak", speed=140, use_whisper=False)
        tts_croak.speak("This is the croaky voice variant.")
        
        print("\n✅ All tests complete!")
        print("\n💡 Available variants:")
        print("  +whisper   - Whispering (intimate, vulnerable)")
        print("  +croak     - Croaky voice (damaged, glitchy)")
        print("  +f1, +f2   - Female variants")
        print("  +m1, +m2   - Male variants")
        print("  Combine them: en+f2+whisper")
        
    except RuntimeError as e:
        print(f"❌ {e}")
        print("\nTo install eSpeak NG:")
        print("1. Download from: https://github.com/espeak-ng/espeak-ng/releases")
        print("2. Or use winget: winget install eSpeak-NG")
