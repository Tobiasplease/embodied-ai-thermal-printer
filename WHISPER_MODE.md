# 🤫 Whisper Mode - Quick Guide

## What is Whisper Mode?

Whisper mode makes the AI speak in a quieter, more intimate, breathier voice - like actually whispering. Perfect for creating different emotional atmospheres!

## How to Enable

### Simple Toggle (config.py):
```python
VOICE_WHISPER_MODE = True  # Enable whisper by default
```

### Dynamic Control (in code):
```python
# Set whisper mode for all speech
voice_system.set_whisper_mode(True)

# Override per-speech
voice_system.speak("A secret thought", whisper=True)
voice_system.speak("A loud thought", whisper=False)
```

## Technical Details

### Whisper Parameters:
- **Noise Scale**: 0.9 (vs 0.667 normal) - More breath, airier quality
- **Length Scale**: 1.3 (vs 1.0 normal) - 30% slower, more deliberate
- **Noise W**: 1.0 (vs 0.8 normal) - More phoneme variation (natural whisper)
- **Sentence Silence**: 0.3s - Slightly longer pauses

### Normal Voice Parameters:
- **Noise Scale**: 0.667 - Clear articulation
- **Length Scale**: Configurable (default 1.0)
- **Noise W**: 0.8 - Standard variation
- **Sentence Silence**: 0.3s

## Use Cases for Whisper Mode

### 🌙 Time-Based
- **Night time** (after 10pm): Auto-enable whisper
- **Early morning** (before 7am): Gentle whisper mode
- **Quiet hours**: Respectful of environment

### 💭 Emotional States
- **Vulnerable emotions**: scared, uncertain, fragile
- **Intimate thoughts**: personal reflections, secrets
- **Low energy**: tired, numb, dissociative
- **Contemplative**: deep thought, philosophical

### 📍 Environmental
- **Small enclosed spaces**: Whispering feels natural
- **Someone sleeping nearby**: Respectful awareness
- **Library/quiet mode**: Context-appropriate
- **Long stasis**: Whisper during extended observation

### 🎭 Dramatic Effect
- **Building tension**: Normal → whisper
- **Revealing secrets**: "I notice something..."
- **Intimate observations**: Personal discoveries
- **Vulnerability moments**: Emotional rawness

## Configuration Examples

### Example 1: Always Whisper
```python
# config.py
VOICE_WHISPER_MODE = True
VOICE_SPEECH_RATE = 1.2  # Slightly slower
```

### Example 2: Time-Based Whisper
```python
# In main.py, before speaking:
import datetime
current_hour = datetime.datetime.now().hour

# Whisper at night
is_night = current_hour >= 22 or current_hour <= 6
if voice_system:
    voice_system.set_whisper_mode(is_night)
```

### Example 3: Emotion-Based Whisper
```python
# In personality.py, when generating speech:
whisper_emotions = ["scared", "uncertain", "vulnerable", "tired", 
                    "numb", "hollow", "fragile", "intimate"]

use_whisper = current_emotional_state in whisper_emotions
voice_system.speak(thought, whisper=use_whisper)
```

### Example 4: Stasis Duration Whisper
```python
# After long periods staring at same thing, whisper
stasis_minutes = (time.time() - last_significant_change_time) / 60

# Whisper after 60+ minutes of same view
if stasis_minutes > 60:
    voice_system.set_whisper_mode(True)
else:
    voice_system.set_whisper_mode(False)
```

## Speech Rate Control

Works with both normal and whisper modes:

```python
# config.py
VOICE_SPEECH_RATE = 1.0   # Normal speed
VOICE_SPEECH_RATE = 0.8   # 25% faster
VOICE_SPEECH_RATE = 1.5   # 50% slower
VOICE_SPEECH_RATE = 2.0   # 2x slower (very deliberate)
```

**Note**: Whisper mode already includes 1.3x slowdown. If you set `VOICE_SPEECH_RATE = 1.5` and enable whisper, it will be VERY slow (deliberate effect).

## Combining Effects

### Exhausted AI:
```python
VOICE_WHISPER_MODE = True
VOICE_SPEECH_RATE = 1.8  # Very slow + whisper = exhausted
```

### Anxious AI:
```python
VOICE_WHISPER_MODE = False
VOICE_SPEECH_RATE = 0.7  # Fast speech, normal volume
```

### Contemplative AI:
```python
VOICE_WHISPER_MODE = True
VOICE_SPEECH_RATE = 1.5  # Slow whisper = deep thought
```

### Excited/Manic AI:
```python
VOICE_WHISPER_MODE = False
VOICE_SPEECH_RATE = 0.6  # Very fast, clear voice
```

## Testing

```bash
# Test whisper vs normal
python test_whisper.py

# Test in main system
# 1. Enable in config:
VOICE_WHISPER_MODE = True

# 2. Run:
python main.py
```

## Advanced: Dynamic Emotional Voice

Want voice to match AI's emotional state automatically? Add to `main.py` before `voice_system.speak()`:

```python
# Get current emotional state from personality
mood_value = self.personality.current_mood
emotional_state = self.personality.emotional_state.get("state", "neutral")

# Map emotion to voice settings
if emotional_state in ["scared", "vulnerable", "uncertain"]:
    use_whisper = True
    speech_rate = 1.4  # Slow, uncertain
elif emotional_state in ["tired", "numb", "hollow"]:
    use_whisper = True
    speech_rate = 1.8  # Very slow, exhausted
elif emotional_state in ["anxious", "manic", "frantic"]:
    use_whisper = False
    speech_rate = 0.7  # Fast, agitated
elif emotional_state in ["contemplative", "philosophical"]:
    use_whisper = True
    speech_rate = 1.3  # Measured, thoughtful
else:
    use_whisper = False
    speech_rate = 1.0  # Normal

# Apply settings
self.voice_system.set_speech_rate(speech_rate)
self.voice_system.speak(clean_caption, whisper=use_whisper)
```

## Current Status

✅ Whisper mode implemented
✅ Dynamic per-speech override
✅ Speech rate control
✅ Config integration
✅ Test script ready

Default settings:
- `VOICE_WHISPER_MODE = False` (normal voice)
- `VOICE_SPEECH_RATE = 1.0` (normal speed)

Change anytime in `config.py`!
