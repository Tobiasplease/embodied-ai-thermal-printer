# SYSTEM AUDIT - What Actually Works vs What's Half-Baked

Date: 2025-11-05
Context: Duck keeps repeating "I notice a person with glasses" despite having presence tracking

## WHAT'S ACTUALLY WIRED UP AND WORKING

### 1. ✅ Person Tracking (person_tracker.py)
- **YOLOv8n detection**: Works, runs every frame
- **PresenceState dataclass**: Tracks continuous presence
  - `someone_present`: bool ✅
  - `person_count`: int ✅
  - `presence_duration`: float ✅ (how long they've been here)
  - `urgency_score`: float ✅ (0.995 decay rate - stays above 0.6 for ~2.7s)
  - `just_arrived`: bool ✅
  - `just_left`: bool ✅
- **get_presence_state()**: Returns thread-safe copy ✅
- **State updates every frame** ✅

### 2. ✅ Presence Context in Prompt (personality.py line 1050-1055)
```python
presence_context_line = ""
if hasattr(self, 'person_tracker') and self.person_tracker:
    presence_state = self.person_tracker.get_presence_state()
    if presence_state:
        presence_context_line = self._format_presence_context(presence_state)
```
**This IS wired up** and formats presence duration:
- "someone just arrived"
- "someone here 5s"
- "with someone 1m"

### 3. ✅ Persistent Facts (personality.py line 500-503, 1078-1089)
- `self.persistent_facts`: set() ✅
- Extracts keywords from responses (laptop, screen, desk, etc) ✅
- Tracks first_seen and last_seen timestamps ✅
- Shows in prompt as `(still: bright, light)` ✅
- **Working and showing in logs** ✅

### 4. ✅ Temporal Awareness (personality.py line 1092)
```python
temporal_awareness = f"[I've been awake {time_awake}]{persistent_context}"
```
Shows as `[I've been awake 2m 7s] (still: bright, light)` ✅

## THE ACTUAL PROBLEM

Looking at the logs, the prompt IS getting rich context:

```
Previous thought: ""Noticing anything out of the ordinary""
[I've been awake 38s]
(with someone)
Last thought: "This is a person with dark hair and glasses..."
Current state: Feeling curious, afternoon, feeling alert, eyes open, noticing
[What I'm seeing now]
OBSERVING: Through the duck's vision (the duck is the observer)
Internal monologue (continue):
```

**The presence context shows:**
- `(with someone)` - so it knows duration
- `(someone still)` - appears later in logs

**But the vision model sees a FRESH IMAGE every time and says:**
- "I notice a person with glasses"
- "They seem focused on something"
- "The room has an interesting setup"

## ROOT CAUSE IDENTIFIED

**The vision model (LLaVA) has NO MEMORY of what it already described.**

The prompt says:
- "Previous thought: 'Noticing anything out of the ordinary'"
- "(with someone)"

But when LLaVA sees `[What I'm seeing now]` + fresh image, it:
1. Sees person with glasses
2. Describes what it sees literally
3. Ignores that it already described this 30 seconds ago

**The "Recent thoughts" section helps a bit** but not enough because:
- It's buried in the middle of the prompt
- Vision models weight image content very heavily
- No explicit instruction to "don't re-describe what you already said"

## HALF-BAKED FEATURES THAT DO NOTHING

### ❌ Person Activity Tracking (line 1218-1240)
```python
activity = person_data.get('activity')  # NEW: What they're doing
if activity and random.random() < 0.7:
    person_presence = f"someone {activity}"
```

**Problem**: Where does `activity` come from?
- person_tracker.py has `activity_description` in PresenceState
- But it's always set to "still" (line 30)
- Never actually tracks real activity
- **This does NOTHING**

### ❌ Memory Pattern Recognition (line 1261-1265)
```python
elif current_focus == "MEMORY":
    task_directive = "Internal monologue (what patterns am I noticing?):"
```

**Problem**:
- No episodic memories exist yet (they're only stored during compression)
- Asking "what patterns am I noticing?" without established facts = hallucination
- This is a compression question, not a real-time question
- **This causes repetition loops**

### ❌ Psychological State (line 1182-1195)
```python
desires = self.memory_ref.self_model.get('desires', [])
doubts = self.memory_ref.self_model.get('doubts', [])
identity_fragments = self.memory_ref.self_model.get('identity_fragments', [])
```

**Problem**:
- Only populated during compression (every 5 minutes)
- Empty at startup and most of the time
- Has conditions `if observation_count > 5` / `> 3` / `> 10`
- Even when populated, rarely shows because of random logic
- **Adds complexity but does nothing most of the time**

### ❌ Staleness Hints (line 1003-1011)
```python
if minutes_with_baseline >= 10:
    staleness_hint = f" [I've noted this for {minutes_with_baseline} minutes - find something NEW]"
```

**Problem**:
- Only applies to `baseline_context` (compressed memory)
- Baseline is empty for first 5 minutes
- Vision model sees fresh image every time anyway
- **Doesn't prevent visual repetition**

## WHAT THE PROMPT ACTUALLY NEEDS

The prompt needs to **explicitly tell the vision model**:

1. ✅ **You already know there's a person here** (if presence_duration > 30s)
2. ✅ **You already described them** (if we've mentioned "person" in last 3 thoughts)
3. ✅ **What's DIFFERENT or NEW now?** (movement, expression, posture change)
4. ✅ **If nothing new, reflect on their STATE not their APPEARANCE**

Current prompt structure:
```
Previous thought: "X"
Recent thoughts: A → B → C
[What I'm seeing now]  <-- Vision model goes "oh, a person! let me describe them!"
Internal monologue (continue):
```

**The image comes AFTER the context, so vision dominates.**

Better structure would be:
```
ESTABLISHED FACTS (don't re-describe these):
- Person with glasses present (here for 1m 30s)
- Room is workspace/studio setup
- They're focused on something

[What I'm seeing now]
What's DIFFERENT or new? What's their state/mood?
Internal monologue (continue from "X"):
```

## SUMMARY

**Working features:**
- ✅ Person detection & tracking
- ✅ Continuous presence state with duration
- ✅ Persistent facts extraction
- ✅ Temporal awareness
- ✅ Focus mode cycling

**Half-baked / broken:**
- ❌ Activity tracking (always "still", never updates)
- ❌ Memory pattern recognition (no memories to recognize)
- ❌ Psychological state (empty most of time)
- ❌ Staleness hints (wrong layer - applies to compression not vision)

**Core issue:**
- Vision model sees fresh image every time
- Describes what it sees literally
- Context comes BEFORE image, so image dominates
- No explicit instruction to avoid re-describing established facts

**Solution direction:**
1. Move established facts AFTER "Previous thought" but BEFORE image
2. Explicitly list what NOT to re-describe
3. Redirect attention to CHANGES/STATE not APPEARANCE
4. Remove/fix half-baked features that add noise
