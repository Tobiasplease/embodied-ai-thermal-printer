# Embodied AI v2 🤖

Clean, minimal implementation of embodied AI system without legacy dependencies.

## Architecture

**🎯 Single-threaded design** - Avoids threading issues of original system
- **Camera**: Simple OpenCV interface with reliable frame capture
- **Personality**: AI analysis using Ollama LLM with memory & beliefs
- **Hand Control**: Integration with existing proven hand controller system  
- **Main Loop**: Clean coordination without complex threading

## Components

- **main.py**: Main system coordinator (single-threaded)
- **camera.py**: Simple OpenCV camera interface  
- **personality.py**: AI personality with memory & mood
- **hand_control_integration.py**: Wrapper for existing hand controller
- **config.py**: Centralized configuration
- **requirements.txt**: Minimal dependencies (OpenCV, requests, numpy)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test individual components
python camera.py              # Test camera capture
python personality.py         # Test AI personality 
python hand_control_integration.py  # Test hand control wrapper

# Run complete system
python main.py
```

## Key Features

✅ **No Threading Issues**: Single main thread with timed intervals
✅ **Clean Integration**: Uses existing proven hand controller system  
✅ **State Persistence**: AI personality saves/loads state automatically
✅ **Graceful Shutdown**: Proper signal handling and cleanup
✅ **Easy Migration**: ~300 lines total, ready for separate repo

## Integration with Hand Controller

- Hand controller runs as independent process (not thread)
- Communication via state file (`current_emotion.json`)
- Maps AI mood to discrete emotional states:
  - `energized_engaged` (mood > 0.8)
  - `alert_curious` (mood 0.6-0.8)  
  - `calm_observant` (mood 0.4-0.6)
  - `quiet_detached` (mood 0.2-0.4)
  - `withdrawn_distant` (mood < 0.2)

## Configuration

Edit `config.py` to customize:
- Camera settings (resolution, FPS, device)
- AI processing interval
- Ollama model settings
- Debug output levels

## Requirements

- **Python 3.8+**
- **OpenCV** (camera interface)
- **Ollama** running locally with `llava:7b-v1.6-mistral-q5_1` model
- **Hand Controller** (optional - from parent directory)

## Design Principles

1. **Simplicity**: Each component is standalone and testable
2. **Stability**: No complex threading, clean shutdown handling  
3. **Integration**: Reuses existing proven hand controller system
4. **Maintainability**: Easy to understand, modify, and extend