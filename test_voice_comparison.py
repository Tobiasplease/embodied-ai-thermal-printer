"""
Compare male vs female voices for embodied AI
"""
import time
from voice import VoiceSystem

def test_voice_comparison():
    print("=" * 70)
    print("VOICE COMPARISON TEST")
    print("=" * 70)
    print()
    
    test_phrases = [
        "I'm observing the room around me.",
        "Something feels different now.",
        "The silence is heavy and thick.",
        "I notice the shadows shifting on the wall."
    ]
    
    voices = [
        ("en_US-kristin-medium", "Female - Expressive, emotional (60 MB)"),
        ("en_US-ryan-high", "Male - Expressive, dynamic (115 MB, higher quality)")
    ]
    
    for voice_model, description in voices:
        print(f"🎤 Testing: {voice_model}")
        print(f"   {description}")
        print()
        
        voice = VoiceSystem(voice_model=voice_model)
        
        if not voice.piper_exe or not voice.model_path:
            print(f"   ❌ Voice model not found: {voice_model}")
            print(f"   Run: python download_voices.py")
            print()
            continue
        
        voice.start()
        
        for phrase in test_phrases:
            print(f"   Speaking: {phrase}")
            voice.speak(phrase)
            time.sleep(0.5)
        
        print()
        print("   ⏳ Waiting for speech to complete...")
        time.sleep(15)
        
        voice.stop()
        print()
        print("-" * 70)
        print()
    
    print("=" * 70)
    print("COMPARISON COMPLETE")
    print("=" * 70)
    print()
    print("Consider:")
    print()
    print("FEMALE (Kristin):")
    print("  ✅ Same performance as original")
    print("  ✅ Expressive and emotional")
    print("  ✅ Natural for vulnerability/intimacy")
    print("  ? Traditional 'assistant' associations")
    print()
    print("MALE (Ryan):")
    print("  ⚠️  Slightly slower (~50-100ms more)")
    print("  ✅ Higher quality audio")
    print("  ✅ More dynamic range")
    print("  ✅ Less 'assistant' stereotype")
    print("  ? Depends on your preference")
    print()
    print("Performance impact:")
    print("  • Kristin: ~200ms synthesis (same as lessac)")
    print("  • Ryan: ~250-300ms synthesis (still fast enough)")
    print()
    print("For 7-second AI intervals, both are real-time capable!")
    print()
    print("Update config.py with your choice:")
    print('  VOICE_MODEL = "en_US-kristin-medium"  # Female')
    print('  VOICE_MODEL = "en_US-ryan-high"       # Male')
    print()

if __name__ == "__main__":
    try:
        test_voice_comparison()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
