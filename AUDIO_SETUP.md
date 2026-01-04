# Background Audio for Subtitle Projector

The subtitle projector now supports seamless looping ambient audio.

## Setup

1. **Install pygame** (if not already installed):
   ```bash
   pip install pygame
   ```

2. **Configure audio** in `config.py`:
   ```python
   SUBTITLE_PROJECTOR_AUDIO = r"C:\Users\tobia\Desktop\drone.wav"
   SUBTITLE_PROJECTOR_AUDIO_VOLUME = 0.3  # 0.0-1.0
   ```

   To disable audio, set to `None`:
   ```python
   SUBTITLE_PROJECTOR_AUDIO = None
   ```

3. **Place your audio file** at the configured path
   - Supports: WAV, MP3, OGG
   - Audio will loop seamlessly (infinite loop)
   - Fades in over 2 seconds on start
   - Fades out over 1 second when muted

## Controls

When the subtitle projector window is running:

- **A** - Toggle audio on/off
- **+** - Increase volume (10% increments)
- **-** - Decrease volume (10% increments)
- **F11** - Toggle fullscreen
- **M** - Mirror display (for back-projection)
- **ESC** - Exit fullscreen
- **Q** - Quit projector

## Features

- **Seamless loop**: Audio repeats infinitely with no gaps
- **Fade in/out**: Smooth transitions when toggling
- **Volume control**: Adjust on-the-fly with +/- keys
- **Low latency**: 512-byte buffer for minimal delay
- **Automatic initialization**: Starts playing when projector launches
- **Optional**: Falls back gracefully if pygame not installed

## Technical Details

- Uses `pygame.mixer` for reliable cross-platform audio playback
- 44.1kHz stereo, 16-bit audio
- Runs in subprocess alongside subtitle display
- No impact on main AI performance
