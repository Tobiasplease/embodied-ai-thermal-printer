# Activity Detection Fix: Robust Movement Detection for Grainy Webcam

## The Problem

**Current behavior:**
- Person sitting still → Activity score 60-65
- Constant false "They're moving..." reactions
- Forces VISUAL focus mode (high novelty)
- System stuck in observation loop

**Root cause (activity_detector.py line 90):**
```python
activity_score = min(100, (avg_magnitude / 5.0) * 100)
```

Grainy webcam produces optical flow magnitude ~1.5 even when static:
- Score = (1.5 / 5.0) * 100 = **30**
- Threshold for "moderate activity" = 25
- **Result: Constant false positives**

## Why Optical Flow Fails on Grainy Webcams

**Optical flow (Farneback) tracks pixel movement between frames.**

With grainy/noisy camera:
- ISO noise shifts pixels randomly
- Compression artifacts change between frames
- Auto-exposure adjustments create global shifts
- Result: Magnitude 1-3 from NOISE, not movement

## The Solution: Adaptive Baseline with Statistical Deviation

**Don't use absolute thresholds. Use deviation from learned baseline.**

### Concept

1. **Learn noise baseline** - First 30 seconds, observe typical noise level
2. **Calculate standard deviation** - How much does noise fluctuate?
3. **Set dynamic threshold** - Movement = baseline + (N * std_dev)
4. **Require sustained spike** - One frame ≠ movement, 3 consecutive frames = real

### Implementation

```python
class ActivityDetector:
    def __init__(self):
        # Existing
        self.activity_history = deque(maxlen=30)  # 30 frames ~ 1 second
        self.baseline_activity = 0.0

        # NEW: Statistical tracking
        self.baseline_std = 0.0  # Standard deviation of baseline
        self.calibration_frames = 30  # Calibrate for first 30 frames
        self.is_calibrated = False
        self.noise_floor = 0.0  # Learned noise threshold

        # NEW: Sustained detection (prevent single-frame spikes)
        self.high_activity_streak = 0  # Consecutive high frames
        self.required_streak = 3  # Need 3 frames to confirm

    def analyze_frame(self, frame):
        # ... existing optical flow calculation ...

        # Update history
        self.activity_history.append(avg_magnitude)

        # CALIBRATION PHASE (first 30 frames)
        if not self.is_calibrated:
            if len(self.activity_history) >= self.calibration_frames:
                self._calibrate_baseline()
                self.is_calibrated = True
                print(f"📊 Activity baseline calibrated:")
                print(f"   Median: {self.baseline_activity:.3f}")
                print(f"   Std Dev: {self.baseline_std:.3f}")
                print(f"   Noise Floor: {self.noise_floor:.3f}")

            # During calibration, return neutral
            return self._neutral_result(avg_magnitude)

        # DETECTION PHASE (after calibration)
        # Calculate deviation from baseline
        deviation = avg_magnitude - self.baseline_activity
        deviation_in_stds = deviation / max(self.baseline_std, 0.01)  # Prevent div by 0

        # MOVEMENT THRESHOLDS (in standard deviations)
        # Grainy webcam: Need 3+ std devs to be confident it's real movement
        if deviation_in_stds > 3.0:  # 3 std devs above baseline
            self.high_activity_streak += 1
        else:
            self.high_activity_streak = 0  # Reset streak

        # REQUIRE SUSTAINED ACTIVITY (3 consecutive frames)
        is_real_movement = self.high_activity_streak >= self.required_streak

        # Calculate activity score based on deviation
        if is_real_movement:
            # Confirmed movement - scale based on how far above threshold
            activity_score = min(100, 50 + (deviation_in_stds - 3.0) * 20)
        elif deviation_in_stds > 1.5:
            # Possible movement but not sustained
            activity_score = 20 + (deviation_in_stds - 1.5) * 10
        else:
            # Below noise floor - static scene
            activity_score = min(15, deviation_in_stds * 10)

        # Determine response mode
        response_mode, suggested_delay = self._classify_activity(
            activity_score,
            is_real_movement
        )

        return {
            'activity_score': float(activity_score),
            'magnitude': float(avg_magnitude),
            'baseline': float(self.baseline_activity),
            'deviation_stds': float(deviation_in_stds),
            'is_real_movement': is_real_movement,
            'response_mode': response_mode,
            'suggested_delay': suggested_delay
        }

    def _calibrate_baseline(self):
        """Calculate baseline statistics from calibration period"""
        history = list(self.activity_history)

        # Use median (robust to outliers)
        self.baseline_activity = np.median(history)

        # Calculate standard deviation
        self.baseline_std = np.std(history)

        # Noise floor = baseline + 1 std dev (anything below is definitely noise)
        self.noise_floor = self.baseline_activity + self.baseline_std

    def _classify_activity(self, score, is_real_movement):
        """Classify activity with knowledge of whether it's real movement"""

        if is_real_movement and score > 60:
            # CONFIRMED HIGH MOVEMENT - immediate reaction
            return 'immediate', 0.5

        elif is_real_movement and score > 30:
            # CONFIRMED MODERATE MOVEMENT - normal response
            return 'normal', 2.0

        elif score > 20:
            # UNCONFIRMED ACTIVITY - possible movement, be cautious
            return 'sparse', 8.0

        else:
            # STATIC SCENE - introspect
            return 'introspective', 15.0
```

