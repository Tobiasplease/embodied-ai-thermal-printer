"""
Test continuous video feed to verify smooth playback
"""
import cv2
import time
from camera import Camera
from config import SHOW_CAMERA_PREVIEW, PREVIEW_WIDTH, PREVIEW_HEIGHT


def test_continuous_video():
    """Test that camera shows smooth continuous video"""
    print("📹 Testing continuous video feed...")
    
    camera = Camera(
        show_preview=True,
        preview_width=PREVIEW_WIDTH,
        preview_height=PREVIEW_HEIGHT
    )
    
    if not camera.start():
        print("❌ Failed to start camera")
        return False
    
    print("🎥 Showing continuous video feed...")
    print("📺 Should see smooth real-time video (not still frames)")
    print("🔲 Press 'q' to quit")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Get fresh frame and show it
            if camera.show_frame_with_subtitles("📹 Continuous Video Test"):
                frame_count += 1
                
                # Show FPS every 30 frames
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    print(f"📊 FPS: {fps:.1f} (Frame {frame_count})")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("🛑 Quit requested")
                    break
            else:
                print("⚠️ No frame available")
                time.sleep(0.01)
            
            # Target 30 FPS
            time.sleep(0.033)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    
    finally:
        camera.stop()
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"✅ Test complete - Avg FPS: {avg_fps:.1f}")
    
    return True


if __name__ == "__main__":
    test_continuous_video()