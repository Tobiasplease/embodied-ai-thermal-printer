# Voice System - Quick Reference

## Current Status
✅ Voice system integrated into main.py
✅ Fully toggleable via config.py
✅ Non-blocking async operation
✅ Won't interfere with existing systems

## Quick Toggle

### Enable Voice:
```python
# In config.py
VOICE_ENABLED = True
VOICE_ALL_THOUGHTS = False  # Speak every 30s (configurable)
VOICE_INTERVAL = 30  # seconds between speaking
```

### Disable Voice:
```python
# In config.py
VOICE_ENABLED = False  # That's it!
```

## Voice Modes

### Mode 1: Selective Speaking (Recommended)
```python
VOICE_ENABLED = True
VOICE_ALL_THOUGHTS = False
VOICE_INTERVAL = 30  # Speak every 30 seconds
```
- Less overwhelming
- Good for long sessions
- Highlights key moments

### Mode 2: Continuous Speaking
```python
VOICE_ENABLED = True
VOICE_ALL_THOUGHTS = True
VOICE_INTERVAL = 30  # Ignored in this mode
```
- Speaks every thought (every 7 seconds)
- Very immersive
- Can be intense!

## Testing

### Before enabling in main system:
```bash
python test_voice.py
```

This will test if Piper is installed and working.

### Without Piper installed:
System will gracefully disable voice and continue normally.
No errors, no crashes - just prints a warning.

## What Gets Spoken

The voice system automatically:
- ✅ Removes timestamps `[12:34:56]`
- ✅ Removes emoji 🎯🧠💭
- ✅ Removes debug markers `[DEBUG]`
- ✅ Normalizes whitespace
- ✅ Speaks clean, natural text

## Integration Points

Voice triggers after:
1. AI generates thought
2. Caption is cleaned
3. Thermal printer receives it
4. **Then voice speaks (if enabled)**

No interference with existing systems!

## Performance Impact

- Voice synthesis: ~100-200ms per sentence
- Runs in background thread (non-blocking)
- Zero impact on camera/AI/subtitle timing
- Async queue handles multiple requests

## Troubleshooting

### "Voice system disabled (Piper not found)"
- Run `test_voice.py` to see what's missing
- Check VOICE_SETUP.md for installation steps
- Piper should be in `./piper/piper.exe`

### "Voice system disabled (config)"
- VOICE_ENABLED is set to False in config.py
- This is normal if you haven't enabled it yet

### No sound but no errors
- Check Windows volume
- Verify Piper works: `test_voice.py`
- Check speaker/headphone connection

## Voice Models Available

Default: **en_US-lessac-medium** (female, clear)

Others you can try:
- `en_US-ryan-high` - Male, expressive
- `en_US-amy-medium` - Female, natural
- `en_US-libritts-high` - Very natural but larger

Change in config.py:
```python
VOICE_MODEL = "en_US-ryan-high"
```

## Quick Commands

```bash
# Test voice system
python test_voice.py

# Run AI with voice enabled
# (First set VOICE_ENABLED = True in config.py)
python main.py

# Voice system will auto-start if Piper is detected
```

## Integration Status

✅ Imported in main.py (line ~24)
✅ Initialized in __init__ (line ~113)
✅ Started in initialize() (line ~165)
✅ Speaks after AI processing (line ~358)
✅ Cleanup in shutdown() (line ~632)

All integration points are **conditional** - system works fine without voice!
