"""
Windows TTS with REAL whisper effect using DSP
Transforms normal speech into actual whisper (not fake slow-down!)
"""
import threading
import queue
import tempfile
import os
from pathlib import Path

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import numpy as np
    from scipy import signal
    from pydub import AudioSegment
    DSP_AVAILABLE = True
except ImportError:
    DSP_AVAILABLE = False

DEBUG_VOICE = True

class WindowsTTSWithWhisper:
    """Windows TTS with real whisper DSP processing"""
    
    def __init__(self):
        """Initialize Windows TTS engine"""
        self.engine = None
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.should_stop = False
        self.worker_thread = None
        
        # Voice parameters
        self.rate = 150
        self.volume = 0.9
        self.voice_gender = "female"
        
        # Whisper mode
        self.whisper_enabled = False
        
        # Set ffmpeg path for pydub
        self._setup_ffmpeg()
        
        if not PYTTSX3_AVAILABLE:
            print("❌ pyttsx3 not installed")
            return
        
        if not DSP_AVAILABLE:
            print("⚠️ Whisper DSP not available (scipy/pydub missing)")
            print("   Voice will work but whisper effect disabled")
        
        try:
            self.engine = pyttsx3.init()
            self._configure_voice()
            if DEBUG_VOICE:
                print("✅ Windows TTS initialized")
                if DSP_AVAILABLE:
                    print("✅ Real whisper DSP available")
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            self.engine = None
    
    def _setup_ffmpeg(self):
        """Setup ffmpeg path for pydub"""
        # Look for local ffmpeg installation
        possible_paths = [
            Path("ffmpeg") / "ffmpeg-*" / "bin" / "ffmpeg.exe",
            Path("ffmpeg") / "bin" / "ffmpeg.exe",
        ]
        
        for pattern in possible_paths:
            matches = list(Path(".").glob(str(pattern)))
            if matches:
                ffmpeg_path = str(matches[0].absolute())
                os.environ["PATH"] = str(matches[0].parent) + os.pathsep + os.environ["PATH"]
                if DEBUG_VOICE:
                    print(f"✅ Found ffmpeg at: {ffmpeg_path}")
                break
    
    def _configure_voice(self):
        """Configure voice parameters"""
        if not self.engine:
            return
        
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)
        
        # Set voice gender
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if self.voice_gender == "female" and "zira" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
            elif self.voice_gender == "male" and "david" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def set_rate(self, rate):
        """Set speech rate (words per minute)"""
        self.rate = max(50, min(400, rate))
        if self.engine:
            self.engine.setProperty('rate', self.rate)
    
    def set_volume(self, volume):
        """Set volume level (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty('volume', self.volume)
    
    def set_voice_gender(self, gender):
        """Set voice gender ('male' or 'female')"""
        self.voice_gender = gender
        self._configure_voice()
    
    def set_whisper_mode(self, enabled=True):
        """Enable/disable real whisper DSP processing"""
        if not DSP_AVAILABLE:
            if DEBUG_VOICE and enabled:
                print("⚠️ Whisper mode requested but DSP not available")
            return
        
        self.whisper_enabled = enabled
        if DEBUG_VOICE:
            print(f"🤫 Real whisper mode: {'ON' if enabled else 'OFF'}")
    
    def start(self):
        """Start the voice worker thread"""
        if not self.engine:
            return False
        
        self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)
        self.worker_thread.start()
        
        if DEBUG_VOICE:
            print("🔊 Windows TTS started")
        return True
    
    def speak(self, text, priority=False, whisper=None):
        """
        Queue text for speech output
        
        Args:
            text: Text to speak
            priority: If True, clear queue and speak immediately
            whisper: Override whisper mode for this speech (True/False/None)
        """
        if not self.engine:
            return
        
        text = self._clean_for_speech(text)
        use_whisper = whisper if whisper is not None else self.whisper_enabled
        
        if priority:
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break
            if self.is_speaking:
                self.engine.stop()
        
        self.speech_queue.put((text, use_whisper))
        
        if DEBUG_VOICE:
            mode = "🤫" if use_whisper else "🎙️"
            print(f"{mode} Queued: {text[:50]}... (queue: {self.speech_queue.qsize()})")
    
    def _clean_for_speech(self, text):
        """Clean text for speech output"""
        import re
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)
        text = re.sub(r'[🎯🧹🚫🔄✅👁️🧠🎭💭🖨️📝]', '', text)
        text = re.sub(r'\[(?:DEBUG|System|Tone)[^\]]*\]', '', text)
        text = ' '.join(text.split())
        return text.strip()
    
    def _voice_worker(self):
        """Worker thread that processes speech queue"""
        while not self.should_stop:
            try:
                item = self.speech_queue.get(timeout=0.5)
                
                if item:
                    if isinstance(item, tuple):
                        text, use_whisper = item
                    else:
                        text = item
                        use_whisper = self.whisper_enabled
                    
                    self._synthesize_and_play(text, use_whisper)
                    
            except queue.Empty:
                continue
            except Exception as e:
                if DEBUG_VOICE:
                    print(f"❌ Voice worker error: {e}")
    
    def _synthesize_and_play(self, text, use_whisper=False):
        """Synthesize and play speech, optionally with whisper effect"""
        self.is_speaking = True
        
        try:
            if use_whisper and DSP_AVAILABLE:
                # Generate to WAV, apply whisper DSP, then play
                self._speak_with_whisper_dsp(text)
            else:
                # Normal speech
                if DEBUG_VOICE:
                    print(f"🤖 Speaking: {text[:60]}...")
                self.engine.say(text)
                self.engine.runAndWait()
            
        except Exception as e:
            if DEBUG_VOICE:
                print(f"❌ Speech error: {e}")
        finally:
            self.is_speaking = False
    
    def _speak_with_whisper_dsp(self, text):
        """Generate speech, apply whisper DSP, and play"""
        # Create temp WAV file for TTS output
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_in:
            temp_in_path = temp_in.name
        
        try:
            # Generate speech to WAV
            if DEBUG_VOICE:
                print(f"🤫 Whispering: {text[:60]}...")
            
            self.engine.save_to_file(text, temp_in_path)
            self.engine.runAndWait()
            
            # Apply whisper DSP
            whisper_audio = self._apply_whisper_dsp(temp_in_path)
            
            # Play whispered audio
            self._play_audio_segment(whisper_audio)
            
        finally:
            # Clean up
            try:
                os.unlink(temp_in_path)
            except:
                pass
    
    def _apply_whisper_dsp(self, audio_path):
        """Apply real whisper effect using DSP"""
        # Load audio
        audio = AudioSegment.from_wav(audio_path)
        
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        sample_rate = audio.frame_rate
        channels = audio.channels
        
        # Process each channel
        if channels == 2:
            # Stereo - process each channel
            left = samples[::2]
            right = samples[1::2]
            left_whisper = self._whisperize(left, sample_rate)
            right_whisper = self._whisperize(right, sample_rate)
            # Interleave
            whisper_samples = np.empty(len(samples), dtype=np.int16)
            whisper_samples[::2] = left_whisper
            whisper_samples[1::2] = right_whisper
        else:
            # Mono
            whisper_samples = self._whisperize(samples, sample_rate)
        
        # Create whispered audio segment
        whisper_audio = AudioSegment(
            whisper_samples.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=channels
        )
        
        return whisper_audio
    
    def _whisperize(self, samples, sample_rate):
        """Transform speech samples into whisper - AGGRESSIVE version"""
        # Normalize
        samples = samples / (np.max(np.abs(samples)) + 1e-10)
        
        # 1. Remove pitch (flatten harmonics) - MORE AGGRESSIVE
        samples = self._remove_pitch(samples, sample_rate)
        
        # 2. Add MORE pink noise (breath) - doubled
        noise_level = 0.15  # Increased from 0.08 for obvious breath
        pink = self._generate_pink_noise(len(samples)) * noise_level
        samples = samples + pink
        
        # 3. High-pass filter (whispers have less bass) - HIGHER cutoff
        nyquist = sample_rate / 2
        cutoff = 500 / nyquist  # Increased from 300 Hz - more treble
        b, a = signal.butter(4, cutoff, btype='high')
        samples = signal.filtfilt(b, a, samples)
        
        # 4. Reduce amplitude MORE
        samples = samples * 0.5  # Quieter - from 0.7
        
        # 5. Add band-pass emphasis on breath frequencies (2-8 kHz)
        # This is where whisper "sibilance" lives
        bp_low = 2000 / nyquist
        bp_high = min(0.99, 8000 / nyquist)
        b_bp, a_bp = signal.butter(2, [bp_low, bp_high], btype='band')
        breath_emphasis = signal.filtfilt(b_bp, a_bp, samples) * 0.3
        samples = samples + breath_emphasis
        
        # 6. Normalize and convert to int16
        samples = samples / (np.max(np.abs(samples)) + 1e-10)
        return (samples * 32767 * 0.9).astype(np.int16)
    
    def _remove_pitch(self, samples, sample_rate):
        """Remove fundamental frequency to make speech unvoiced - AGGRESSIVE"""
        fft = np.fft.rfft(samples)
        magnitude = np.abs(fft)
        phase = np.angle(fft)
        
        # Much more aggressive smoothing to flatten harmonics
        window_size = max(5, int(sample_rate / 20))  # Larger window = more flattening
        smoothed = np.convolve(magnitude, np.ones(window_size)/window_size, mode='same')
        
        # Reduce overall magnitude to compensate for added noise
        smoothed = smoothed * 0.6
        
        new_fft = smoothed * np.exp(1j * phase)
        return np.fft.irfft(new_fft, len(samples))
    
    def _generate_pink_noise(self, length):
        """Generate pink noise (1/f) for breath simulation"""
        white = np.random.randn(length)
        fft = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(length)
        freqs[0] = 1  # Avoid division by zero
        pink_filter = 1 / np.sqrt(freqs)
        pink_fft = fft * pink_filter
        pink = np.fft.irfft(pink_fft, length)
        return pink / (np.max(np.abs(pink)) + 1e-10)
    
    def _play_audio_segment(self, audio_segment):
        """Play an AudioSegment using Windows"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_out:
            temp_out_path = temp_out.name
        
        try:
            audio_segment.export(temp_out_path, format="wav")
            
            import winsound
            winsound.PlaySound(temp_out_path, winsound.SND_FILENAME)
        finally:
            try:
                os.unlink(temp_out_path)
            except:
                pass
    
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


