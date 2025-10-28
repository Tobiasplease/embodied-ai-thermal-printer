# Configuration for Embodied AI v2
# Simple, single-source configuration

# Camera Settings
CAMERA_INDEX = 0  # 0 = built-in laptop camera, 1 = external USB webcam
CAMERA_WIDTH = 640  # Back to higher resolution for better AI vision
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# AI Settings
OLLAMA_URL = "http://localhost:11434"
# Dual Consciousness Model Setup - PERFORMANCE TESTING OPTIONS

# === CURRENT SETUP (uncomment ONE set) ===

# Option 1: ORIGINAL (best quality, slowest) - 10.4GB total - Desktop only
# OLLAMA_MODEL = "minicpm-v:8b"  # 5.5GB vision
# SUBCONSCIOUS_MODEL = "Tohur/natsumura-storytelling-rp-llama-3.1:8b"  # 4.9GB language

# Option 2: LIGHTER VISION (good balance) - 10.4GB total  
# OLLAMA_MODEL = "minicpm-v:latest"  # 5.5GB vision (same as 8b currently)
# SUBCONSCIOUS_MODEL = "Tohur/natsumura-storytelling-rp-llama-3.1:8b"  # 4.9GB language

# Option 3: LIGHTER LANGUAGE (faster, keep vision quality) - 7.5GB total
# OLLAMA_MODEL = "minicpm-v:8b"  # 5.5GB vision
# SUBCONSCIOUS_MODEL = "llama3.2:3b"  # 2.0GB language - faster, less character

# Option 4: ULTRA LIGHT (fastest, experimental) - 3.5GB total
# OLLAMA_MODEL = "moondream:latest"  # 1.7GB vision - tiny but capable
# SUBCONSCIOUS_MODEL = "smollm2:1.7b"  # 1.8GB language - very fast

# Option 5: MOONDREAM + NATSUMURA (light vision, keep character) - 6.6GB total
# OLLAMA_MODEL = "moondream:latest"  # 1.7GB vision
# SUBCONSCIOUS_MODEL = "Tohur/natsumura-storytelling-rp-llama-3.1:8b"  # 4.9GB language

# Option 6: MOONDREAM + MISTRAL (light vision, better instruction following) - 6.1GB total
# OLLAMA_MODEL = "moondream:latest"  # 1.7GB vision - fast
# SUBCONSCIOUS_MODEL = "mistral:latest"  # 4.4GB language - better at following first-person instructions

# Option 7: MOONDREAM + LLAMA3.2 (balanced - fast with good instruction following) - 3.7GB total
# OLLAMA_MODEL = "moondream:latest"  # 1.7GB vision - fast
# SUBCONSCIOUS_MODEL = "llama3.2:3b"  # 2.0GB language - NOT DOWNLOADED YET

# Option 4: ULTRA LIGHT (fastest) - 3.5GB total ⭐ ACTIVE (for now)
OLLAMA_MODEL = "moondream:latest"  # 1.7GB vision
SUBCONSCIOUS_MODEL = "smollm2:1.7b"  # 1.8GB language - very fast

AI_PROCESS_INTERVAL = 8.0  # seconds between AI processing - slower for stability
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
ESPEAK_VOICE = "en-us+whisper"  # Voice with variants: en-us+whisper, en-gb+whisper, en+f3+whisper, etc.
ESPEAK_SPEED = 150  # Words per minute: 80-450 (faster = more natural whisper)
ESPEAK_PITCH = 50  # Pitch: 0-99 (neutral pitch sounds less demonic)

# Piper TTS Settings (if VOICE_ENGINE = "piper")
VOICE_MODEL = "en_US-kristin-medium"  # Voice model: kristin (F), ryan (M), lessac (F)

# Windows TTS Settings (if VOICE_ENGINE = "windows")
WINDOWS_TTS_RATE = 150  # Words per minute: 100=slow, 200=normal, 300=fast
WINDOWS_TTS_VOLUME = 0.9  # Volume: 0.0 to 1.0
WINDOWS_TTS_GENDER = "female"  # "male" or "female" (David or Zira)

# Common Voice Settings
VOICE_ALL_THOUGHTS = True  # Speak every thought (can be overwhelming!)
VOICE_INTERVAL = 30  # Speak every N seconds (if not speaking all thoughts)

# Lip Sync Settings (servo jaw control)
LIPSYNC_ENABLED = True  # Enable servo jaw lip sync
LIPSYNC_PORT = "COM3"  # Arduino serial port
LIPSYNC_BAUD = 9600  # Serial baud rate

# Camera Preview Settings  
SHOW_CAMERA_PREVIEW = True
PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600
SUBTITLE_DURATION = 8.0  # seconds to show each caption
MIN_CAPTION_INTERVAL = 5.0  # minimum seconds between captions