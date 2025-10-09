"""
Clean hand control integration - minimal wrapper around existing perfect system
"""
import json
import time
import subprocess
import os
from pathlib import Path
from config import MOTOR_TYPE, DEBUG_MOTOR


class HandControlInterface:
    """Clean interface to existing hand control system"""
    
    def __init__(self):
        self.current_emotion = "calm_observant"
        self.last_update_time = 0
        self.update_interval = 2.0  # Don't spam updates
        
        # Path to hand control state file
        self.state_file = Path(__file__).parent.parent / "hand_control" / "current_emotion.json"
        
        # Hand control process (if we want to launch it)
        self.hand_process = None
        
        if DEBUG_MOTOR:
            print(f"Hand control interface initialized")
            print(f"State file: {self.state_file}")
    
    def set_emotion(self, emotion_name, mood_value=0.5):
        """Set emotional state for hand controller"""
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return False
        
        if emotion_name == self.current_emotion:
            return False  # No change
        
        # Update state
        old_emotion = self.current_emotion
        self.current_emotion = emotion_name
        self.last_update_time = current_time
        
        # Write to state file for hand controller to read
        try:
            state_data = {
                'emotion_state': emotion_name,
                'mood_value': mood_value,
                'timestamp': current_time,
                'source': 'embodied_ai_v2'
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            if DEBUG_MOTOR:
                print(f"Motor: {old_emotion} → {emotion_name} (mood: {mood_value:.2f})")
            
            return True
            
        except Exception as e:
            if DEBUG_MOTOR:
                print(f"Failed to update hand controller state: {e}")
            return False
    
    def launch_hand_controller(self, headless=True):
        """Launch the hand controller process if not running"""
        if self.hand_process and self.hand_process.poll() is None:
            if DEBUG_MOTOR:
                print("Hand controller already running")
            return True
        
        try:
            hand_dir = Path(__file__).parent.parent / "hand_control"
            
            if headless:
                # Launch in headless mode 
                cmd = ["python", "hand_control_interface.py", "--headless"]
            else:
                # Launch with GUI
                cmd = ["python", "hand_control_interface.py"]
            
            self.hand_process = subprocess.Popen(
                cmd,
                cwd=hand_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if headless else 0
            )
            
            if DEBUG_MOTOR:
                mode = "headless" if headless else "GUI"
                print(f"Hand controller launched in {mode} mode (PID: {self.hand_process.pid})")
            
            return True
            
        except Exception as e:
            if DEBUG_MOTOR:
                print(f"Failed to launch hand controller: {e}")
            return False
    
    def is_running(self):
        """Check if hand controller process is running"""
        if not self.hand_process:
            return False
        return self.hand_process.poll() is None
    
    def get_status(self):
        """Get current hand controller status"""
        return {
            'current_emotion': self.current_emotion,
            'last_update_time': self.last_update_time,
            'is_running': self.is_running(),
            'pid': self.hand_process.pid if self.hand_process else None
        }
    
    def cleanup(self):
        """Clean shutdown of hand controller"""
        if self.hand_process:
            try:
                self.hand_process.terminate()
                # Give it a moment to shutdown gracefully
                try:
                    self.hand_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.hand_process.kill()  # Force kill if needed
                    
                if DEBUG_MOTOR:
                    print("Hand controller process terminated")
                    
            except Exception as e:
                if DEBUG_MOTOR:
                    print(f"Error during hand controller cleanup: {e}")


# Map personality emotions to hand controller emotions
EMOTION_MAP = {
    'energized_engaged': 'energized_engaged',
    'alert_curious': 'alert_curious', 
    'calm_observant': 'calm_observant',
    'quiet_detached': 'quiet_detached',
    'withdrawn_distant': 'withdrawn_distant'
}

def personality_to_hand_emotion(personality_suggestion):
    """Map personality system suggestion to hand controller emotion"""
    return EMOTION_MAP.get(personality_suggestion, 'calm_observant')


def test_hand_control():
    """Test hand control integration"""
    print("Testing hand control integration...")
    
    hand = HandControlInterface()
    print(f"✓ Interface created: {hand.get_status()}")
    
    # Test emotion switching
    test_emotions = ['energized_engaged', 'alert_curious', 'calm_observant', 'quiet_detached']
    
    for emotion in test_emotions:
        success = hand.set_emotion(emotion, mood_value=0.7)
        print(f"✓ Set emotion {emotion}: {success}")
        time.sleep(1)  # Brief pause
    
    print(f"✓ Final status: {hand.get_status()}")
    
    # Don't launch process in test - just test the interface
    print("✓ Hand control integration test complete")
    return True


if __name__ == "__main__":
    test_hand_control()