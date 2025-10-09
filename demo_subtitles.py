"""
Quick demo of the AI inner monologue subtitle system
"""
from main import EmbodiedAI
import time

def demo_ai_subtitles():
    """Demo the complete AI system with live subtitles"""
    print("🎬 Starting AI Inner Monologue Demo")
    print("📺 Camera window will show live AI thoughts as subtitles")
    print("🔲 Press 'q' in camera window to quit")
    print("⚡ AI will analyze every 3 seconds and show thoughts")
    print()
    
    # Create and start the AI system
    ai_system = EmbodiedAI()
    
    if not ai_system.initialize():
        print("❌ Failed to initialize AI system")
        return
    
    print("🚀 Starting AI inner monologue...")
    print("💭 Watch the camera window for live AI thoughts!")
    
    try:
        # Run for demo period
        ai_system.run()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    finally:
        ai_system.shutdown()
        print("✅ Demo complete")

if __name__ == "__main__":
    demo_ai_subtitles()