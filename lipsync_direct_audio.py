"""
Direct Audio Lip Sync
======================
Plays audio files while simultaneously analyzing the waveform for jaw control.
Perfect sync because we control both audio playback and jaw movement.
"""
import serial
import threading
import time
import wave
import numpy as np
import pyaudio
from pathlib import Path
from typing import Optional

class DirectAudioLipSync:
    """Plays audio and controls jaw servo based on actual waveform analysis"""

    def __init__(self, port: str = "COM3", baud: int = 9600, enabled: bool = True,
                 lightbulb_port: Optional[str] = None, lightbulb_baud: int = 9600,
                 lightbulb_enabled: bool = False):
        """
        Initialize direct audio lip sync

        Args:
            port: Serial port for jaw servo Arduino
            baud: Baud rate
            enabled: Enable/disable lip sync
            lightbulb_port: Serial port for lightbulb Arduino (optional)
            lightbulb_baud: Baud rate for lightbulb
            lightbulb_enabled: Enable/disable synchronized lightbulb
        """
        self.enabled = enabled
        self.port = port
        self.baud = baud
        self.serial_conn = None

        # Lightbulb control (separate Arduino)
        self.lightbulb_enabled = lightbulb_enabled
        self.lightbulb_port = lightbulb_port
        self.lightbulb_baud = lightbulb_baud
        self.lightbulb_serial = None

        # Lightbulb smoothing (prevents strobing)
        self.lightbulb_current_brightness = 20  # Start dim (maps to 30/255 on Arduino)
        self.lightbulb_smooth_factor = 0.2  # Slower smoothing for bulb (0.2 = smooth, 1.0 = instant)

        self.is_playing = False
        self.should_stop = False

        # Servo positions
        self.JAW_CLOSED = 20
        self.JAW_OPEN = 70

        # Audio thresholds (lower = more sensitive, adjusted for better responsiveness)
        self.SILENCE_THRESHOLD = 20   # Very low = opens on even quiet sounds
        self.MAX_AMPLITUDE = 250      # Lower = reaches full open more easily (adjusted for typical amplitude 30-50)

        # Smoothing (higher = smoother, 0.0-1.0) - reduced for faster response
        self.last_angle = self.JAW_CLOSED
        self.smoothing_factor = 0.5  # Reduced from 0.75 for quicker movement

        # Keep-alive for rapid speech (prevents closing too fast)
        self.last_open_time = 0
        self.keep_open_duration = 0.05  # Stay open for 50ms after sound

        # Playback timing (for subtitle sync)
        self.playback_start_time = None
        self.current_playback_time = 0.0

        # PyAudio
        self.audio = pyaudio.PyAudio()

        if self.enabled:
            self._connect_serial()

        if self.lightbulb_enabled and self.lightbulb_port:
            self._connect_lightbulb()

    def _connect_serial(self):
        """Connect to jaw servo Arduino"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)
            self._send_command(self.JAW_CLOSED)
            print(f"✅ Direct audio lip sync connected to {self.port}")
        except Exception as e:
            print(f"⚠️ Lip sync disabled: {e}")
            self.enabled = False
            self.serial_conn = None

    def _connect_lightbulb(self):
        """Connect to lightbulb Arduino"""
        try:
            self.lightbulb_serial = serial.Serial(self.lightbulb_port, self.lightbulb_baud, timeout=1)
            time.sleep(2)
            self._send_lightbulb_command(self.JAW_CLOSED)  # Start dim
            print(f"✅ Lightbulb sync connected to {self.lightbulb_port}")
        except Exception as e:
            print(f"⚠️ Lightbulb sync disabled: {e}")
            self.lightbulb_enabled = False
            self.lightbulb_serial = None

    def _send_command(self, angle: int):
        """Send servo angle to jaw Arduino"""
        if not self.enabled or not self.serial_conn:
            return
        try:
            angle = max(self.JAW_CLOSED, min(self.JAW_OPEN, int(angle)))
            self.serial_conn.write(f"{angle}\n".encode())
        except Exception as e:
            print(f"⚠️ Lip sync error: {e}")

    def _send_lightbulb_command(self, target_angle: int):
        """Send smoothed brightness to lightbulb Arduino (prevents strobing)"""
        if not self.lightbulb_enabled or not self.lightbulb_serial:
            return
        try:
            target_angle = max(self.JAW_CLOSED, min(self.JAW_OPEN, int(target_angle)))

            # Smooth the transition using exponential moving average
            # This prevents rapid flickering
            self.lightbulb_current_brightness = (
                self.lightbulb_smooth_factor * target_angle +
                (1 - self.lightbulb_smooth_factor) * self.lightbulb_current_brightness
            )

            smoothed_angle = int(self.lightbulb_current_brightness)
            self.lightbulb_serial.write(f"{smoothed_angle}\n".encode())
        except Exception as e:
            print(f"⚠️ Lightbulb sync error: {e}")

    def _amplitude_to_angle(self, amplitude: float) -> int:
        """Convert amplitude to jaw angle with minimum visible movement"""
        current_time = time.time()

        # Check if we should keep jaw open from recent sound
        time_since_open = current_time - self.last_open_time
        keep_alive = time_since_open < self.keep_open_duration

        if amplitude < self.SILENCE_THRESHOLD and not keep_alive:
            # True silence - close jaw
            target_angle = self.JAW_CLOSED
        else:
            # Sound detected OR keep-alive active
            if amplitude >= self.SILENCE_THRESHOLD:
                self.last_open_time = current_time

            # Normalize amplitude
            normalized = (amplitude - self.SILENCE_THRESHOLD) / (self.MAX_AMPLITUDE - self.SILENCE_THRESHOLD)
            normalized = max(0, min(1, normalized))

            # FULL OPENING: Always open fully when sound detected
            # With fast movement and consistent whisper volume, go all the way
            if normalized > 0.1:  # If any real sound detected
                normalized = 1.0  # Always fully open for maximum visibility

            # Keep-alive maintains high opening between syllables
            if keep_alive and normalized < 0.8:
                normalized = 0.8  # Stay mostly open during speech

            # Calculate target angle
            target_angle = self.JAW_CLOSED + (normalized * (self.JAW_OPEN - self.JAW_CLOSED))

        # Simplified smoothing - balanced for clear syllables
        if target_angle > self.last_angle:
            # Opening: moderate smoothing for clear but smooth opening
            dynamic_smoothing = self.smoothing_factor * 0.5
        else:
            # Closing: more smoothing to avoid jitter
            dynamic_smoothing = self.smoothing_factor * 1.0

        smoothed = (dynamic_smoothing * target_angle) + ((1 - dynamic_smoothing) * self.last_angle)

        # Limit maximum change per frame to reduce servo stress (prevents current spikes)
        MAX_CHANGE_PER_FRAME = 15  # degrees - balanced for responsiveness and hardware protection
        angle_delta = smoothed - self.last_angle
        if abs(angle_delta) > MAX_CHANGE_PER_FRAME:
            smoothed = self.last_angle + (MAX_CHANGE_PER_FRAME if angle_delta > 0 else -MAX_CHANGE_PER_FRAME)

        self.last_angle = smoothed

        return int(smoothed)

    def play_with_lipsync(self, wav_path: str, on_start_callback=None, on_end_callback=None):
        """
        Play WAV file and sync jaw to audio waveform

        Args:
            wav_path: Path to WAV file to play
            on_start_callback: Called when jaw actually starts moving (audio playing)
            on_end_callback: Called when audio playback finishes
        """
        print(f"🔊 play_with_lipsync called: {wav_path}, callback={on_start_callback is not None}")
        
        # Always play audio, even if serial/jaw control isn't available
        if not Path(wav_path).exists():
            print(f"❌ WAV file not found: {wav_path}")
            return

        self.is_playing = True
        self.should_stop = False
        self.playback_start_time = time.time()
        self.current_playback_time = 0.0

        try:
            # Open WAV file
            wf = wave.open(wav_path, 'rb')
            framerate = wf.getframerate()

            # Open audio stream
            stream = self.audio.open(
                format=self.audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=framerate,
                output=True
            )

            # Read and play audio in chunks while analyzing
            chunk_size = 1024
            data = wf.readframes(chunk_size)
            frames_played = 0
            callback_fired = False

            while data and not self.should_stop:
                # Play audio
                stream.write(data)

                # Update playback time based on frames played
                frames_played += len(data) // wf.getsampwidth() // wf.getnchannels()
                self.current_playback_time = frames_played / framerate

                # Analyze amplitude for jaw movement and callback timing
                audio_array = np.frombuffer(data, dtype=np.int16)
                if len(audio_array) > 0:
                    # Calculate RMS amplitude with NaN protection
                    rms = np.mean(np.abs(audio_array)**2)
                    amplitude = np.sqrt(rms) if not np.isnan(rms) else 0
                else:
                    amplitude = 0

                # Fire start callback when ACTUAL SPEECH begins (amplitude above threshold)
                # This syncs subtitles with when voice actually starts, not just audio file
                if not callback_fired and amplitude >= self.SILENCE_THRESHOLD and on_start_callback:
                    print(f"🎤 Speech detected (amplitude: {amplitude:.0f}) - firing callback")
                    try:
                        on_start_callback()
                    except Exception as e:
                        print(f"Callback error: {e}")
                    callback_fired = True

                # Move jaw and sync lightbulb
                if self.enabled:
                    jaw_angle = self._amplitude_to_angle(amplitude)
                    self._send_command(jaw_angle)
                    # Send same angle to lightbulb (it will map to brightness)
                    self._send_lightbulb_command(jaw_angle)

                # Read next chunk
                data = wf.readframes(chunk_size)

            # Cleanup
            stream.stop_stream()
            stream.close()
            wf.close()

            # Fire end callback after audio finishes
            if on_end_callback:
                try:
                    on_end_callback()
                except Exception as e:
                    print(f"End callback error: {e}")

        except Exception as e:
            print(f"⚠️ Audio playback error: {e}")

        finally:
            # Close jaw and dim lightbulb
            self._send_command(self.JAW_CLOSED)
            self._send_lightbulb_command(self.JAW_CLOSED)
            self.is_playing = False

    def stop(self):
        """Stop playback, close jaw, and turn off lightbulb"""
        self.should_stop = True
        time.sleep(0.2)

        if self.serial_conn:
            self._send_command(self.JAW_CLOSED)
            self.serial_conn.close()

        if self.lightbulb_serial:
            self._send_lightbulb_command(self.JAW_CLOSED)
            self.lightbulb_serial.close()

        self.audio.terminate()
        print("✅ Direct audio lip sync stopped")


if __name__ == "__main__":
    # Test with a WAV file
    print("Testing direct audio lip sync...")
    print("Place a test.wav file in this directory to test")

    lipsync = DirectAudioLipSync(port="COM3", enabled=True)

    # Test with any WAV file
    test_file = "test.wav"
    if Path(test_file).exists():
        print(f"Playing {test_file} with lip sync...")
        lipsync.play_with_lipsync(test_file)
    else:
        print(f"No {test_file} found - create one to test")

    lipsync.stop()
