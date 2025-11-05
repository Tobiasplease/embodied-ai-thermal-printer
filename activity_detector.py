"""
Activity detection using optical flow for intelligent response timing

Measures "how much is happening" in the scene to determine:
- Immediate response (high activity - something happening NOW)
- Normal response (moderate activity - ongoing scene)
- Sparse introspection (low activity - nothing changing, boredom mode)
"""

import cv2
import numpy as np
import time
from collections import deque


class ActivityDetector:
    """Detect scene activity level using optical flow"""

    def __init__(self, history_length=30):
        """
        Initialize activity detector with adaptive baseline calibration

        Args:
            history_length: Number of frames to track for activity baseline (default 30 ~ 1 second)
        """
        self.prev_gray = None
        self.activity_history = deque(maxlen=history_length)
        self.baseline_activity = 0.0
        self.last_high_activity_time = 0

        # NEW: Statistical tracking for adaptive thresholds
        self.baseline_std = 0.0  # Standard deviation of baseline noise
        self.calibration_frames = 30  # Calibrate for first 30 frames (~1 second)
        self.is_calibrated = False
        self.noise_floor = 0.0  # Learned noise threshold

        # NEW: Sustained detection (prevent single-frame spikes)
        self.high_activity_streak = 0  # Consecutive high frames
        self.required_streak = 3  # Need 3 frames to confirm real movement

        # Optical flow parameters (Farneback)
        self.flow_params = dict(
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )

    def analyze_frame(self, frame):
        """
        Analyze frame for activity level

        Args:
            frame: OpenCV frame (BGR or grayscale)

        Returns:
            dict with keys:
                - activity_score: 0-100 (how much is happening)
                - magnitude: Average optical flow magnitude
                - response_mode: 'immediate', 'normal', 'sparse', 'introspective'
                - suggested_delay: Recommended seconds until next check
        """
        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # Need previous frame for optical flow
        if self.prev_gray is None:
            self.prev_gray = gray
            return self._empty_result()

        # Calculate optical flow
        try:
            flow = cv2.calcOpticalFlowFarneback(
                self.prev_gray, gray,
                None,
                **self.flow_params
            )

            # Calculate magnitude of flow vectors
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            avg_magnitude = np.mean(magnitude)

            # Update history
            self.activity_history.append(avg_magnitude)

            # CALIBRATION PHASE (first 30 frames to learn camera noise)
            if not self.is_calibrated:
                if len(self.activity_history) < self.calibration_frames:
                    # Still collecting calibration data
                    self.prev_gray = gray
                    return {
                        'activity_score': 10.0,  # Neutral during calibration
                        'magnitude': float(avg_magnitude),
                        'baseline': 0.0,
                        'deviation_stds': 0.0,
                        'is_real_movement': False,
                        'calibrating': True,
                        'response_mode': 'normal',
                        'suggested_delay': 3.0
                    }
                else:
                    # Enough data - calibrate NOW and fall through to detection
                    self._calibrate_baseline()
                    self.is_calibrated = True
                    print(f"📊 Activity baseline calibrated:")
                    print(f"   Median: {self.baseline_activity:.3f}")
                    print(f"   Std Dev: {self.baseline_std:.3f}")
                    print(f"   Noise Floor: {self.noise_floor:.3f}")
                    # Fall through to detection phase below

            # DETECTION PHASE (after calibration)
            # Calculate deviation from baseline in standard deviations
            deviation = avg_magnitude - self.baseline_activity
            deviation_in_stds = deviation / max(self.baseline_std, 0.01)  # Prevent div by 0

            # MOVEMENT DETECTION: Require 3+ std devs sustained for 3 frames
            if deviation_in_stds > 3.0:
                self.high_activity_streak += 1
            else:
                self.high_activity_streak = 0  # Reset streak

            # Confirm real movement only if sustained
            is_real_movement = self.high_activity_streak >= self.required_streak

            # Calculate activity score based on statistical deviation
            if is_real_movement:
                # Confirmed movement - scale from 50-100 based on intensity
                activity_score = min(100, 50 + (deviation_in_stds - 3.0) * 20)
            elif deviation_in_stds > 1.5:
                # Possible movement but not sustained - cautious score
                activity_score = 15 + min(20, (deviation_in_stds - 1.5) * 10)
            else:
                # Below noise threshold - static scene
                activity_score = min(10, deviation_in_stds * 5)

            # Determine response mode
            response_mode, suggested_delay = self._classify_activity(activity_score, is_real_movement)

            # Store previous frame
            self.prev_gray = gray

            return {
                'activity_score': float(activity_score),
                'magnitude': float(avg_magnitude),
                'baseline': float(self.baseline_activity),
                'deviation_stds': float(deviation_in_stds),
                'is_real_movement': is_real_movement,
                'calibrating': False,
                'response_mode': response_mode,
                'suggested_delay': suggested_delay
            }

        except Exception as e:
            print(f"⚠️ Activity detection error: {e}")
            self.prev_gray = gray
            return self._empty_result()

    def _calibrate_baseline(self):
        """Calculate baseline statistics from calibration period"""
        history = list(self.activity_history)

        # Use median (robust to outliers)
        self.baseline_activity = np.median(history)

        # Calculate standard deviation
        self.baseline_std = np.std(history)

        # Noise floor = baseline + 1 std dev (anything below is definitely noise)
        self.noise_floor = self.baseline_activity + self.baseline_std

    def _classify_activity(self, score, is_real_movement=False):
        """
        Classify activity level and suggest response timing

        Args:
            score: Activity score 0-100
            is_real_movement: Whether movement is confirmed (sustained 3+ frames)

        Returns:
            (response_mode, suggested_delay_seconds)
        """
        current_time = time.time()

        # CONFIRMED MOVEMENT takes priority
        if is_real_movement and score > 60:
            # CONFIRMED HIGH MOVEMENT - immediate reaction
            self.last_high_activity_time = current_time
            return 'immediate', 0.5

        elif is_real_movement and score > 30:
            # CONFIRMED MODERATE MOVEMENT - normal response
            self.last_high_activity_time = current_time
            return 'normal', 2.0

        elif score > 20:
            # UNCONFIRMED ACTIVITY - possible movement, be cautious
            return 'sparse', 8.0

        elif score > 10:
            # LOW ACTIVITY - very subtle
            return 'sparse', 12.0

        else:
            # STATIC SCENE - introspect based on how long it's been static
            time_since_activity = current_time - self.last_high_activity_time

            if time_since_activity < 60:
                # Recently active - still attentive
                return 'contemplative', 20.0
            elif time_since_activity < 300:
                # Been a while - getting bored
                return 'introspective', 45.0
            else:
                # Long stasis - deep thoughts
                return 'dreamlike', 60.0

    def _empty_result(self):
        """Return empty result"""
        return {
            'activity_score': 0.0,
            'magnitude': 0.0,
            'baseline': 0.0,
            'deviation_stds': 0.0,
            'is_real_movement': False,
            'calibrating': not self.is_calibrated,
            'response_mode': 'normal',
            'suggested_delay': 3.0
        }

    def reset(self):
        """Reset detector (e.g., after scene change)"""
        self.prev_gray = None
        self.activity_history.clear()
        self.is_calibrated = False  # Recalibrate after reset
        self.high_activity_streak = 0


# Test code
if __name__ == "__main__":
    print("Testing activity detector with webcam...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        exit(1)

    detector = ActivityDetector()

    print("✅ Activity detector ready")
    print("Move around to see activity scores!")
    print("Press 'q' to quit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Analyze activity
        result = detector.analyze_frame(frame)

        # Display info
        score = result['activity_score']
        mode = result['response_mode']
        delay = result['suggested_delay']

        # Color code by activity level
        if score > 60:
            color = (0, 0, 255)  # Red - high activity
        elif score > 25:
            color = (0, 165, 255)  # Orange - moderate
        elif score > 5:
            color = (0, 255, 255)  # Yellow - low
        else:
            color = (0, 255, 0)  # Green - very low

        cv2.putText(frame, f"Activity: {score:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"Mode: {mode}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"Delay: {delay:.1f}s", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow('Activity Detector Test', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("\n✅ Test complete!")
