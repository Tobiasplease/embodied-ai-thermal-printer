# Setup Guide for New Machine

## Quick Start (5 minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Ollama
Download from: https://ollama.ai/download

After installing, pull the models:
```bash
ollama pull moondream:latest
ollama pull Tohur/natsumura-storytelling-rp-llama-3.1:8b
```

**Total download:** ~6.6 GB (moondream 1.7GB + natsumura 4.9GB)

### 3. Install eSpeak NG (for natural voice)
```bash
python install_espeak.py
```

This will download and install eSpeak NG with the whisper voice variant.

### 4. Run the System
```bash
python main.py
```

## What Gets Installed

### Python Packages (via pip)
- `opencv-python` - Camera input
- `requests` - Ollama API communication
- `pywin32` - Windows TTS fallback
- `syllapy` - Syllable counting for natural speech pacing
- `pillow` - Image processing
- `numpy` - Array operations
- `pyserial` - Hand controller (optional hardware)

### External Software
- **Ollama** - Local LLM server (runs models locally)
  - `moondream:latest` (1.7GB) - Vision understanding
  - `Tohur/natsumura-storytelling-rp-llama-3.1:8b` (4.9GB) - Language generation
  
- **eSpeak NG** - Text-to-speech engine
  - Uses `en-us+whisper` voice for natural-sounding speech
  - Much better than Windows default TTS

## Troubleshooting

### Camera not found
Check available cameras:
```bash
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"
```

Edit `config.py` and change `CAMERA_INDEX` if needed.

### Ollama connection error
Make sure Ollama is running:
```bash
ollama list
```

Should show your installed models.

### No voice output
The system falls back to Windows TTS if eSpeak fails. Check:
```bash
python -c "import espeak_tts_simple; espeak_tts_simple.ESpeakTTS().speak('test')"
```

## Configuration

Edit `config.py` to customize:
- `AI_PROCESS_INTERVAL` - How often AI processes (default: 5 seconds)
- `ESPEAK_SPEED` - Speech speed in words per minute (default: 150)
- `CAMERA_INDEX` - Which camera to use (default: 0)
- `DEBUG_AI` - Enable detailed AI output logging
