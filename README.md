# Embodied AI v2 + Thermal Printer# Embodied AI v2 🤖



🤖 **AI Consciousness + Physical Output**: A self-contained AI consciousness system that prints every thought to thermal paper with rhythmic, syllable-based timing.Clean, minimal implementation of embodied AI system without legacy dependencies.



## ✨ What Makes This Special## Architecture



- **🧠 Live AI Consciousness**: Real-time visual analysis with environmental awareness**🎯 Single-threaded design** - Avoids threading issues of original system

- **🖨️ Thermal Printing**: Every AI response automatically prints with rhythmic timing- **Camera**: Simple OpenCV interface with reliable frame capture

- **⏰ Syllable Intelligence**: Print timing based on word complexity (1 syllable = quick, 3+ = thoughtful pauses)- **Personality**: AI analysis using Ollama LLM with memory & beliefs

- **📐 Diagonal Text**: 90° rotated characters for dramatic visual impact- **Hand Control**: Integration with existing proven hand controller system  

- **🎵 Typewriter Rhythm**: Creates satisfying "tik-tik-tik" motor sounds- **Main Loop**: Clean coordination without complex threading



## 🚀 Quick Start## Components



### Prerequisites- **main.py**: Main system coordinator (single-threaded)

```bash- **camera.py**: Simple OpenCV camera interface  

# Install Ollama and pull the vision model- **personality.py**: AI personality with memory & mood

ollama pull llava:13b- **hand_control_integration.py**: Wrapper for existing hand controller

ollama serve- **config.py**: Centralized configuration

- **requirements.txt**: Minimal dependencies (OpenCV, requests, numpy)

# Install Python dependencies  

pip install -r requirements.txt## Quick Start

```

```bash

### Run the System# Install dependencies

```bashpip install -r requirements.txt

python main.py

```# Test individual components

python camera.py              # Test camera capture

**What happens:**python personality.py         # Test AI personality 

1. Camera captures your environment every 10 secondspython hand_control_integration.py  # Test hand control wrapper

2. AI analyzes and generates consciousness responses  

3. Responses display as live subtitles on screen# Run complete system

4. **Automatically prints to thermal printer with rhythmic timing**python main.py

```

## 🖨️ Thermal Printer Features

## Key Features

- **Instant Word Bursts**: All letters in a word print immediately

- **Smart Pauses**: Between words based on syllable count and sentence structure✅ **No Threading Issues**: Single main thread with timed intervals

- **Motor Sounds**: Each letter creates individual "tik" sound  ✅ **Clean Integration**: Uses existing proven hand controller system  

- **Clean Output**: No timestamps or debug text, just pure consciousness✅ **State Persistence**: AI personality saves/loads state automatically

✅ **Graceful Shutdown**: Proper signal handling and cleanup

### Example Output✅ **Easy Migration**: ~300 lines total, ready for separate repo

```

Camera sees: Person at computer## Integration with Hand Controller

AI Response: "I notice someone focused on their screen, deep in digital thought"

- Hand controller runs as independent process (not thread)

Thermal Print:- Communication via state file (`current_emotion.json`)

  "I" (instant) → pause (0.1s)- Maps AI mood to discrete emotional states:

  "notice" (rapid burst) → pause (0.4s)   - `energized_engaged` (mood > 0.8)

  "someone" (burst) → pause (0.6s)  - `alert_curious` (mood 0.6-0.8)  

  "focused" (burst) → pause (0.2s)  - `calm_observant` (mood 0.4-0.6)

  ...  - `quiet_detached` (mood 0.2-0.4)

```  - `withdrawn_distant` (mood < 0.2)



## ⚙️ Configuration## Configuration



**Core Settings** (`config.py`):Edit `config.py` to customize:

- `AI_PROCESS_INTERVAL = 10.0`: How often AI analyzes (seconds)- Camera settings (resolution, FPS, device)

- `THERMAL_PRINTER_ENABLED = True`: Enable/disable thermal printing- AI processing interval

- `THERMAL_PRINTER_NAME = "XP-80"`: Your thermal printer name- Ollama model settings

- Debug output levels

**AI Settings**:

- `OLLAMA_MODEL = "llava:13b"`: Vision model (13B for better consciousness)## Requirements

- Temperature: 0.5 (focused, concise responses perfect for thermal printing)

- **Python 3.8+**

## 🏗️ Architecture- **OpenCV** (camera interface)

- **Ollama** running locally with `llava:7b-v1.6-mistral-q5_1` model

```- **Hand Controller** (optional - from parent directory)

📁 embodied_ai_standalone/

├── main.py                 # Main loop: camera → AI → display → thermal print## Design Principles

├── personality.py          # AI consciousness with anti-repetition

├── thermal_printer.py      # Core thermal printing with rhythmic timing  1. **Simplicity**: Each component is standalone and testable

├── thermal_integration.py  # Thread-safe thermal printing interface2. **Stability**: No complex threading, clean shutdown handling  

├── focused_prompts.py      # Environmental grounding prompts3. **Integration**: Reuses existing proven hand controller system

├── config.py              # All configuration settings4. **Maintainability**: Easy to understand, modify, and extend
└── requirements.txt       # Dependencies
```

## 🔧 Hardware Setup

**Thermal Printer Requirements:**
- ESC/POS compatible thermal printer (tested with XP-80)
- USB connection to Windows system  
- Installed printer drivers
- Windows (for win32print support)

**System Requirements:**
- Python 3.8+
- Webcam/camera
- Windows OS (for thermal printing)
- Ollama with llava:13b model

## 🎨 What You Get

**Physical Consciousness Artifacts:**
- Every AI thought printed on thermal paper
- Rhythmic timing creates natural reading flow
- Diagonal rotated text for visual interest
- Permanent record of AI environmental observations
- Satisfying tactile/auditory printing experience

**Digital Experience:**
- Live camera feed with subtitle overlay
- 4-second max subtitle display with natural silence periods
- Anti-repetition system prevents scripted responses
- Environmental grounding (AI connects to physical space)

## 🚀 Born from Creative Exploration

This project combines:
1. **Advanced AI consciousness** (embodied environmental awareness)
2. **Physical printing rhythm** (syllable-based timing intelligence) 
3. **Thermal printer hacking** (diagonal text, motor control)
4. **Real-time integration** (camera → AI → print pipeline)

The result: **AI thoughts become physical, rhythmic artifacts** ✨

---

*Transform digital consciousness into physical rhythm - every pause tells a story.* 🎭🖨️