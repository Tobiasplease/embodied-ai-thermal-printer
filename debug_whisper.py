"""
Debug whisper DSP - check what's happening at each step
"""
import numpy as np
from scipy import signal
from pydub import AudioSegment
import tempfile
import os

def debug_whisper_process(audio_path):
    """Step through whisper processing to see where audio disappears"""
    print("=" * 70)
    print("WHISPER DSP DEBUG")
    print("=" * 70)
    print()
    
    # Load audio
    print("1. Loading original audio...")
    audio = AudioSegment.from_wav(audio_path)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    sample_rate = audio.frame_rate
    
    print(f"   Sample rate: {sample_rate} Hz")
    print(f"   Samples: {len(samples)}")
    print(f"   Duration: {len(samples)/sample_rate:.2f}s")
    print(f"   Range: {samples.min():.0f} to {samples.max():.0f}")
    print()
    
    # Step 1: Normalize
    print("2. Normalizing...")
    samples = samples / (np.max(np.abs(samples)) + 1e-10)
    print(f"   Range after normalize: {samples.min():.3f} to {samples.max():.3f}")
    print()
    
    # Step 2: Add pink noise (NO pitch removal yet)
    print("3. Adding pink noise (breath)...")
    noise_level = 0.05  # Reduced from 0.08
    pink = generate_pink_noise(len(samples)) * noise_level
    samples_with_noise = samples + pink
    print(f"   Range after noise: {samples_with_noise.min():.3f} to {samples_with_noise.max():.3f}")
    
    # Export test
    test_audio = create_audio_segment(samples_with_noise, sample_rate)
    test_path = "test_with_noise.wav"
    test_audio.export(test_path, format="wav")
    print(f"   ✅ Exported: {test_path}")
    print()
    
    # Step 3: High-pass filter
    print("4. Applying high-pass filter (300 Hz cutoff)...")
    nyquist = sample_rate / 2
    cutoff = 300 / nyquist
    b, a = signal.butter(4, cutoff, btype='high')
    samples_filtered = signal.filtfilt(b, a, samples_with_noise)
    print(f"   Range after filter: {samples_filtered.min():.3f} to {samples_filtered.max():.3f}")
    
    # Export test
    test_audio = create_audio_segment(samples_filtered, sample_rate)
    test_path = "test_filtered.wav"
    test_audio.export(test_path, format="wav")
    print(f"   ✅ Exported: {test_path}")
    print()
    
    # Step 4: Reduce amplitude
    print("5. Reducing amplitude to 70%...")
    samples_quiet = samples_filtered * 0.7
    print(f"   Range after reduction: {samples_quiet.min():.3f} to {samples_quiet.max():.3f}")
    
    # Export test
    test_audio = create_audio_segment(samples_quiet, sample_rate)
    test_path = "test_final.wav"
    test_audio.export(test_path, format="wav")
    print(f"   ✅ Exported: {test_path}")
    print()
    
    print("=" * 70)
    print("DIAGNOSIS")
    print("=" * 70)
    print()
    print("Generated test files:")
    print("  - test_with_noise.wav (just noise added)")
    print("  - test_filtered.wav (after high-pass)")
    print("  - test_final.wav (final whisper)")
    print()
    print("Play these files to find where audio disappears!")
    print()

def generate_pink_noise(length):
    """Generate pink noise"""
    white = np.random.randn(length)
    fft = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(length)
    freqs[0] = 1
    pink_filter = 1 / np.sqrt(freqs)
    pink_fft = fft * pink_filter
    pink = np.fft.irfft(pink_fft, length)
    return pink / (np.max(np.abs(pink)) + 1e-10)

def create_audio_segment(samples, sample_rate):
    """Convert samples to AudioSegment"""
    # Normalize and convert to int16
    samples = samples / (np.max(np.abs(samples)) + 1e-10)
    samples_int = (samples * 32767 * 0.9).astype(np.int16)
    
    return AudioSegment(
        samples_int.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

if __name__ == "__main__":
    import pyttsx3
    
    # Generate test audio
    print("Generating test speech...")
    engine = pyttsx3.init()
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
        temp_path = temp.name
    
    engine.save_to_file("I notice the shadows on the wall", temp_path)
    engine.runAndWait()
    
    print(f"Saved to: {temp_path}")
    print()
    
    # Debug the whisper process
    debug_whisper_process(temp_path)
    
    # Clean up
    try:
        os.unlink(temp_path)
    except:
        pass
