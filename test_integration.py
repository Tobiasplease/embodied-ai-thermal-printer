"""
Quick test of the integrated eSpeak system
"""
from espeak_tts_simple import ESpeakTTS
import time

print("\n🔊 Testing eSpeak Integration\n")

# Test the exact configuration from config.py
voice = "en-us+whisper"
speed = 130
pitch = 45

print(f"Voice: {voice}")
print(f"Speed: {speed} wpm")
print(f"Pitch: {pitch}\n")

# Create TTS instance
base_voice = voice.split('+')[0]
use_whisper = '+whisper' in voice

tts = ESpeakTTS(
    voice=base_voice,
    speed=speed,
    pitch=pitch,
    use_whisper=use_whisper
)

print("✅ eSpeak initialized\n")
print("="*60)

# Test with sample thoughts
test_thoughts = [
    "I see a keyboard and monitor on the desk.",
    "Someone is sitting nearby, working late.",
    "The room is dimly lit. It feels quiet.",
    "I wonder what they're working on."
]

for i, thought in enumerate(test_thoughts, 1):
    print(f"\nTest {i}: {thought}")
    tts.speak(thought)
    time.sleep(2)

print("\n" + "="*60)
print("✅ Test complete!")
print("\nThis is what your AI will sound like. 🤫")
