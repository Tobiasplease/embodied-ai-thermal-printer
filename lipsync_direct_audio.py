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

    def __init__(self, port: str = "COM3", baud: int = 9600, enabled: bool = True):
        """
        Initialize direct audio lip sync

        Args:
            port: Serial port for Arduino
            baud: Baud rate
            enabled: Enable/disable lip sync
        """
        self.enabled = enabled
        self.port = port
        self.baud = baud
        self.serial_conn = None
        self.is_playing = False
        self.should_stop = False

        # Servo positions
        self.JAW_CLOSED = 20
        self.JAW_OPEN = 70

        # Audio thresholds (lower = more sensitive)
        self.SILENCE_THRESHOLD = 50
        self.MAX_AMPLITUDE = 5000

        # Smoothing (higher = smoother, 0.0-1.0)
        self.last_angle = self.JAW_CLOSED
        self.smoothing_factor = 0.75

        # PyAudio
        self.audio = pyaudio.PyAudio()

        if self.enabled:
            self._connect_serial()

    def _connect_serial(self):
        """Connect to Arduino"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)
            self._send_command(self.JAW_CLOSED)
            print(f"✅ Direct audio lip sync connected to {self.port}")
        except Exception as e:
            print(f"⚠️ Lip sync disabled: {e}")
            self.enabled = False
            self.serial_conn = None

    def _send_command(self, angle: int):
        """Send servo angle to Arduino"""
        if not self.enabled or not self.serial_conn:
            return
        try:
            angle = max(self.JAW_CLOSED, min(self.JAW_OPEN, int(angle)))
            self.serial_conn.write(f"{angle}\n".encode())
        except Exception as e:
            print(f"⚠️ Lip sync error: {e}")

    def _amplitude_to_angle(self, amplitude: float) -> int:
        """Convert amplitude to jaw angle"""
        if amplitude < self.SILENCE_THRESHOLD:
            return self.JAW_CLOSED

        # Normalize amplitude
        normalized = (amplitude - self.SILENCE_THRESHOLD) / (self.MAX_AMPLITUDE - self.SILENCE_THRESHOLD)
        normalized = max(0, min(1, normalized))

        # Calculate target angle
        target_angle = self.JAW_CLOSED + (normalized * (self.JAW_OPEN - self.JAW_CLOSED))

        # Smooth movement
        smoothed = (self.smoothing_factor * target_angle) + ((1 - self.smoothing_factor) * self.last_angle)
        self.last_angle = smoothed

        return int(smoothed)

    def play_with_lipsync(self, wav_path: str):
        """
        Play WAV file and sync jaw to audio waveform

        Args:
            wav_path: Path to WAV file to play
        """
        if not self.enabled or not Path(wav_path).exists():
            return

        self.is_playing = True
        self.should_stop = False

        try:
            # Open WAV file
            wf = wave.open(wav_path, 'rb')

            # Open audio stream
            stream = self.audio.open(
                format=self.audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )

            # Read and play audio in chunks while analyzing
            chunk_size = 1024
            data = wf.readframes(chunk_size)

            while data and not self.should_stop:
                # Play audio
                stream.write(data)

                # Analyze amplitude
                audio_array = np.frombuffer(data, dtype=np.int16)
                amplitude = np.sqrt(np.mean(audio_array**2))

                # Move jaw
                jaw_angle = self._amplitude_to_angle(amplitude)
                self._send_command(jaw_angle)

                # Read next chunk
                data = wf.readframes(chunk_size)

            # Cleanup
            stream.stop_stream()
            stream.close()
            wf.close()

        except Exception as e:
            print(f"⚠️ Audio playback error: {e}")

        finally:
            # Close jaw
            self._send_command(self.JAW_CLOSED)
            self.is_playing = False

    def stop(self):
        """Stop playback and close jaw"""
        self.should_stop = True
        time.sleep(0.2)

        if self.serial_conn:
            self._send_command(self.JAW_CLOSED)
            self.serial_conn.close()

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
