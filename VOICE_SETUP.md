# Voice System Setup Guide

## Quick Setup (Piper TTS - Recommended)

### 1. Download Piper
- Go to: https://github.com/rhasspy/piper/releases
- Download `piper_windows_amd64.zip` (latest release)
- Extract to `./piper/` in your project directory

### 2. Download Voice Model
- Go to: https://huggingface.co/rhasspy/piper-voices/tree/main
- Navigate to your preferred voice:
  - `en_US/lessac/medium/` - Female, clear (recommended)
  - `en_US/ryan/high/` - Male, expressive
  - `en_US/amy/medium/` - Female, natural
- Download both files:
  - `en_US-lessac-medium.onnx` (~10MB)
  - `en_US-lessac-medium.onnx.json` (~1KB)
- Place in `./piper/models/`

### 3. Directory Structure
```
embodied_ai_standalone/
├── piper/
│   ├── piper.exe
│   ├── espeak-ng-data/ (included in zip)
│   └── models/
│       ├── en_US-lessac-medium.onnx
│       └── en_US-lessac-medium.onnx.json
├── voice.py
└── main.py
```

### 4. Test It
```bash
python voice.py
```

## Integration with Main System

Add to `config.py`:
```python
# Voice Settings
VOICE_ENABLED = True  # Set to False to disable voice
VOICE_MODEL = "en_US-lessac-medium"  # Voice to use
VOICE_ALL_THOUGHTS = False  # Speak every thought (can be overwhelming!)
VOICE_INTERVAL = 30  # Speak every N seconds
```

## Alternative: Simple System TTS (No download needed)

If you want something immediate without downloading Piper:

```python
# Simple fallback using Windows built-in TTS
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed
engine.setProperty('volume', 0.9)  # Volume
engine.say("Hello, I am the embodied AI")
engine.runAndWait()
```

Install with: `pip install pyttsx3`

**Trade-off**: Much lower quality, less natural, but works immediately.

## Performance Notes

- **Piper**: ~100-200ms latency per sentence (real-time capable)
- **pyttsx3**: ~50ms latency but robotic quality
- **Coqui TTS**: ~500-1000ms latency (too slow for real-time)

For your 7-second thought interval, Piper is perfect!

## Voice Personality Tips

You could modulate speech based on emotional state:
- **Curious**: Faster rate, higher pitch
- **Contemplative**: Slower rate, lower pitch  
- **Anxious**: Faster rate, slight variation
- **Numb**: Monotone, very slow

This would require pitch/rate adjustments to Piper models.
