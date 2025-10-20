"""
Discover all available Windows TTS voices
"""
import pyttsx3

print("=" * 70)
print("AVAILABLE WINDOWS TTS VOICES")
print("=" * 70)
print()

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print(f"Found {len(voices)} voices installed:\n")

for i, voice in enumerate(voices, 1):
    print(f"{i}. {voice.name}")
    print(f"   ID: {voice.id}")
    print(f"   Languages: {voice.languages}")
    if hasattr(voice, 'gender'):
        print(f"   Gender: {voice.gender}")
    if hasattr(voice, 'age'):
        print(f"   Age: {voice.age}")
    print()

print("=" * 70)
print("TEST ALL VOICES")
print("=" * 70)
print()

test_text = "I notice the shadows on the wall. The room is quiet."

for i, voice in enumerate(voices, 1):
    print(f"Testing voice {i}: {voice.name}")
    engine.setProperty('voice', voice.id)
    engine.setProperty('rate', 150)
    engine.say(test_text)
    engine.runAndWait()
    print()

print("=" * 70)
print()
print("To use a specific voice, note its ID and update windows_tts.py")
print()
