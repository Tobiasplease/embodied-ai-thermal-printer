"""
Test different ways to get female whisper working
"""
import subprocess
import time

espeak = r"C:\Program Files\eSpeak NG\espeak-ng.exe"

print("\n🔊 Testing Female Voice Variants\n")
print("="*60)

tests = [
    ("en+f2", "Female variant f2"),
    ("en+f3", "Female variant f3"),
    ("en+f4", "Female variant f4"),
    ("en-us+f2", "US English female f2"),
    ("en+f2+whisper", "Female f2 with whisper"),
    ("en+f3+whisper", "Female f3 with whisper"),
    ("en+whisper+f2", "Whisper first, then female (reversed order)"),
    ("en+12", "Numbered variant 12"),
]

for voice, description in tests:
    print(f"\n{description}: '{voice}'")
    try:
        subprocess.run(
            [espeak, "-v", voice, "-s", "130", f"Testing {description}"],
            timeout=5,
            capture_output=True
        )
        time.sleep(0.8)
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*60)
print("✅ Test complete!")
