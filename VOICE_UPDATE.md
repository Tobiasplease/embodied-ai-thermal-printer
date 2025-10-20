"""
🔊 eSpeak TTS Integration - Male Whisper Voice
==============================================

WHAT'S NEW:
- eSpeak NG installed with built-in whisper mode
- Male whisper voice configured (en-us+whisper)
- Clean output - no more debug spam
- Simple, lo-fi aesthetic

VOICE SETTINGS (config.py):
```
VOICE_ENABLED = True
VOICE_ENGINE = "espeak"
ESPEAK_VOICE = "en-us+whisper"  # Male whisper
ESPEAK_SPEED = 130              # Slower for whisper
ESPEAK_PITCH = 45               # Deeper/masculine
```

AVAILABLE VOICE OPTIONS:
- "en-us"          - Normal male voice
- "en-us+whisper"  - Male whisper (CURRENT)
- "en+f3"          - Female voice (higher)
- "en+f4"          - Female voice (very high)
- "en+croak"       - Croaky/damaged voice
- "en+m2"          - Alternative male voice

TO CHANGE VOICE:
Edit config.py line: ESPEAK_VOICE = "your-choice"

OUTPUT CHANGES:
- DEBUG_CAMERA = False (no camera overlay spam)
- DEBUG_AI = False (no AI processing spam)
- Clean format: [HH:MM:SS] 💭 thought text

WHAT YOU'LL SEE:
```
[23:45:12] 💭 I see a keyboard and monitor on the desk

[23:45:19] 💭 Someone is sitting nearby, working late

[23:45:26] 💭 The room is dimly lit, feels quiet
```

And you'll HEAR the whisper voice speaking every 30 seconds.

TO TEST:
python main.py

NOTES:
- Female whisper (en+f3+whisper) doesn't work well - just sounds like pitched-down male
- The male whisper is iconic and works great
- eSpeak is much simpler than DSP processing - it just works!
