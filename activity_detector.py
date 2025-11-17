"""
Simple, robust activity detection using background subtraction

Uses OpenCV's MOG2 background subtractor which handles:
- Camera noise
- Gradual lighting changes
- Auto-exposure adjustments

Much simpler than multi-signal consensus.
"""

import cv2
import numpy as np
import time
from collections import deque


class ActivityDetector:
    """Simple background subtraction activity detector"""

    def __init__(self):
        """Initialize with background subtractor"""
        # MOG2 learns background over time, tolerates noise
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,  # Learn from last 500 frames (~16 seconds)
            varThreshold=16,  # Sensitivity (lower = more sensitive)
            detectShadows=False  # Shadows aren't movement
        )

        # Simple activity tracking
        self.activity_history = deque(maxlen=10)
        self.last_high_activity_time = 0

        # Calibration
        self.frames_processed = 0
        self.calibration_frames = 30  # Learn background for 1 second

    def analyze_frame(self, frame) -> dict:
        """
        Analyze frame for activity

        Returns:
            dict with activity_score, is_real_movement, response_mode
        """
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)

        # Calculate percentage of foreground pixels
        total_pixels = fg_mask.shape[0] * fg_mask.shape[1]
        fg_pixels = np.count_nonzero(fg_mask)
        fg_percentage = (fg_pixels / total_pixels) * 100

        self.frames_processed += 1

        # During calibration, just learn background
        if self.frames_processed < self.calibration_frames:
            print(f"📊 Calibrating background model: {self.frames_processed}/{self.calibration_frames}")
            return {
                'activity_score': 0.0,
                'fg_percentage': fg_percentage,
                'is_real_movement': False,
                'calibrating': True,
                'response_mode': 'normal',
                'suggested_delay': 3.0
            }

        # Track activity history
        self.activity_history.append(fg_percentage)

        # Calculate activity score
        # RAISED THRESHOLDS: Person detector handles subtle arrivals
        # This only triggers on significant motion
        if fg_percentage > 15:
            activity_score = min(100, 60 + fg_percentage * 2)
        elif fg_percentage > 5:
            activity_score = 30 + fg_percentage * 2
        else:
            activity_score = fg_percentage * 3

        # Check if sustained over multiple frames
        # RAISED: average >30% over 3 frames = real movement (person detector handles subtle changes)
        # High threshold allows static_duration to accumulate during normal fidgeting
        if len(self.activity_history) >= 3:
            recent_avg = np.mean(list(self.activity_history)[-3:])
            is_real_movement = recent_avg > 30.0
        else:
            is_real_movement = False

        # Classify response mode
        response_mode, delay = self._classify_activity(activity_score, is_real_movement)

        # Debug output (suppressed to reduce terminal clutter)
        # if fg_percentage > 1:
        #     print(f"📊 Activity: {fg_percentage:.1f}% changed | score: {activity_score:.0f} | movement: {is_real_movement}")

        return {
            'activity_score': float(activity_score),
            'fg_percentage': float(fg_percentage),
            'is_real_movement': is_real_movement,
            'calibrating': False,
            'response_mode': response_mode,
            'suggested_delay': delay
        }

    def _classify_activity(self, score, is_real_movement):
        """Classify activity and suggest timing"""
        current_time = time.time()

        if is_real_movement and score > 60:
            self.last_high_activity_time = current_time
            return 'immediate', 0.5
        elif is_real_movement and score > 30:
            self.last_high_activity_time = current_time
            return 'normal', 2.0
        elif score > 20:
            return 'sparse', 8.0
        else:
            # Static scene
            time_since = current_time - self.last_high_activity_time
            if time_since < 60:
                return 'contemplative', 20.0
            elif time_since < 180:
                return 'introspective', 45.0
            else:
                return 'dreamlike', 60.0

    def reset(self):
        """Reset detector"""
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=False
        )
        self.activity_history.clear()
        self.frames_processed = 0


# Test code
if __name__ == "__main__":
    print("Testing simple activity detector with webcam...")
    print("Using background subtraction (MOG2)\n")

    # Find all available cameras
    print("🔍 Searching for cameras...")
    available_cameras = []
    for i in range(5):  # Check first 5 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                print(f"  Camera {i}: Available ({frame.shape[1]}x{frame.shape[0]})")
            cap.release()

    if not available_cameras:
        print("❌ No cameras found")
        exit(1)

    # Prefer external camera (usually higher index than 0)
    if len(available_cameras) > 1:
        camera_idx = available_cameras[-1]  # Use last found (likely external)
        print(f"\n✅ Using camera {camera_idx} (external camera detected)")
    else:
        camera_idx = available_cameras[0]
        print(f"\n✅ Using camera {camera_idx}")

    cap = cv2.VideoCapture(camera_idx)
    if not cap.isOpened():
        print("❌ Cannot open selected camera")
        exit(1)

    detector = ActivityDetector()

    print("Move around to see activity scores!")
    print("Press 'q' to quit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Analyze activity
        result = detector.analyze_frame(frame)

        score = result['activity_score']
        fg_pct = result['fg_percentage']
        is_movement = result['is_real_movement']

        # Color code
        if is_movement:
            color = (0, 0, 255)  # Red - confirmed
        elif score > 20:
            color = (0, 165, 255)  # Orange - possible
        else:
            color = (0, 255, 0)  # Green - static

        # Display
        cv2.putText(frame, f"Activity: {score:.0f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"Changed: {fg_pct:.1f}%", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if is_movement:
            cv2.putText(frame, "MOVEMENT", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Simple Activity Detector', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("\n✅ Test complete!")