# For backwards compatibility
WindowsTTS = WindowsTTSWithWhisper

if __name__ == "__main__":
    import time
    
    print("=" * 70)
    print("REAL WHISPER DSP TEST")
    print("=" * 70)
    print()
    
    tts = WindowsTTSWithWhisper()
    
    if tts.start():
        print("Test 1: Normal speech")
        tts.set_whisper_mode(False)
        tts.speak("I notice the shadows on the wall.")
        time.sleep(4)
        
        print()
        print("Test 2: REAL whisper (with DSP processing)")
        tts.set_whisper_mode(True)
        tts.speak("I notice the shadows on the wall.")
        time.sleep(6)
        
        print()
        print("Test 3: Per-speech override")
        tts.set_whisper_mode(False)
        tts.speak("This is normal speech.", whisper=False)
        time.sleep(3)
        tts.speak("This is whispered.", whisper=True)
        time.sleep(6)
        
        print()
        print("⏳ Waiting for completion...")
        time.sleep(3)
        
        tts.stop()
        
        print()
        print("=" * 70)
        print("✅ TEST COMPLETE")
        print("=" * 70)
        print()
        print("That was REAL whispering - not fake slow-down!")
        print("Pitch removed, breath added, frequencies filtered.")
        print()
    else:
        print("❌ TTS not available")
