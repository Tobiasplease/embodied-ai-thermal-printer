# Configuration for Embodied AI v2
# Simple, single-source configuration

# Camera Settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640  
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# AI Settings
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llava:13b"  # Upgraded to 13B for better consciousness quality
AI_PROCESS_INTERVAL = 10.0  # seconds between AI processing (increased for 13B + sophisticated prompts)
USE_SOPHISTICATED_PROMPTS = False  # Testing hybrid focus-aware legacy system
OLLAMA_TIMEOUT = 120  # seconds - increase for complex prompts

# Personality Settings
MEMORY_SIZE = 100  # number of observations to remember
BELIEF_THRESHOLD = 0.7  # confidence needed to form beliefs
PERSONALITY_SAVE_FILE = "personality_state.json"

# Motor Settings  
MOTOR_TYPE = "simulation"  # or "arduino", "servo", etc.
MOTOR_PORT = "COM3"  # for hardware controllers
MOTOR_BAUD = 9600

# Debug Settings
DEBUG_CAMERA = True
DEBUG_AI = True
DEBUG_MOTOR = False
VERBOSE_OUTPUT = True

# Camera Preview Settings  
SHOW_CAMERA_PREVIEW = True
PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600
SUBTITLE_DURATION = 8.0  # seconds to show each caption
MIN_CAPTION_INTERVAL = 5.0  # minimum seconds between captions