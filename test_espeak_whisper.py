"""
Quick test of eSpeak whisper mode
"""
import subprocess
import time

espeak = r"C:\Program Files\eSpeak NG\espeak-ng.exe"

print("\n🔊 eSpeak Whisper Test\n")
print("="*60)

# Test 1: Normal
print("\n1. Normal voice:")
subprocess.run([espeak, "-v", "en-us", "-s", "150", "Hello, this is my normal voice."])
time.sleep(1)

# Test 2: Whisper
print("\n2. Whisper mode:")
subprocess.run([espeak, "-v", "en-us+whisper", "-s", "130", "Now I am whispering to you."])
time.sleep(1)

# Test 3: Female voice (normal)
print("\n3. Female voice (normal):")
subprocess.run([espeak, "-v", "en+f3", "-s", "140", "This is a female voice."])
time.sleep(1)

# Test 4: Female whisper (combining variants)
print("\n4. Female whisper:")
subprocess.run([espeak, "-v", "en+f3+whisper", "-s", "120", "Now I am a female whispering."])
time.sleep(1)

# Test 5: Higher pitched female whisper
print("\n5. Higher pitched female whisper:")
subprocess.run([espeak, "-v", "en+f4+whisper", "-p", "60", "-s", "115", "I sound more delicate."])
time.sleep(1)

# Test 6: Croak
print("\n6. Croaky voice:")
subprocess.run([espeak, "-v", "en-us+croak", "-s", "140", "I sound broken and glitchy."])

print("\n" + "="*60)
print("✅ Test complete!")
print("\n💡 Voice variant combinations that work:")
print("   en+f1, en+f2, en+f3, en+f4  - Female variants (f3/f4 higher pitched)")
print("   en+m1, en+m2, en+m3         - Male variants")
print("   +whisper                    - Whisper mode")
print("   +croak                      - Croaky/damaged voice")
print("   Combine: en+f3+whisper      - Female whispering")
print("\n   Adjust pitch (-p 0-99) for more variation!")
