# Configuration for Embodied AI v2 - OPTIMIZED FOR LIGHTER SYSTEMS
# This uses smaller versions of the same model families
# Simple, single-source configuration

# Camera Settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640  
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# AI Settings
OLLAMA_URL = "http://localhost:11434"

# Dual Consciousness Model Setup - SMALLER VERSIONS
# Option 1: Smaller MiniCPM-V (if available - we pulled 'latest' which might be smaller)
OLLAMA_MODEL = "minicpm-v:latest"  # Visual perception model (lighter than 8b)
SUBCONSCIOUS_MODEL = "smollm2:1.7b"  # Language/thought model (MUCH lighter - 1.7B vs 8B)

# Option 2: Ultra-light with Moondream (uncomment to try)
# OLLAMA_MODEL = "moondream:latest"  # Ultra-lightweight vision (1.7GB vs 5.5GB)
# SUBCONSCIOUS_MODEL = "smollm2:1.7b"

# Option 3: Just use smaller language model with 8b vision
# OLLAMA_MODEL = "minicpm-v:8b"  # Keep original vision
# SUBCONSCIOUS_MODEL = "smollm2:1.7b"  # Use smaller language

AI_PROCESS_INTERVAL = 15.0  # seconds between AI processing (can increase to 20-30 for even lighter load)
USE_SOPHISTICATED_PROMPTS = False  # Testing hybrid focus-aware legacy system
OLLAMA_TIMEOUT = 120  # seconds - increase for complex prompts

# Personality Settings
MEMORY_SIZE = 100  # number of observations to remember
MAX_BELIEFS = 50  # maximum number of beliefs to track
BELIEF_THRESHOLD = 0.7  # confidence needed to form beliefs
PERSONALITY_SAVE_FILE = "personality_state.json"

# Motor Settings  
MOTOR_TYPE = "simulation"  # or "arduino", "servo", etc.
MOTOR_PORT = "COM3"  # for hardware controllers
MOTOR_BAUD = 9600

# Debug Settings
DEBUG_CAMERA = False  # Camera overlay debug
DEBUG_AI = True       # AI processing debug
DEBUG_MOTOR = False   # Motor control debug
VERBOSE_OUTPUT = False  # Extra verbose logging

# Thermal Printer Settings
THERMAL_PRINTER_ENABLED = True
THERMAL_PRINTER_NAME = "XP-80"  # Default thermal printer name

# Voice Settings
VOICE_ENABLED = True  # Set to True to enable voice output
VOICE_ENGINE = "espeak"  # "espeak" (lo-fi, whisper), "windows" (robotic), or "piper" (natural)

# eSpeak TTS Settings (if VOICE_ENGINE = "espeak")
ESPEAK_VOICE = "en-us+whisper"  # Voice with variants: en-us+whisper, en+f3+whisper, en+croak, etc.
ESPEAK_SPEED = 130  # Words per minute: 80-450 (slower for whisper)
ESPEAK_PITCH = 85  # Pitch: 0-99 (lower = deeper/more masculine)

# Piper TTS Settings (if VOICE_ENGINE = "piper")
VOICE_MODEL = "en_US-kristin-medium"  # Voice model: kristin (F), ryan (M), lessac (F)

# Windows TTS Settings (if VOICE_ENGINE = "windows")
WINDOWS_TTS_RATE = 150  # Words per minute: 100=slow, 200=normal, 300=fast
WINDOWS_TTS_VOLUME = 0.9  # Volume: 0.0 to 1.0
WINDOWS_TTS_GENDER = "female"  # "male" or "female" (David or Zira)

# Common Voice Settings
VOICE_ALL_THOUGHTS = True  # Speak every thought (can be overwhelming!)
VOICE_INTERVAL = 30  # Speak every N seconds (if not speaking all thoughts)

# Camera Preview Settings  
SHOW_CAMERA_PREVIEW = True
PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600
SUBTITLE_DURATION = 8.0  # seconds to show each caption
MIN_CAPTION_INTERVAL = 5.0  # minimum seconds between captions
