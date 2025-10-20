"""
Test whisper mode vs normal voice
"""
import time
from voice import VoiceSystem

def test_whisper():
    print("=" * 70)
    print("WHISPER MODE TEST")
    print("=" * 70)
    print()
    
    voice = VoiceSystem(voice_model="en_US-lessac-medium")
    
    if not voice.piper_exe or not voice.model_path:
        print("❌ Voice system not available!")
        return
    
    voice.start()
    print()
    
    test_text = "I notice the shadows on the wall, shifting slowly as time passes."
    
    # Test 1: Normal voice
    print("🎤 TEST 1: Normal Voice")
    print(f"   Text: {test_text}")
    print("   Speaking...")
    voice.set_whisper_mode(False)
    voice.speak(test_text)
    time.sleep(8)
    
    print()
    
    # Test 2: Whisper mode
    print("🤫 TEST 2: Whisper Mode (breathier, slower)")
    print(f"   Text: {test_text}")
    print("   Speaking...")
    voice.set_whisper_mode(True)
    voice.speak(test_text)
    time.sleep(10)
    
    print()
    
    # Test 3: Different speeds
    print("⏱️ TEST 3: Speed variations")
    voice.set_whisper_mode(False)
    
    speeds = [
        (0.8, "Fast (0.8x)"),
        (1.0, "Normal (1.0x)"),
        (1.5, "Slow (1.5x)")
    ]
    
    for rate, description in speeds:
        print(f"   {description}: The room is very quiet.")
        voice.set_speech_rate(rate)
        voice.speak("The room is very quiet.")
        time.sleep(5)
    
    print()
    
    # Test 4: Mixed modes
    print("🎭 TEST 4: Mixed modes (per-speech override)")
    voice.set_whisper_mode(False)  # Default to normal
    
    print("   Normal: I'm observing the space around me.")
    voice.speak("I'm observing the space around me.", whisper=False)
    time.sleep(5)
    
    print("   Whisper override: But something feels different now.")
    voice.speak("But something feels different now.", whisper=True)
    time.sleep(6)
    
    print()
    print("⏳ Waiting for all speech to complete...")
    time.sleep(5)
    
    voice.stop()
    
    print()
    print("=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    print()
    print("Whisper mode effects:")
    print("  • Breathier, airier quality")
    print("  • Slower, more deliberate pace")
    print("  • More phoneme variation (natural whisper)")
    print("  • Longer pauses between sentences")
    print()
    print("Use cases:")
    print("  • Quiet observations")
    print("  • Vulnerable emotional states")
    print("  • Night time / low energy")
    print("  • Intimate or personal thoughts")

if __name__ == "__main__":
    try:
        test_whisper()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
