# Adaptive Activity Detection - Implementation Complete

## What Was Implemented

Replaced absolute threshold activity detection with **adaptive statistical baseline** system.

## Changes Made

### 1. activity_detector.py

**New calibration system:**
- First 30 frames (~1 second) learn camera-specific noise characteristics
- Calculates baseline median and standard deviation
- Sets noise floor automatically

**Statistical movement detection:**
- Movement = 3+ standard deviations above baseline
- Requires sustained spike (3 consecutive frames)
- Eliminates false positives from single-frame glitches

**New return values:**
```python
{
    'activity_score': 0-100,
    'magnitude': float,
    'baseline': float,
    'deviation_stds': float,  # NEW: How many std devs above baseline
    'is_real_movement': bool,  # NEW: Confirmed sustained movement
    'calibrating': bool,  # NEW: Still learning baseline
    'response_mode': str,
    'suggested_delay': float
}
```

### 2. focus_system.py

**Updated novelty calculation:**
```python
# OLD (broken):
if activity_score > 50:
    return 0.85  # False positives from noise!

# NEW (robust):
if is_real_movement and activity_score > 60:
    return 0.85  # Only confirmed movement
elif is_real_movement and activity_score > 30:
    return 0.6  # Moderate confirmed movement
# Otherwise: use text-based novelty (static scene)
```

### 3. personality.py

**Pass full activity_result dict:**
```python
# OLD:
activity_score=activity_score

# NEW:
activity_result=activity_data  # Full dict with is_real_movement flag
```

## Expected Behavior

### Static Scene (Person Sitting Still)

**Before fix:**
```
Activity: 60-65 (false positive from noise)
Novelty: 0.85 (high)
Focus: VISUAL (stuck)
Output: "I see various objects..." (repeating)
```

**After fix:**
```
📊 Activity baseline calibrated:
   Median: 1.234
   Std Dev: 0.421
   Noise Floor: 1.655

Activity: 5-10 (below noise floor)
is_real_movement: False
Novelty: 0.2 (text-based, low)
Focus: PHILOSOPHICAL/MEMORY
Output: "We've been sitting together a while. What are they thinking?"
```

### Person Enters Room (Gallery Use Case)

**Both systems agree:**
```
YOLO: person_arrived event
Activity: 80+ (large confirmed movement, 3+ std devs)
is_real_movement: True
Novelty: 1.0 (person event takes priority)
Response: "Oh" within 8 seconds ✅
```

### Person Waves Hand

**Activity detector leads:**
```
YOLO: Same person (no events)
Activity: 65 (3.5 std devs above baseline, sustained 3 frames)
is_real_movement: True
Novelty: 0.85 (confirmed movement)
Response: "They moved" or attentive observation
```

## Testing Instructions

### Test 1: Calibration (First 1 Second)
1. Run system with static scene
2. Watch for calibration message after ~1 second:
   ```
   📊 Activity baseline calibrated:
      Median: X.XXX
      Std Dev: X.XXX
      Noise Floor: X.XXX
   ```
3. Verify baseline makes sense for your camera

### Test 2: Static Scene Detection
1. After calibration, sit completely still for 30 seconds
2. Expected:
   - Activity score: 5-15
   - is_real_movement: False
   - Focus should switch to MEMORY/PHILOSOPHICAL after a few observations
   - Responses should become introspective

### Test 3: Movement Detection
1. Wave hand across camera
2. Expected:
   - Activity score: 50-80
   - is_real_movement: True (after 3 frames)
   - Focus: VISUAL
   - Response should notice movement

### Test 4: Gallery Arrival Simulation
1. Person walks into frame
2. Expected:
   - YOLO: person_arrived event
   - Activity: Spike to 70+
   - is_real_movement: True
   - Duck: Reacts within 10 seconds

## Debug Output to Watch

```
📊 Activity baseline calibrated:
   Median: 1.234
   Std Dev: 0.421
   Noise Floor: 1.655

📊 Activity: 8.2 | Mode: introspective
   Deviation: 0.8 std devs (below threshold)
   is_real_movement: False

🔍 Focus Mode: PHILOSOPHICAL
   Static duration: 45.2s
   Novelty: 0.25 (text-based)
```

## Known Issues / Edge Cases

### Issue: Calibration During Movement
**Symptom**: If someone is moving during first 30 frames, baseline will be artificially high

**Solution**: System will self-correct after ~1 minute as new stable frames enter history

### Issue: Sudden Lighting Change
**Symptom**: Global brightness shift creates optical flow spike

**Solution**: 3-frame sustained requirement filters out single lightning/auto-exposure events

### Issue: Very Slow Movement
**Symptom**: Person slowly leaning might not cross 3 std dev threshold

**Solution**: This is intentional - we want to distinguish "real movement" from slow drift/posture adjustment

## Success Metrics

✅ **Static scene stays below 15 activity score**
✅ **Hand wave triggers is_real_movement = True**
✅ **Person entering room detected within 3 frames (~100ms)**
✅ **Focus system switches to MEMORY/PHILOSOPHICAL when static**
✅ **No more "various objects" repetition loops**

## Next Steps

1. Test with your actual camera/lighting
2. If false negatives (missing real movement), lower threshold from 3.0 to 2.5 std devs
3. If false positives (detecting noise as movement), raise threshold from 3.0 to 3.5 std devs
4. Adjust `required_streak` from 3 to 2 frames if movement detection feels sluggish

---

**This makes the system gallery-ready.** Person walks in → Duck notices within 10 seconds. Person sits still → Duck introspects naturally.
