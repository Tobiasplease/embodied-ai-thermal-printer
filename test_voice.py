"""
Quick test script for voice system
Run this to verify voice setup before enabling in main system
"""
import time
from voice import VoiceSystem
from config import VOICE_MODEL

def test_voice():
    print("=" * 60)
    print("VOICE SYSTEM TEST")
    print("=" * 60)
    
    # Initialize voice system with config setting
    print(f"\nTesting voice: {VOICE_MODEL}")
    voice = VoiceSystem(voice_model=VOICE_MODEL)
    
    if not voice.piper_exe or not voice.model_path:
        print("\n❌ Voice system not available!")
        print("\n📥 SETUP INSTRUCTIONS:")
        print("1. Download Piper: https://github.com/rhasspy/piper/releases")
        print("2. Extract to './piper/' directory")
        print("3. Download voice model from: https://huggingface.co/rhasspy/piper-voices")
        print("4. Place .onnx and .json files in './piper/models/'")
        print("\nSee VOICE_SETUP.md for detailed instructions")
        return False
    
    # Start the voice system
    print("\n🔊 Starting voice system...")
    if not voice.start():
        print("❌ Failed to start voice system")
        return False
    
    print("✅ Voice system started successfully!\n")
    
    # Test speeches
    test_phrases = [
        "Hello, I am the embodied AI.",
        "I can see through the camera and speak my thoughts.",
        "This is a test of the text to speech system.",
        "The room is quiet and still."
    ]
    
    print("🎙️ Testing speech output...\n")
    for i, phrase in enumerate(test_phrases, 1):
        print(f"   {i}. Speaking: {phrase}")
        voice.speak(phrase)
        time.sleep(0.5)  # Small delay between queuing
    
    print("\n⏳ Waiting for speech to complete (this may take 15-20 seconds)...")
    
    # Wait for all speech to complete
    time.sleep(20)
    
    # Check if still speaking
    if voice.is_speaking:
        print("   Still speaking... waiting a bit more...")
        time.sleep(10)
    
    # Stop the voice system
    print("\n🔇 Stopping voice system...")
    voice.stop()
    
    print("\n" + "=" * 60)
    print("✅ VOICE SYSTEM TEST COMPLETE")
    print("=" * 60)
    print("\nIf you heard the test phrases spoken aloud, the system is working!")
    print("You can now enable voice in config.py by setting VOICE_ENABLED = True")
    
    return True

if __name__ == "__main__":
    try:
        test_voice()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
