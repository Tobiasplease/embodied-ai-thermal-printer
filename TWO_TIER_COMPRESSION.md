# Two-Tier Compression System Implementation

## Overview

Implemented a two-tier compression system to solve the repetitive observation problem where the duck kept saying "I notice a person with glasses" despite continuous presence.

## The Problem

**Before**:
- Only 5-minute deep compression existed
- Vision model saw fresh image every time with no environmental context
- Resulted in repetitive descriptions: "I notice a person..." → "They seem focused..." → "I notice a person..."
- No accumulated understanding between compressions

## The Solution

### Tier 1: Environmental Baseline (2 minutes)
**Purpose**: Lightweight scene understanding that anchors observations

**What it does**:
- After 2 minutes of observation, queries LLaVA with last 5 thoughts
- Asks: "What's the STABLE environment?"
- Extracts 2-3 sentence factual summary
- Example output: "I'm in a workspace. A person with glasses is focused on a screen. The room has a creative studio atmosphere."

**Stored as**: `self.environmental_baseline`

### Tier 2: Deep Compression (5 minutes, existing)
**Purpose**: Episodic memories, patterns, psychological themes

**Unchanged**: Still runs full compression with reflection, memory consolidation, etc.

## How It Works

### 1. Compression Triggers
```python
# Line 497-499: New timing variables
self.last_environmental_compression = time.time()
self.environmental_compression_interval = 120  # 2 minutes
self.environmental_baseline = ""

# Line 1423: Environmental compression check
self._check_environmental_compression(temp_path)

# Line 1426: Deep compression check (existing, now renamed)
self._check_reflection_interval(response, temp_path)
```

### 2. Environmental Baseline Creation (Line 4241-4299)
```python
def _create_environmental_baseline(self, image_path):
    """Create lightweight environmental baseline from recent observations (2 minutes)"""

    # Get last 5 thoughts
    recent_obs = self.recent_responses[-5:]

    # Simple prompt
    env_prompt = """You've been observing for 2 minutes. What's the STABLE environment?

    Recent observations: {thoughts}

    Task: Describe the consistent environment in 2-3 short sentences.
    - What space/setting
    - Who/what is consistently present
    - General atmosphere
    """

    # Query model, limit to 150 chars (2-3 sentences)
    response = self._query_ollama_multimodal(...)
    self.environmental_baseline = response
```

### 3. Prompt Injection (Line 1286-1319)
**CRITICAL**: Environmental baseline comes BEFORE the image in prompt

```python
# Build baseline context
env_baseline_context = ""
if self.environmental_baseline and observation_count > 15:  # After 2+ mins
    env_baseline_context = f"\nFAMILIAR SCENE: {self.environmental_baseline}"

# Add to context block (BEFORE image)
context_block = f"""Previous thought: "{last_thought}"
[I've been awake {time_awake}]
FAMILIAR SCENE: {self.environmental_baseline}  ← ANCHORS UNDERSTANDING
Current state: {full_context}

[What I'm seeing now]  ← Image comes AFTER baseline

Internal monologue (continue with established scene):
```

### 4. Task Directive Adjustment
When environmental baseline exists, add "(continue with established scene)" to task directive:

```python
if self.environmental_baseline and observation_count > 15:
    task_suffix = " (continue with established scene)"
```

This subtly nudges the model to:
- Recognize the scene as familiar
- Focus on changes/state instead of re-describing appearance
- Continue narrative within known context

## Expected Behavior Change

### Before (No Environmental Baseline)
```
Observation 1: "I notice a person with glasses working at a desk"
Observation 2: "They seem focused on something in front of them"
Observation 3: "I notice a person with glasses" ← REPETITION
Observation 4: "The room has an interesting setup" ← REPETITION
```

### After (With Environmental Baseline at 2 min)
```
Observation 1-15 (first 2 minutes): Initial descriptions, building understanding
[2 minute mark - Environmental baseline created]
Observation 16+:

Context includes:
FAMILIAR SCENE: I'm in a workspace. A person with glasses is focused on a screen. The room has a creative studio atmosphere.

Expected outputs:
Observation 16: "They shifted in their chair slightly"
Observation 17: "The focused energy is palpable"
Observation 18: "I wonder what's holding their attention"
Observation 19: "We've been sitting together a while now"
```

## Performance Impact

**Cost**: One additional LLaVA query every 2 minutes
- Current load: ~8 queries/minute = 480/hour
- Additional: +0.5 queries/minute = 30/hour
- **Total impact: +6% query load** (negligible)

**Speed**: Runs in same thread as main processing (2-3 second pause every 2 minutes)

## Key Design Decisions

### Why 2 minutes?
- Long enough to accumulate meaningful observations (15+ at 8s interval)
- Short enough to establish context before repetition becomes annoying
- Aligns with human short-term memory consolidation timing

### Why separate from 5-minute compression?
- Different purposes: environmental grounding vs episodic memory
- Lighter prompt = faster response
- Can update environmental_baseline more frequently without heavy processing

### Why "FAMILIAR SCENE" prefix?
- Clear signal to model that this is established context
- Paired with "(continue with established scene)" creates strong nudge
- Suggests temporal continuity vs fresh observation

### Why come BEFORE image?
- Text context arrives first, anchors interpretation
- Image then confirms/updates rather than generates fresh description
- Prevents vision from dominating and triggering re-description

## Limitations & Future Improvements

### Current Limitations
1. **Fixed 2-minute interval**: Could be adaptive based on scene changes
2. **No incremental updates**: Baseline is replaced, not accumulated
3. **No change detection**: Doesn't explicitly track what CHANGED since baseline
4. **Hard cutoff at observation 15**: Could be smoother transition

### Potential Improvements
1. **Adaptive timing**: Trigger baseline creation when scene stabilizes, not just time
2. **Incremental accumulation**: "Baseline: [existing] + Now also: [new facts]"
3. **Change highlighting**: "FAMILIAR SCENE: [baseline] | NEW: [what changed]"
4. **Confidence scoring**: Track how stable baseline is, update if scene shifts significantly

## Testing Checklist

- [ ] Run for 2+ minutes with static scene (person sitting still)
- [ ] Verify environmental baseline creation prints at ~2 minute mark
- [ ] Check that "FAMILIAR SCENE:" appears in debug output after baseline created
- [ ] Verify observations shift from descriptions to states/changes after baseline
- [ ] Test that person arrival/departure triggers new baseline formation
- [ ] Confirm baseline persists across multiple observation cycles
- [ ] Validate 5-minute deep compression still works independently

## Debug Output to Watch

```
🌍 DEBUG: Environmental compression check - 120s since last (need 120s)
🌍 Creating environmental baseline after 120s...
🌍 Querying for environmental baseline...
🌍 Environmental baseline created: I'm observing a workspace. A person with glasses is focused on a screen. The atmosphere feels creative and concentrated.

[Next observation]
📝 Combined prompt:
Previous thought: "..."
[I've been awake 2m 15s]
FAMILIAR SCENE: I'm observing a workspace. A person with glasses is focused on a screen.
Current state: Feeling curious, afternoon, alert

[What I'm seeing now]
OBSERVING: Through the duck's vision (the duck is the observer)

Internal monologue (continue with established scene):
```

## Success Metrics

1. **Reduced repetition**: Should stop re-describing "person with glasses" after 2 minutes
2. **Increased state/change focus**: More "they shifted", "focused energy", "wondering what..."
3. **Improved continuity**: References to "still here", "we've been together", temporal awareness
4. **Better introspection**: More internal reflection vs external description

---

Date: 2025-11-05
Status: Implemented, ready for testing
