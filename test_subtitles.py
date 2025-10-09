"""
Test the subtitle overlay system with sample captions
"""
import cv2
import time
from camera import Camera
from config import SHOW_CAMERA_PREVIEW, PREVIEW_WIDTH, PREVIEW_HEIGHT


def test_subtitle_system():
    """Test subtitle overlay with sample AI responses"""
    print("🎬 Testing AI subtitle overlay system...")
    
    # Initialize camera with subtitle capability
    camera = Camera(
        show_preview=True,
        preview_width=PREVIEW_WIDTH,
        preview_height=PREVIEW_HEIGHT
    )
    
    if not camera.start():
        print("❌ Failed to start camera")
        return False
    
    # Sample AI inner monologue captions - mix of short and long to test live captioning style
    sample_captions = [
        "I see someone working.",
        "My mind drifts as I sit here. The room feels familiar yet distant.",
        "...still feeling withdrawn into melancholy. Can't shake the sad mood. Everything feels distant, detached. Person, working, computer—they seem so important yet unattainable.",
        "The lighting shifts subtly.",
        "I'm sitting in front of my computer again, staring at the screen. It's late and I can barely keep my eyes open. A pile of papers scattered across the desk tells the story of a productive but exhausting day.",
        "Something catches my attention. Movement in the periphery.",
        "There's something hypnotic about the way they move their hands across the keyboard. Each keystroke deliberate, purposeful. I wonder what thoughts flow through their mind as they work.",
        "Time seems to stretch and compress. Patterns emerge in the chaos.",
        "The colors in my vision have muted to soft blues and grays, like a hazy sky meets cold water. It's almost as if everything I see has taken on the hue of my inner emotional state."
    ]
    
    print("🎥 Camera preview with LIVE CAPTIONING style subtitles...")
    print("� Sentence-based chunks (1-2 sentences max)")
    print("⏱️  Organic pacing: ~3 words/second + natural pauses")
    print("🔄 Automatic flow between chunks with pause indicators")
    print("🔲 Press 'q' to quit, 's' to add subtitle, 'c' to clear")
    
    caption_index = 0
    last_caption_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Auto-add captions with dynamic timing based on current subtitle status
            subtitle_status = camera.get_subtitle_status()
            
            # Add new caption when queue is nearly empty (like live captions)
            should_add_caption = (
                subtitle_status['queue_length'] <= 2 and  # Keep buffer of 2 chunks
                current_time - last_caption_time >= 3.0   # Space out new thoughts
            ) or (
                subtitle_status['queue_length'] == 0 and
                current_time - last_caption_time >= 1.0
            )
            
            if should_add_caption:
                if caption_index < len(sample_captions):
                    caption = sample_captions[caption_index]
                    success = camera.add_subtitle(caption)
                    if success:
                        word_count = len(caption.split())
                        print(f"💭 Added caption {caption_index + 1} ({word_count} words): {caption[:40]}...")
                    caption_index = (caption_index + 1) % len(sample_captions)
                    last_caption_time = current_time
            
            # Show frame with subtitles
            if not camera.show_frame_with_subtitles("🤖 AI Inner Monologue - Subtitle Test"):
                print("⚠️ No frame available")
                time.sleep(0.01)
                continue
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("🛑 Quit requested")
                break
            elif key == ord('s'):
                # Manual subtitle addition
                test_caption = f"Manual test caption at {time.strftime('%H:%M:%S')}"
                camera.add_subtitle(test_caption)
                print(f"📝 Manual caption added: {test_caption}")
            elif key == ord('c'):
                # Clear current subtitle
                camera.current_subtitle = ""
                print("🧹 Subtitles cleared")
            
            # Brief pause
            time.sleep(0.033)  # ~30 FPS
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    
    finally:
        camera.stop()
        print("✅ Subtitle test complete")
    
    return True


if __name__ == "__main__":
    test_subtitle_system()