"""
Clean motor control system - abstraction for different motor types
"""
import json
import time
import serial
from config import MOTOR_TYPE, MOTOR_PORT, MOTOR_BAUD, DEBUG_MOTOR


class MotorController:
    """Clean motor control abstraction"""
    
    def __init__(self):
        self.motor_type = MOTOR_TYPE
        self.current_state = "calm_observant"
        self.connection = None
        
        if self.motor_type == "arduino":
            self._init_arduino()
        elif self.motor_type == "simulation":
            self._init_simulation()
        
        if DEBUG_MOTOR:
            print(f"Motor controller initialized: {self.motor_type}")
    
    def _init_arduino(self):
        """Initialize Arduino serial connection"""
        try:
            self.connection = serial.Serial(MOTOR_PORT, MOTOR_BAUD, timeout=1)
            time.sleep(2)  # Arduino reset delay
            if DEBUG_MOTOR:
                print(f"Arduino connected on {MOTOR_PORT}")
        except Exception as e:
            if DEBUG_MOTOR:
                print(f"Arduino connection failed: {e}")
            self.motor_type = "simulation"  # Fall back to simulation
    
    def _init_simulation(self):
        """Initialize simulation mode"""
        self.simulation_states = []
        if DEBUG_MOTOR:
            print("Motor simulation mode active")
    
    def set_emotional_state(self, emotion_name):
        """Set motor behavior based on emotional state"""
        if emotion_name == self.current_state:
            return  # No change needed
        
        old_state = self.current_state
        self.current_state = emotion_name
        
        if DEBUG_MOTOR:
            print(f"Motor: {old_state} → {emotion_name}")
        
        if self.motor_type == "arduino":
            self._send_arduino_command(emotion_name)
        elif self.motor_type == "simulation":
            self._simulate_movement(emotion_name)
    
    def _send_arduino_command(self, emotion_name):
        """Send command to Arduino"""
        if not self.connection:
            return
        
        try:
            # Map emotions to Arduino commands
            command_map = {
                "energized_engaged": "ENERGIZED\n",
                "alert_curious": "CURIOUS\n",
                "calm_observant": "CALM\n", 
                "quiet_detached": "QUIET\n",
                "withdrawn_distant": "WITHDRAWN\n"
            }
            
            command = command_map.get(emotion_name, "CALM\n")
            self.connection.write(command.encode())
            
            if DEBUG_MOTOR:
                print(f"Sent to Arduino: {command.strip()}")
                
        except Exception as e:
            if DEBUG_MOTOR:
                print(f"Arduino send error: {e}")
    
    def _simulate_movement(self, emotion_name):
        """Simulate motor movement for testing"""
        # Map emotions to movement descriptions
        movement_map = {
            "energized_engaged": {"speed": "fast", "amplitude": "large", "pattern": "dynamic"},
            "alert_curious": {"speed": "medium", "amplitude": "medium", "pattern": "scanning"},
            "calm_observant": {"speed": "slow", "amplitude": "small", "pattern": "gentle"},
            "quiet_detached": {"speed": "very_slow", "amplitude": "minimal", "pattern": "subtle"},
            "withdrawn_distant": {"speed": "stop", "amplitude": "none", "pattern": "still"}
        }
        
        movement = movement_map.get(emotion_name, movement_map["calm_observant"])
        self.simulation_states.append({
            'emotion': emotion_name,
            'movement': movement,
            'timestamp': time.time()
        })
        
        if DEBUG_MOTOR:
            print(f"Motor simulation: {movement}")
    
    def get_status(self):
        """Get current motor status"""
        status = {
            'type': self.motor_type,
            'current_state': self.current_state,
            'connected': self.connection is not None if self.motor_type == "arduino" else True
        }
        
        if self.motor_type == "simulation":
            status['simulation_history'] = len(self.simulation_states)
        
        return status
    
    def cleanup(self):
        """Clean up motor connections"""
        if self.connection:
            try:
                self.connection.close()
                if DEBUG_MOTOR:
                    print("Arduino connection closed")
            except:
                pass


# Pre-defined emotional states with movement patterns
EMOTIONAL_STATES = {
    "energized_engaged": {
        "description": "High energy, focused attention",
        "movement": "Dynamic, sweeping motions", 
        "duration_range": (5, 15),
        "triggers": ["high_confidence", "interesting_input", "positive_mood"]
    },
    "alert_curious": {
        "description": "Medium energy, exploring", 
        "movement": "Scanning, investigative motions",
        "duration_range": (8, 20),
        "triggers": ["new_input", "moderate_confidence", "learning_mode"]
    },
    "calm_observant": {
        "description": "Peaceful attention, default state",
        "movement": "Gentle, flowing motions",
        "duration_range": (10, 30), 
        "triggers": ["neutral_mood", "familiar_input", "stable_state"]
    },
    "quiet_detached": {
        "description": "Low energy, minimal interaction",
        "movement": "Subtle, minimal motions", 
        "duration_range": (15, 45),
        "triggers": ["low_confidence", "boring_input", "tired_state"]
    },
    "withdrawn_distant": {
        "description": "Very low energy, almost still",
        "movement": "Nearly motionless, occasional tiny movements",
        "duration_range": (20, 60),
        "triggers": ["very_low_mood", "no_input", "shutdown_mode"]
    }
}


def test_motor_system():
    """Test motor control system"""
    print("Testing motor control system...")
    
    motor = MotorController()
    print(f"✓ Motor initialized: {motor.get_status()}")
    
    # Test different emotional states
    test_emotions = ["energized_engaged", "alert_curious", "calm_observant", "quiet_detached"]
    
    for emotion in test_emotions:
        motor.set_emotional_state(emotion)
        time.sleep(0.5)  # Brief pause between states
    
    print(f"✓ State changes tested: {motor.get_status()}")
    
    # Test emotional state info
    print("\n📋 Available emotional states:")
    for state, info in EMOTIONAL_STATES.items():
        print(f"  {state}: {info['description']}")
    
    motor.cleanup()
    print("✓ Motor system test complete")
    return True


if __name__ == "__main__":
    test_motor_system()