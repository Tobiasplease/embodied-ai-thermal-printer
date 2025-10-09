"""
Quick test of the fixed main system
"""
import time
from main import EmbodiedAI

def test_fixed_system():
    """Test the fixed system with direct camera access"""
    print("🎬 Testing fixed embodied AI system...")
    print("📹 Should show smooth video feed")
    print("💭 Should show yellow subtitles when AI processes")
    print("🔲 Press 'q' in camera window to quit")
    
    ai = EmbodiedAI()
    
    try:
        ai.run()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    finally:
        ai.shutdown()
        print("✅ Test complete")

if __name__ == "__main__":
    test_fixed_system()