## Key Improvements

### 1. **Calibration Period (30 frames)**
- Learns YOUR specific camera's noise characteristics
- Different cameras/lighting = different baselines
- No hard-coded thresholds

### 2. **Statistical Deviation**
- Activity = "How many std devs above baseline?"
- 3+ std devs = Very likely real movement (not noise)
- 1-3 std devs = Maybe noise, maybe movement
- <1 std dev = Definitely noise

### 3. **Sustained Detection (3 consecutive frames)**
- Single spike = probably noise
- 3 frames in a row = real movement
- Prevents false positives from single-frame glitches

### 4. **Graceful Degradation**
- Unconfirmed activity → "sparse" mode (cautious)
- Confirmed activity → "immediate" mode (react!)
- Static scene → "introspective" mode (think)

## Integration with Person Tracker

**Person tracker (YOLO) is more reliable for arrival/departure:**

```python
# In focus_system.py:

def _calculate_visual_novelty(self, recent_observations, person_events, activity_score):
    """Calculate novelty using BOTH person events AND activity"""

    # PRIORITY 1: Person events (YOLO - most reliable)
    if person_events:
        if 'person_arrived' in person_events or 'person_left' in person_events:
            return 1.0  # Maximum novelty - environment changed!

    # PRIORITY 2: Confirmed real movement (sustained activity spike)
    if activity_result.get('is_real_movement'):
        if activity_score > 60:
            return 0.85  # High novelty - something happening
        elif activity_score > 30:
            return 0.6  # Moderate novelty

    # PRIORITY 3: Static scene - use text repetition
    if activity_score < 20:
        return self._text_based_novelty(recent_observations)

    # DEFAULT: Medium novelty
    return 0.4
```

## Testing Strategy

### Phase 1: Calibration Verification
```python
python activity_detector.py  # Run test mode
# Sit still for 10 seconds
# Verify: Activity score stays < 20
# Verify: Mode shows "introspective"
```

### Phase 2: Movement Detection
```python
# Still running test mode
# Wave hand across camera
# Verify: Activity spike > 50 after 3 frames
# Verify: Mode switches to "immediate"
```

### Phase 3: Gallery Simulation
```python
# Person walks into frame
# Expected:
#   - YOLO detects: person_arrived event
#   - Activity detector: Spike to 70+
#   - Novelty: 1.0 (person event takes priority)
#   - Duck: Reacts within 8 seconds
```

## Expected Behavior After Fix

### Static Person Sitting (Current problem)
**Before:**
- Activity score: 60-65
- Mode: immediate/normal
- Focus: VISUAL (high novelty)
- Output: "I see various objects..." (repeating)

**After:**
- Activity score: 5-15 (below noise floor)
- Mode: introspective
- Focus: PHILOSOPHICAL/MEMORY (low novelty)
- Output: "We've been sitting together a while. What are they thinking?"

### Person Enters Room (Must work for gallery)
**Both systems agree:**
- YOLO: person_arrived event
- Activity: Spike to 80+ (large movement)
- Novelty: 1.0
- Duck: "Oh" or "Someone's here" within 8 seconds ✅

### Person Waves Hand
**Activity detector leads:**
- YOLO: Same person (no events)
- Activity: Spike to 60 (movement detected)
- Novelty: 0.85 (activity-based)
- Duck: "They moved" or attentive observation

## Implementation Checklist

- [ ] Update `ActivityDetector.__init__()` with new variables
- [ ] Add `_calibrate_baseline()` method
- [ ] Modify `analyze_frame()` to use statistical detection
- [ ] Update `_classify_activity()` to use `is_real_movement` flag
- [ ] Test calibration with static scene (10 seconds)
- [ ] Test movement detection (hand wave)
- [ ] Integrate `is_real_movement` flag into focus_system.py
- [ ] Test full system: person enters → duck reacts within 10s

## Fallback: Disable Activity for Now

If statistical approach is too complex, temporarily:

```python
# In focus_system.py line 174-178:
# Comment out activity-based novelty
# if activity_score > 50:
#     return 0.85

# Trust ONLY person_events from YOLO
# Activity detector will be "observation only" until fixed
```

This breaks gracefully - person arrivals still detected, but no false movement.

---

Your ambition is NOT hopeless. You just need adaptive thresholds, not absolute ones.

Let me implement this?
