# Critical Fixes Applied - Activity Detection & Environmental Baseline

## Problems Found

### 1. Activity Detection Stuck at 10.0
**Symptom**: Activity score always 10.0, never calibrated
**Root cause**: Logic bug in calibration flow - returned AFTER setting `is_calibrated = True`
**Result**: System stayed in "calibrating" mode forever

### 2. Environmental Baseline Failed
**Symptom**: `'PersonalityAI' object has no attribute '_query_ollama_multimodal'`
**Root cause**: Wrong method name for single model approach
**Result**: 2-minute environmental compression completely broken

## Fixes Applied

### Fix 1: Activity Detector Calibration Flow (activity_detector.py line 92-115)

**BEFORE (Broken):**
```python
if not self.is_calibrated:
    if len >= 30:
        calibrate()
        self.is_calibrated = True

    return calibration_result  # BUG: Always returns, even after calibrating!
```

**AFTER (Fixed):**
```python
if not self.is_calibrated:
    if len < 30:
        return calibration_result  # Still collecting data
    else:
        calibrate()
        self.is_calibrated = True
        # Fall through to detection phase below
```

**Expected behavior after fix:**
- First 30 frames: Activity 10.0, calibrating=True
- Frame 31: Calibration message prints, then immediately starts detection
- Frame 32+: Real activity scores (0-100 based on deviation)

### Fix 2: Environmental Baseline Query Method (personality.py line 4284-4290)

**BEFORE (Broken):**
```python
response = self._query_ollama_multimodal(  # This method doesn't exist!
    model_name=SINGLE_MULTIMODAL_MODEL,
    prompt=env_prompt,
    image_path=image_path,
    timeout=30
)
```

**AFTER (Fixed):**
```python
system_prompt = "You are observing your environment. Describe what has been consistently present."
response = self._query_ollama_with_images(  # Correct method for single model
    system_prompt=system_prompt,
    user_prompt=env_prompt,
    image_paths=[image_path]
)
```

**Expected behavior after fix:**
- 2-minute mark: Environmental baseline query runs
- Creates 2-3 sentence summary
- Injects as "FAMILIAR SCENE:" in future prompts

## Testing Checklist

### Test 1: Activity Calibration
- [ ] Start system
- [ ] After ~1 second, see calibration message:
  ```
  📊 Activity baseline calibrated:
     Median: X.XXX
     Std Dev: X.XXX
     Noise Floor: X.XXX
  ```
- [ ] Activity score changes from 10.0 to real values

### Test 2: Static Scene Detection
- [ ] Sit completely still for 30 seconds
- [ ] Activity score should be < 15
- [ ] is_real_movement should be False
- [ ] Focus should eventually switch from VISUAL to MEMORY/PHILOSOPHICAL

### Test 3: Environmental Baseline
- [ ] Run for 2+ minutes
- [ ] See: `🌍 Creating environmental baseline after 120s...`
- [ ] See: `🌍 Environmental baseline created: [description]`
- [ ] NO error about `_query_ollama_multimodal`
- [ ] Future prompts include "FAMILIAR SCENE:"

### Test 4: Person Arrival
- [ ] Leave frame
- [ ] Wait 10 seconds (let system stabilize)
- [ ] Enter frame
- [ ] Should see person_arrived event
- [ ] Activity should spike
- [ ] Duck should react within 10 seconds

## What Should Change

### Before Fixes:
- Activity: Always 10.0 (stuck in calibration)
- Environmental baseline: Crashes every 2 minutes
- Person arrival: YOLO detects but no reaction
- Focus: Stuck on VISUAL (fake high novelty)
- Output: "The light creates patterns..." (endless observation)

### After Fixes:
- Activity: Calibrates, then 5-15 when static, 60+ when moving
- Environmental baseline: Works, creates scene summary
- Person arrival: YOLO + Activity both trigger
- Focus: Switches to MEMORY/PHILOSOPHICAL when static
- Output: Should be introspective after baseline established

## Next Test

Run the system with these fixes and watch for:
1. Calibration message at ~1 second
2. Activity scores changing from 10.0
3. Environmental baseline at 2 minute mark
4. Person arrival detection when you enter frame

If these all work, the system should be MUCH better.

---

Date: 2025-11-05
Status: Fixes applied, ready for testing
