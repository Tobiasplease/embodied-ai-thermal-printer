"""
Lightweight person tracking using YOLOv8

Tracks people in frame to provide narrative continuity:
- Entrances/exits ("someone arrived", "I'm alone again")
- Person count changes
- Basic activity context
- CONTINUOUS presence state (not just events)

Optimized for real-time performance - only detects 'person' class.
"""

import numpy as np
from collections import deque
import time
import cv2
import copy
from dataclasses import dataclass
from typing import Optional


@dataclass
class PresenceState:
    """Continuous presence state (updated every frame, not just events)"""
    someone_present: bool = False
    person_count: int = 0
    presence_duration: float = 0.0      # How long current person(s) been here
    absence_duration: float = 0.0       # How long alone
    last_activity_time: float = 0.0     # When last movement detected
    activity_description: str = "still"

    # State transitions (for urgency calculation)
    just_arrived: bool = False          # True for first 3 seconds after arrival
    just_left: bool = False            # True for first 3 seconds after leaving

    urgency_score: float = 0.0         # 0.0-1.0, decays over time

    # Position info
    avg_position_x: float = 0.0        # Average X position (for "left/right" awareness)
    avg_position_y: float = 0.0        # Average Y position (for "near/far" awareness)

class PersonTracker:
    """Track people in frame for narrative continuity"""

    def __init__(self, model_size='n', confidence_threshold=0.5):
        """
        Initialize person tracker with YOLOv8

        Args:
            model_size: 'n' (nano - fastest), 's' (small), 'm' (medium)
            confidence_threshold: Minimum confidence for person detection (0-1)
        """
        try:
            from ultralytics import YOLO

            # Use nano model for speed
            model_path = f'yolov8{model_size}.pt'
            self.model = YOLO(model_path)

            # Optimize for inference speed
            self.model.fuse()  # Fuse layers for faster inference

            print(f"✅ Person tracker initialized (YOLOv8-{model_size})")

        except ImportError:
            print("❌ YOLOv8 not available - install with: pip install ultralytics")
            self.model = None
        except Exception as e:
            print(f"⚠️ Person tracker initialization failed: {e}")
            self.model = None

        # Tracking state
        self.current_person_count = 0
        self.last_person_count = 0
        self.smoothed_person_count = 0
        self.person_positions = []
        self.last_person_positions = []  # Track previous frame for movement
        self.scene_populated = False
        self.confidence_threshold = confidence_threshold

        # CONTINUOUS PRESENCE STATE (updated every frame)
        self.presence_state = PresenceState()
        self.last_state_update = time.time()

        # Minimum detection size (reject tiny false positives)
        self.min_detection_width = 30  # pixels (lowered for distant detections)
        self.min_detection_height = 60  # pixels (lowered for distant detections)

        # Stable state detection (prevent event spam from detection jitter)
        # INCREASED thresholds for more stable person counting (reduce flickering)
        self.stable_person_count = 0  # The CONFIRMED stable count
        self.candidate_count = None    # Potential new count being evaluated
        self.candidate_frames = 0      # How many frames we've seen the candidate
        self.stability_threshold = 40  # 4 seconds @ 10fps - strong debounce to prevent flicker

        # Event cooldown (prevent duplicate events)
        self.last_event_time = {}      # event_type -> timestamp
        self.event_cooldown = 5.0      # 5 seconds between same event type

        # History for smoothing (reduce jitter)
        # INCREASED history length for stronger smoothing
        self.count_history = deque(maxlen=10)

        # Size change smoothing (prevent false "coming closer"/"moving away" from bbox jitter)
        self.size_change_history = deque(maxlen=5)  # Track last 5 size changes
        self.sustained_movement_threshold = 3  # Need 3 consecutive movements in same direction

        # Performance tracking
        self.last_inference_time = 0

        # Detection persistence (prevents flicker-driven arrivals/departures)
        self.presence_confirmation_time = 0.6   # Seconds of consistent detection before confirming presence
        self.absence_grace_time = 2.5           # Seconds to wait before declaring everyone gone
        self.pending_positive_count = 0
        self.pending_positive_start = None
        self.last_positive_detection_time = 0.0
        self.last_confirmed_count = 0

    def analyze_image(self, image_path):
        """
        Analyze image from file path

        Args:
            image_path: Path to image file

        Returns:
            Same as analyze_frame()
        """
        frame = cv2.imread(image_path)
        if frame is None:
            return self._empty_result()
        return self.analyze_frame(frame)

    def analyze_frame(self, frame):
        """
        Extract person-level observations from frame

        Returns:
            dict with keys:
                - count: Number of people detected
                - populated: Boolean - is anyone present?
                - events: List of narrative events (entrance, exit, etc.)
                - positions: List of person bounding boxes
                - inference_time: Time taken for detection (ms)
        """
        if self.model is None:
            return self._empty_result()

        start_time = time.time()

        try:
            # Run YOLO inference - only detect person class (class 0)
            results = self.model(
                frame,
                classes=[0],  # Only detect 'person' class
                verbose=False,  # Suppress output
                conf=self.confidence_threshold
            )

            # Extract person detections
            detections = results[0].boxes

            if detections is not None and len(detections) > 0:
                # Get bounding boxes and confidences
                boxes = detections.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
                confidences = detections.conf.cpu().numpy()

                # Store person positions (center + size) - filter by minimum size
                self.person_positions = []
                for box, conf in zip(boxes, confidences):
                    x1, y1, x2, y2 = box
                    width = int(x2 - x1)
                    height = int(y2 - y1)

                    # Reject detections that are too small (likely false positives)
                    if width < self.min_detection_width or height < self.min_detection_height:
                        continue

                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    self.person_positions.append({
                        'center_x': center_x,
                        'center_y': center_y,
                        'width': width,
                        'height': height,
                        'confidence': float(conf),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })

                self.current_person_count = len(self.person_positions)
                stabilized_count = self._apply_presence_grace(self.current_person_count)
            else:
                self.current_person_count = 0
                self.person_positions = []
                stabilized_count = self._apply_presence_grace(0)

            # Add to history for smoothing
            self.count_history.append(stabilized_count)

            # Use majority vote from history to reduce jitter
            smoothed_count = self._get_smoothed_count()
            self.smoothed_person_count = smoothed_count

            # Detect narrative events
            events = self._detect_events(smoothed_count)

            # Detect person activity/movement
            activity_description = self._detect_person_activity()

            # UPDATE CONTINUOUS PRESENCE STATE (every frame!)
            self._update_presence_state(smoothed_count, activity_description)

            # Update state
            self.last_person_positions = self.person_positions.copy()
            self.last_person_count = smoothed_count
            self.scene_populated = smoothed_count > 0

            # Track inference time
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            self.last_inference_time = inference_time

            return {
                'count': smoothed_count,
                'raw_count': self.current_person_count,
                'populated': self.scene_populated,
                'events': events,
                'positions': self.person_positions,
                'activity': activity_description,  # NEW: What the person is doing
                'inference_time': inference_time,
                'presence_state': copy.copy(self.presence_state)  # NEW: Continuous state snapshot
            }

        except Exception as e:
            print(f"⚠️ Person tracking error: {e}")
            return self._empty_result()

    def _get_smoothed_count(self):
        """Get smoothed person count using majority vote from recent history"""
        if not self.count_history:
            return 0

        # Use most common count from recent history
        from collections import Counter
        counts = Counter(self.count_history)
        return counts.most_common(1)[0][0]

    def _detect_events(self, smoothed_count):
        """Detect narrative events using stable state detection (prevents spam)"""
        events = []
        current_time = time.time()

        # Update stable state tracking
        if smoothed_count == self.stable_person_count:
            # Current count matches stable state - reset candidate
            self.candidate_count = None
            self.candidate_frames = 0

        elif smoothed_count == self.candidate_count:
            # Still seeing the same candidate change - increment confidence
            self.candidate_frames += 1

            # Check if candidate has become stable
            if self.candidate_frames >= self.stability_threshold:
                # STABLE CHANGE CONFIRMED - generate event
                old_stable = self.stable_person_count
                self.stable_person_count = smoothed_count

                # Generate event based on stable change
                event_type = None

                # Entrance - someone arrived
                if smoothed_count > 0 and old_stable == 0:
                    event_type = 'someone_arrived'

                # Exit - now alone
                elif smoothed_count == 0 and old_stable > 0:
                    event_type = 'now_alone'

                # More people joined
                elif smoothed_count > old_stable > 0:
                    event_type = 'more_people'

                # Someone left (but others remain)
                elif 0 < smoothed_count < old_stable:
                    event_type = 'fewer_people'

                # Check event cooldown to prevent duplicates
                if event_type:
                    last_event = self.last_event_time.get(event_type, 0)
                    if current_time - last_event >= self.event_cooldown:
                        events.append(event_type)
                        self.last_event_time[event_type] = current_time

                # Reset candidate after confirming
                self.candidate_count = None
                self.candidate_frames = 0

        else:
            # New different reading - start evaluating new candidate
            self.candidate_count = smoothed_count
            self.candidate_frames = 1

        return events

    def _apply_presence_grace(self, raw_count: int) -> int:
        """Apply hysteresis so brief detection drops don't register as departures."""
        now = time.time()

        if raw_count > 0:
            if self.pending_positive_count != raw_count:
                self.pending_positive_count = raw_count
                self.pending_positive_start = now
            elif self.pending_positive_start is None:
                self.pending_positive_start = now

            self.last_positive_detection_time = now

            # Confirm initial presence after a short stability window
            if self.last_confirmed_count == 0:
                if self.pending_positive_start and (now - self.pending_positive_start) >= self.presence_confirmation_time:
                    self.last_confirmed_count = self.pending_positive_count
                else:
                    return 0
            else:
                # Update confirmed count if detections consistently show a new number
                if (self.pending_positive_count != self.last_confirmed_count and
                        self.pending_positive_start and
                        (now - self.pending_positive_start) >= self.presence_confirmation_time):
                    self.last_confirmed_count = self.pending_positive_count

            return self.last_confirmed_count

        # No detections - hold last known state briefly before declaring absence
        if self.last_positive_detection_time and (now - self.last_positive_detection_time) < self.absence_grace_time:
            return self.last_confirmed_count

        # Grace expired - truly alone
        self.pending_positive_count = 0
        self.pending_positive_start = None
        self.last_confirmed_count = 0
        return 0

    def _detect_person_activity(self):
        """Detect what the person is doing based on position/movement"""
        if not self.person_positions or not self.last_person_positions:
            return None

        # Only track single person for now (simpler narrative)
        if len(self.person_positions) != 1 or len(self.last_person_positions) != 1:
            return None

        current = self.person_positions[0]
        previous = self.last_person_positions[0]

        # Calculate movement
        dx = current['center_x'] - previous['center_x']
        dy = current['center_y'] - previous['center_y']
        movement_distance = (dx**2 + dy**2)**0.5

        # Size changes (moving closer/further)
        size_change = (current['width'] * current['height']) - (previous['width'] * previous['height'])

        # Detect significant movement (>50 pixels between frames)
        if movement_distance > 50:
            if abs(dx) > abs(dy):
                if dx > 0:
                    return "moving across the space"
                else:
                    return "moving across the space"
            else:
                if dy > 0:
                    return "moving around"
                else:
                    return "moving around"

        # Detect approaching/leaving (size change with smoothing)
        # Track size change history to prevent false positives from bbox jitter
        if abs(size_change) > 20000:  # Significant size change threshold
            # Add to history: 1 for getting bigger, -1 for getting smaller
            direction = 1 if size_change > 0 else -1
            self.size_change_history.append(direction)

            # Only trigger if we've seen sustained movement in same direction
            if len(self.size_change_history) >= self.sustained_movement_threshold:
                recent_directions = list(self.size_change_history)[-self.sustained_movement_threshold:]
                # All recent changes in same direction?
                if all(d == direction for d in recent_directions):
                    if direction > 0:
                        return "coming closer"
                    else:
                        return "moving away"
        else:
            # Small/no size change - reset history
            self.size_change_history.clear()

        # Minimal movement - person is present but still
        if movement_distance > 10:
            return "shifting position"

        return None  # Stationary

    def _update_presence_state(self, person_count, activity_description):
        """Update continuous presence state (called every frame)"""
        current_time = time.time()
        dt = current_time - self.last_state_update

        # Get current state
        someone_now = person_count > 0
        someone_before = self.presence_state.someone_present

        # Update person count
        self.presence_state.person_count = person_count

        # Update presence/absence durations
        if someone_now:
            self.presence_state.presence_duration += dt
            self.presence_state.absence_duration = 0.0
        else:
            self.presence_state.absence_duration += dt
            self.presence_state.presence_duration = 0.0

        # Update activity description
        if activity_description:
            self.presence_state.activity_description = activity_description
            self.presence_state.last_activity_time = 0.0  # Reset - just moved
        else:
            self.presence_state.activity_description = "still"
            self.presence_state.last_activity_time += dt

        # Update average position (for spatial awareness)
        if self.person_positions:
            total_x = sum(p['center_x'] for p in self.person_positions)
            total_y = sum(p['center_y'] for p in self.person_positions)
            self.presence_state.avg_position_x = total_x / len(self.person_positions)
            self.presence_state.avg_position_y = total_y / len(self.person_positions)

        # Detect state transitions and calculate urgency
        if someone_now and not someone_before:
            # ARRIVAL - high urgency!
            self.presence_state.just_arrived = True
            self.presence_state.just_left = False
            self.presence_state.urgency_score = 0.9
            self.presence_state.someone_present = True

        elif not someone_now and someone_before:
            # DEPARTURE - high urgency!
            self.presence_state.just_left = True
            self.presence_state.just_arrived = False
            self.presence_state.urgency_score = 0.8
            self.presence_state.someone_present = False

        else:
            # No transition - decay urgency and clear transition flags
            # SLOWER DECAY: 0.995 per frame = stays above 0.6 for ~60 frames (~2 seconds at 30fps)
            # This gives the main loop time to detect it (main loop checks every ~0.1s in between AI calls)
            self.presence_state.urgency_score *= 0.995  # Much slower exponential decay

            # Clear transition flags after 3 seconds
            if self.presence_state.presence_duration > 3.0:
                self.presence_state.just_arrived = False
            if self.presence_state.absence_duration > 3.0:
                self.presence_state.just_left = False

            # Update presence flag
            self.presence_state.someone_present = someone_now

        # Activity boosts urgency slightly
        if activity_description in ["moving across the space", "moving around"]:
            self.presence_state.urgency_score = min(1.0, self.presence_state.urgency_score + 0.1)

        self.last_state_update = current_time

    def get_presence_state(self):
        """Get thread-safe copy of current presence state"""
        return copy.copy(self.presence_state)

    def get_narrative_context(self):
        """Generate human-readable context for prompt injection (internal use only, not spoken)"""
        if self.current_person_count == 0:
            return ""  # Alone is the default, no need to state it
        elif self.current_person_count == 1:
            return "(someone nearby)"
        elif self.current_person_count == 2:
            return "(two people nearby)"
        else:
            return f"({self.current_person_count} people nearby)"

    def get_event_prompt_override(self, events):
        """
        Get special prompt for narrative events

        Returns None if no override needed, or a prompt fragment if event occurred
        """
        if not events:
            return None

        # Priority: most dramatic events first
        if 'someone_arrived' in events:
            return "Someone just arrived!"
        elif 'now_alone' in events:
            return "They left - I'm alone again"
        elif 'more_people' in events:
            return f"More people arrived (now {self.current_person_count} total)"
        elif 'fewer_people' in events:
            return f"Someone left (now {self.current_person_count} remaining)"

        return None

    def _empty_result(self):
        """Return empty result when tracking unavailable"""
        return {
            'count': 0,
            'raw_count': 0,
            'populated': False,
            'events': [],
            'positions': [],
            'inference_time': 0
        }

    def get_status(self):
        """Get tracker status for debugging"""
        return {
            'available': self.model is not None,
            'current_count': self.current_person_count,
            'last_count': self.last_person_count,
            'populated': self.scene_populated,
            'last_inference_ms': self.last_inference_time
        }


# Test script
if __name__ == "__main__":
    import cv2

    print("Testing PersonTracker with webcam...")

    tracker = PersonTracker(model_size='n', confidence_threshold=0.5)

    if tracker.model is None:
        print("Cannot test - YOLO not available")
        exit(1)

    # Open webcam
    cap = cv2.VideoCapture(0)

    print("\nPress 'q' to quit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Track people
        result = tracker.analyze_frame(frame)

        # Draw bounding boxes
        display_frame = frame.copy()
        for person in result['positions']:
            x1, y1, x2, y2 = person['bbox']
            conf = person['confidence']

            # Draw box
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw confidence
            label = f"Person {conf:.2f}"
            cv2.putText(display_frame, label, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Show info
        info_text = f"Count: {result['count']} | Events: {result['events']} | Time: {result['inference_time']:.1f}ms"
        cv2.putText(display_frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Show narrative context
        context = tracker.get_narrative_context()
        cv2.putText(display_frame, context, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Show event prompt if any
        event_prompt = tracker.get_event_prompt_override(result['events'])
        if event_prompt:
            cv2.putText(display_frame, f"EVENT: {event_prompt}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Person Tracker Test', display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("\nTest complete!")
    print(f"Final status: {tracker.get_status()}")
