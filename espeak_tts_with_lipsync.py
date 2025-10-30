"""
eSpeak TTS with integrated lip sync support
Generates audio to WAV file, then plays while controlling jaw servo
"""
import subprocess
import os
import time
import threading
import queue
from typing import Optional
from pathlib import Path
import tempfile

class ESpeakWithLipSync:
    """eSpeak TTS that generates WAV files for perfect lip sync"""

    def __init__(self, voice: str = "en-us", speed: int = 150, pitch: int = 50,
                 use_whisper: bool = False, lipsync_controller=None):
        """
        Initialize eSpeak with lip sync

        Args:
            voice: Voice name (e.g., "en-us")
            speed: Words per minute
            pitch: Pitch (0-99)
            use_whisper: Use whisper variant
            lipsync_controller: DirectAudioLipSync instance
        """
        # Find eSpeak
        self.espeak_path = r"C:\Program Files\eSpeak NG\espeak-ng.exe"
        if not os.path.exists(self.espeak_path):
            raise RuntimeError(f"eSpeak NG not found at {self.espeak_path}")

        self.voice = voice
        self.speed = speed
        self.pitch = pitch
        self.use_whisper = use_whisper
        self.lipsync = lipsync_controller

        # Queue for thread-safe speech
        self.speech_queue = queue.Queue()
        self.should_stop = False
        self.is_speaking = False
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

        # Temp directory for WAV files
        self.temp_dir = Path(tempfile.gettempdir()) / "espeak_lipsync"
        self.temp_dir.mkdir(exist_ok=True)

        print(f"✅ eSpeak with lip sync initialized")

    def _get_voice_string(self) -> str:
        """Get voice string with variant"""
        voice_str = self.voice
        if self.use_whisper and "+whisper" not in voice_str:
            voice_str = f"{voice_str}+whisper"
        return voice_str

    def _clean_for_speech(self, text: str) -> str:
        """Clean text for speech output"""
        import re

        # Remove timestamps
        text = re.sub(r'\[\d{1,2}[msh]\]', '', text)
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)

        # Remove emoji and special characters
        text = re.sub(r'[🎯🧹🚫🔄✅👁️🧠🎭💭🖨️📝]', '', text)

        # Remove debug markers
        text = re.sub(r'\[(?:DEBUG|System|Tone|Internal|Visual)[^\]]*\]', '', text, flags=re.IGNORECASE)

        # Remove literal asterisks and filter "asterisk" word
        text = text.replace('*', '')
        text = re.sub(r'\basterisk\b', '', text, flags=re.IGNORECASE)

        # Remove action markers and roleplay formatting
        text = re.sub(r'\([^)]*\)', '', text)  # Remove parenthetical actions like (Weary)
        text = re.sub(r'\[[^\]]*\]', '', text)  # Remove bracketed content

        # Clean up extra whitespace
        text = ' '.join(text.split())

        return text.strip()

    def _speech_worker(self):
        """Worker thread that processes speech queue"""
        while not self.should_stop:
            try:
                item = self.speech_queue.get(timeout=0.5)
                if item:
                    if len(item) == 6:
                        text, use_whisper_override, speed_override, pitch_override, start_callback, end_callback = item
                    elif len(item) == 5:
                        # Backwards compatibility - single callback is start callback
                        text, use_whisper_override, speed_override, pitch_override, start_callback = item
                        end_callback = None
                    else:
                        # Backwards compatibility
                        text, use_whisper_override, speed_override, pitch_override = item
                        start_callback = None
                        end_callback = None
                    self._do_speak(text, use_whisper_override, speed_override, pitch_override, start_callback, end_callback)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Speech worker error: {e}")

    def _do_speak(self, text: str, use_whisper_override: Optional[bool],
                   speed_override: Optional[int], pitch_override: Optional[int],
                   on_start_callback: Optional[callable] = None,
                   on_end_callback: Optional[callable] = None):
        """Actually perform speech"""
        if not text or not text.strip():
            return

        # Clean text before speaking
        text = self._clean_for_speech(text)
        if not text:
            return

        self.is_speaking = True

        try:
            # Determine voice
            if use_whisper_override is not None:
                voice_str = self.voice + ("+whisper" if use_whisper_override else "")
            else:
                voice_str = self._get_voice_string()

            # Use speed/pitch overrides if provided
            speed = speed_override if speed_override is not None else self.speed
            pitch = pitch_override if pitch_override is not None else self.pitch

            # Generate unique WAV file
            wav_file = self.temp_dir / f"speech_{int(time.time()*1000)}.wav"

            # Build eSpeak command to generate WAV
            cmd = [
                self.espeak_path,
                "-v", voice_str,
                "-s", str(speed),
                "-p", str(pitch),
                "-w", str(wav_file),  # Write to WAV file
                text
            ]

            # Generate WAV file
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"eSpeak error: {result.stderr}")
                return

            # Play WAV with lip sync - callbacks fire when jaw moves and when audio ends
            if self.lipsync and wav_file.exists():
                self.lipsync.play_with_lipsync(str(wav_file), on_start_callback=on_start_callback, on_end_callback=on_end_callback)
            else:
                # Fallback: play without lip sync
                import pyaudio
                import wave
                p = pyaudio.PyAudio()
                wf = wave.open(str(wav_file), 'rb')
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                               channels=wf.getnchannels(),
                               rate=wf.getframerate(),
                               output=True)
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)
                stream.close()
                wf.close()
                p.terminate()

            # Clean up WAV file
            try:
                wav_file.unlink()
            except:
                pass

        except Exception as e:
            print(f"eSpeak error: {e}")
        finally:
            self.is_speaking = False

    def speak(self, text: str, use_whisper: Optional[bool] = None,
             speed: Optional[int] = None, pitch: Optional[int] = None,
             on_start_callback: Optional[callable] = None,
             on_end_callback: Optional[callable] = None):
        """
        Queue text for speech

        Args:
            text: Text to speak
            use_whisper: Override whisper setting
            speed: Override speed (WPM)
            pitch: Override pitch (0-99)
            on_start_callback: Called when jaw actually moves (audio playing)
            on_end_callback: Called when audio finishes playing
        """
        if not text or not text.strip():
            return

        self.speech_queue.put((text, use_whisper, speed, pitch, on_start_callback, on_end_callback))

    def stop(self):
        """Stop speech system"""
        self.should_stop = True
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)

        # Clean up temp files
        try:
            for f in self.temp_dir.glob("speech_*.wav"):
                f.unlink()
        except:
            pass

        print("eSpeak with lip sync stopped")


if __name__ == "__main__":
    # Test
    from lipsync_direct_audio import DirectAudioLipSync

    print("Testing eSpeak with lip sync...")

    lipsync = DirectAudioLipSync(port="COM3", enabled=True)
    tts = ESpeakWithLipSync(
        voice="en-us",
        speed=150,
        use_whisper=True,
        lipsync_controller=lipsync
    )

    test_phrases = [
        "Hello, this is a test of lip sync.",
        "The jaw should move with my voice.",
        "This is much better than audio capture."
    ]

    for phrase in test_phrases:
        print(f"Speaking: {phrase}")
        tts.speak(phrase)
        time.sleep(5)  # Wait for speech to complete

    tts.stop()
    lipsync.stop()
    print("Test complete!")
