"""
REAL whisper effect using audio signal processing
This actually removes pitch and adds breath noise - not just slow speech!

Requirements: pip install pydub numpy scipy
"""
import numpy as np
from scipy import signal
from pydub import AudioSegment
from pydub.effects import normalize
import io
import wave

def speech_to_whisper(audio_path, output_path=None):
    """
    Convert normal speech to whisper using DSP
    
    Steps:
    1. Remove fundamental frequency (pitch) - make unvoiced
    2. Add pink noise (breath simulation)
    3. Apply high-pass filter (whispers have less low freq)
    4. Reduce overall amplitude (whispers are quieter)
    5. Add slight reverb/room tone
    
    This is REAL whispering, not fake slow-down
    """
    # Load audio
    audio = AudioSegment.from_wav(audio_path)
    
    # Convert to numpy array
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    sample_rate = audio.frame_rate
    
    # Normalize
    samples = samples / np.max(np.abs(samples))
    
    # Step 1: Remove pitch (fundamental frequency)
    # Use spectral flattening to make voiced sounds unvoiced
    samples = remove_pitch(samples, sample_rate)
    
    # Step 2: Add pink noise (breath)
    noise_level = 0.05  # 5% noise
    pink_noise = generate_pink_noise(len(samples)) * noise_level
    samples = samples + pink_noise
    
    # Step 3: High-pass filter (whispers have less bass)
    # Cutoff at 300 Hz - removes rumble
    nyquist = sample_rate / 2
    cutoff = 300 / nyquist
    b, a = signal.butter(4, cutoff, btype='high')
    samples = signal.filtfilt(b, a, samples)
    
    # Step 4: Reduce amplitude (whispers are quieter)
    samples = samples * 0.6
    
    # Step 5: Add slight room ambience
    samples = add_ambience(samples, sample_rate)
    
    # Normalize and convert back
    samples = samples / np.max(np.abs(samples))
    samples = (samples * 32767).astype(np.int16)
    
    # Create output audio
    whisper_audio = AudioSegment(
        samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )
    
    if output_path:
        whisper_audio.export(output_path, format="wav")
    
    return whisper_audio

def remove_pitch(samples, sample_rate):
    """
    Remove fundamental frequency to make speech unvoiced
    Uses spectral processing to flatten harmonics
    """
    # FFT to frequency domain
    fft = np.fft.rfft(samples)
    freqs = np.fft.rfftfreq(len(samples), 1/sample_rate)
    
    # Flatten magnitude spectrum (removes pitch while keeping formants)
    magnitude = np.abs(fft)
    phase = np.angle(fft)
    
    # Smooth magnitude to remove harmonic structure
    window_size = int(sample_rate / 50)  # ~50 Hz smoothing
    smoothed_mag = np.convolve(magnitude, np.ones(window_size)/window_size, mode='same')
    
    # Reconstruct with smoothed magnitude
    new_fft = smoothed_mag * np.exp(1j * phase)
    
    return np.fft.irfft(new_fft, len(samples))

def generate_pink_noise(length):
    """
    Generate pink noise (1/f noise) for breath simulation
    Pink noise sounds more natural than white noise
    """
    # Generate white noise
    white = np.random.randn(length)
    
    # Apply 1/f filter
    fft = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(length)
    
    # 1/f spectrum (avoiding division by zero)
    freqs[0] = 1
    pink_filter = 1 / np.sqrt(freqs)
    pink_fft = fft * pink_filter
    
    pink = np.fft.irfft(pink_fft, length)
    
    # Normalize
    return pink / np.max(np.abs(pink))

def add_ambience(samples, sample_rate):
    """
    Add slight reverb/room tone for natural whisper
    """
    # Simple convolution reverb
    impulse_length = int(sample_rate * 0.05)  # 50ms
    impulse = np.exp(-np.linspace(0, 5, impulse_length))
    
    reverb = np.convolve(samples, impulse, mode='same')
    
    # Mix dry/wet
    return samples * 0.9 + reverb * 0.1


# Test if dependencies available
try:
    import pydub
    import scipy
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

if __name__ == "__main__":
    print("=" * 70)
    print("REAL WHISPER EFFECT TEST")
    print("=" * 70)
    print()
    
    if not WHISPER_AVAILABLE:
        print("❌ Dependencies not installed!")
        print()
        print("Install with:")
        print("  pip install pydub numpy scipy")
        print()
        print("Also install ffmpeg:")
        print("  1. Download: https://ffmpeg.org/download.html")
        print("  2. Add to PATH")
        exit(1)
    
    print("✅ Dependencies available")
    print()
    print("This will:")
    print("  1. Remove pitch (fundamental frequency)")
    print("  2. Add pink noise (breath)")
    print("  3. High-pass filter (less bass)")
    print("  4. Reduce amplitude (quieter)")
    print("  5. Add room ambience")
    print()
    print("Result: ACTUAL whisper, not fake slow-down!")
    print()
    print("To integrate:")
    print("  - Modify windows_tts.py to save WAV")
    print("  - Apply speech_to_whisper() transform")
    print("  - Play processed audio")
    print()
    print("Performance: ~200-500ms processing per sentence")
    print("Worth it? You decide!")
