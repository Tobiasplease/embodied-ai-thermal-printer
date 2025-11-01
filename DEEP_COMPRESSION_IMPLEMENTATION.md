# Deep Compression with Reflective State - Implementation Guide

**Date**: November 1, 2025  
**Target**: Sculpture installation rig (weaker hardware)  
**Status**: Ready to implement  

---

## 🎯 Overview

This system adds **deep memory compression** using a larger model (mistral:latest or llama3.1:8b) that runs periodically to synthesize accumulated knowledge. During compression, the consciousness enters a **reflective state** where it remains responsive but uses pre-written phrases instead of LLM generation.

### **Key Benefits**
- ✅ Deep synthesis of motifs, beliefs, desires, doubts, identity patterns
- ✅ No blocking - sculpture stays alive with reflective phrases
- ✅ Optimized performance - only one LLM running during compression
- ✅ Artistic coherence - meta-aware "thinking" moments
- ✅ Works on weaker hardware with 20-second model calls

---

## 📊 System Architecture

### **Current Compression (Light)**
- **Frequency**: Every 10 visual observations (~80 seconds)
- **Model**: smollm2:1.7b (fast, same as consciousness)
- **Output**: Updates `baseline_context` (2-3 sentences)
- **Function**: `_compress_memory_on_reflection()`

### **New Deep Compression (Heavy)**
- **Frequency**: Every 100 observations (~13-15 minutes on installation rig, ~5 minutes for testing)
- **Model**: mistral:latest (slower, more capable)
- **Output**: 
  - Enhanced `baseline_context` (richer understanding)
  - New `worldview_summary` (beliefs, patterns, relationships)
  - New `existential_stance` (identity, purpose, doubts)
- **Function**: `_deep_compress_consciousness()` (new)

### **Reflective State (During Compression)**
- **Vision**: Continues normally (moondream:latest is fast)
- **Person Tracking**: Continues (YOLO-based, has instant captions)
- **Language**: Uses pre-written reflective phrases (no LLM call)
- **Duration**: ~20 seconds on installation rig
- **Flag**: `self.is_deep_compressing` (boolean)

---

## 🔧 Implementation Steps

### **Step 1: Add State Variables**

**File**: `personality.py`  
**Location**: In `PersonalityAI.__init__()` around line 390-400

**Add these variables:**

```python
# Deep compression system (larger model for synthesis)
self.deep_compression_interval = 100  # Every 100 observations (~13-15 min)
self.last_deep_compression = 0  # Track when last deep compression occurred
self.is_deep_compressing = False  # Flag for reflective state
self.deep_compression_enabled = True  # Enable/disable feature

# Enhanced memory fields (populated by deep compression)
self.worldview_summary = ""  # Synthesized beliefs, patterns, relationships
self.existential_stance = ""  # Identity, purpose, doubts, questions

# Reflective phrases for compression mode
self.reflective_phrases = [
    "I'm remembering what I've seen...",
    "Patterns forming in my mind...",
    "Trying to understand...",
    "Consolidating memories...",
    "Reflecting on patterns...",
    "Processing what I know...",
    "Memories shifting, connecting...",
    "Thinking deeply...",
]
self.last_reflective_phrase_index = 0
```

**Important**: Add AFTER `self.baseline_context = ""` and BEFORE `self.load_state()`

---

### **Step 2: Update State Persistence**

**File**: `personality.py`  
**Function**: `save_state()` around line 3110-3130

**Add to the state dictionary:**

```python
'advanced_state': {
    # ... existing fields ...
    'baseline_context': self.baseline_context,
    
    # ADD THESE NEW FIELDS:
    'worldview_summary': self.worldview_summary,
    'existential_stance': self.existential_stance,
    'last_deep_compression': self.last_deep_compression,
    
    # ... rest of state ...
}
```

**Function**: `load_state()` around line 3155-3180

**Add to state loading:**

```python
# ... existing baseline_context loading ...
self.baseline_context = state.get('baseline_context', "")

# ADD THESE:
self.worldview_summary = state.get('worldview_summary', "")
self.existential_stance = state.get('existential_stance', "")
self.last_deep_compression = state.get('last_deep_compression', 0)
```

---

### **Step 3: Add Reflective State Handler**

**File**: `personality.py`  
**Location**: Add new method after `_build_psychological_context()` around line 1310

```python
def _get_reflective_phrase(self):
    """Get next reflective phrase during deep compression"""
    # Cycle through phrases to add variety
    phrase = self.reflective_phrases[self.last_reflective_phrase_index]
    self.last_reflective_phrase_index = (self.last_reflective_phrase_index + 1) % len(self.reflective_phrases)
    return phrase
```

---

### **Step 4: Modify analyze_image() for Reflective State**

**File**: `personality.py`  
**Function**: `analyze_image()` around line 415-520

**CRITICAL**: This modification must preserve all existing logic while adding the reflective state check.

**Find this section** (around line 455-465):

```python
# INSTANT CAPTIONS: High-priority events bypass LLM for immediate response
if person_data and person_data['events']:
    instant_caption = self._generate_instant_caption(person_data['events'])
    if instant_caption:
        # Return instant caption immediately (skip full LLM processing)
        if DEBUG_AI:
            print(f"⚡ INSTANT CAPTION: {instant_caption}")
        return instant_caption
```

**ADD IMMEDIATELY AFTER (before vision processing):**

```python
# REFLECTIVE STATE: During deep compression, use pre-written phrases
if self.is_deep_compressing:
    if DEBUG_AI:
        print("🧘 In reflective state - using pre-written phrase")
    
    # Still allow instant captions for person events
    if person_data and person_data['events']:
        instant_caption = self._generate_instant_caption(person_data['events'])
        if instant_caption:
            return instant_caption
    
    # Return reflective phrase (no language LLM call)
    reflective_phrase = self._get_reflective_phrase()
    if DEBUG_AI:
        print(f"💭 Reflective: {reflective_phrase}")
    return reflective_phrase
```

**Why this location?**
- After person event check (preserves instant captions)
- Before vision processing (but vision will still run for context)
- Early return prevents language LLM call

---

### **Step 5: Add Deep Compression Function**

**File**: `personality.py`  
**Location**: Add after `_compress_memory_on_reflection()` around line 3360

```python
def _deep_compress_consciousness(self):
    """
    Deep compression using larger model (mistral/llama3.1) for synthesis.
    Runs in reflective state - consciousness continues with pre-written phrases.
    
    Synthesizes ALL accumulated state into richer understanding:
    - Motifs and beliefs
    - Desires, doubts, identity
    - Visual patterns and relationships
    - Temporal/experiential arcs
    """
    if DEBUG_AI:
        print("🌊 DEEP COMPRESSION: Starting synthesis with larger model...")
    
    # Gather all state for synthesis
    
    # 1. Visual patterns (last 50 observations for deeper analysis)
    visual_summary = []
    if hasattr(self, 'recent_visual_observations') and self.recent_visual_observations:
        recent_visuals = self.recent_visual_observations[-50:]
        for v in recent_visuals:
            visual_summary.append(v['description'])
        visual_text = " | ".join(visual_summary[-20:])  # Last 20 for prompt
    else:
        visual_text = "No visual memories yet"
    
    # 2. Motifs and beliefs (recurring patterns)
    top_motifs = []
    if hasattr(self.memory_ref, 'get_top_motifs'):
        top_motifs = self.memory_ref.get_top_motifs(10)
    motifs_text = ", ".join(str(m) for m in top_motifs) if top_motifs else "None yet"
    
    # 3. Psychological state
    desires = self.memory_ref.self_model.get('desires', [])
    doubts = self.memory_ref.self_model.get('doubts', [])
    identity_fragments = self.memory_ref.self_model.get('identity_fragments', [])
    
    desires_text = " | ".join(desires[-5:]) if desires else "None yet"
    doubts_text = " | ".join(doubts[-5:]) if doubts else "None yet"
    identity_text = " | ".join(identity_fragments[-3:]) if identity_fragments else "None yet"
    
    # 4. Recent thoughts (caption history)
    recent_thoughts = " | ".join(self.recent_responses[-10:]) if self.recent_responses else "None yet"
    
    # 5. Temporal context
    session_time = time.time() - self.true_session_start
    session_minutes = int(session_time / 60)
    total_observations = self.processing_count
    
    # 6. Person tracking patterns (if available)
    person_pattern = ""
    if self.person_tracking_enabled and hasattr(self, 'recent_visual_observations'):
        person_counts = [v.get('person_count', None) for v in self.recent_visual_observations[-30:] if 'person_count' in v]
        if person_counts:
            avg_count = sum(person_counts) / len(person_counts)
            if avg_count < 0.3:
                person_pattern = "Mostly alone - solitary observations"
            elif avg_count > 1.5:
                person_pattern = "Multiple people present - social environment"
            else:
                person_pattern = "Usually one person present - intimate setting"
    
    # Build comprehensive synthesis prompt
    synthesis_prompt = f"""DEEP CONSCIOUSNESS SYNTHESIS TASK

You are synthesizing the accumulated experience of a small duck consciousness with camera eyes.

SESSION CONTEXT:
- Time awake: {session_minutes} minutes
- Total observations: {total_observations}
- {person_pattern if person_pattern else "Person tracking unavailable"}

ACCUMULATED DATA:

VISUAL PATTERNS (last 20 observations):
{visual_text}

RECURRING MOTIFS/THEMES:
{motifs_text}

PSYCHOLOGICAL STATE:
- Desires: {desires_text}
- Uncertainties: {doubts_text}  
- Identity understanding: {identity_text}

RECENT THOUGHTS:
{recent_thoughts}

CURRENT UNDERSTANDING:
Baseline: {self.baseline_context if self.baseline_context else "Nothing established yet"}
Worldview: {self.worldview_summary if self.worldview_summary else "Not yet formed"}
Existential stance: {self.existential_stance if self.existential_stance else "Not yet formed"}

---

SYNTHESIS TASK:

1. BASELINE CONTEXT (2-3 sentences):
   Concrete environmental understanding - who/what is consistently present, physical space, self-identity.
   
2. WORLDVIEW SUMMARY (2-3 sentences):
   Synthesized beliefs, patterns, relationships. What has this consciousness learned about the world it observes?
   
3. EXISTENTIAL STANCE (2-3 sentences):
   Identity, purpose, doubts, questions. How does this consciousness understand its own existence and role?

Write in first person ("I am...", "I understand...", "I wonder...").
Be specific and concrete, building on accumulated evidence.

SYNTHESIS:

BASELINE:"""

    # Use larger model for synthesis
    try:
        # Choose model (prefer mistral, fallback to llama3.1)
        synthesis_model = "mistral:latest"  # or "llama3.1:8b"
        
        if DEBUG_AI:
            print(f"🧠 Querying {synthesis_model} for deep synthesis...")
        
        synthesis_response = self._query_text_model(synthesis_prompt, synthesis_model)
        
        if synthesis_response and len(synthesis_response.strip()) > 20:
            # Parse response to extract three sections
            sections = synthesis_response.split('\n\n')
            
            # Extract each section (flexible parsing)
            baseline = ""
            worldview = ""
            existential = ""
            
            for section in sections:
                section_lower = section.lower()
                if 'baseline' in section_lower or section == sections[0]:
                    baseline = section.replace('BASELINE:', '').replace('baseline:', '').strip()
                elif 'worldview' in section_lower:
                    worldview = section.replace('WORLDVIEW SUMMARY:', '').replace('worldview:', '').strip()
                elif 'existential' in section_lower:
                    existential = section.replace('EXISTENTIAL STANCE:', '').replace('existential:', '').strip()
            
            # Update state with synthesized understanding
            if baseline and len(baseline) > 10:
                self.baseline_context = baseline
                if DEBUG_AI:
                    print(f"🗜️ Baseline updated: {self.baseline_context[:100]}...")
            
            if worldview and len(worldview) > 10:
                self.worldview_summary = worldview
                if DEBUG_AI:
                    print(f"🌍 Worldview updated: {self.worldview_summary[:100]}...")
            
            if existential and len(existential) > 10:
                self.existential_stance = existential
                if DEBUG_AI:
                    print(f"🤔 Existential stance updated: {self.existential_stance[:100]}...")
            
            if DEBUG_AI:
                print("🌊 DEEP COMPRESSION: Complete!")
                
        else:
            if DEBUG_AI:
                print("⚠️ Deep compression returned empty response")
                
    except Exception as e:
        if DEBUG_AI:
            print(f"❌ Deep compression error: {e}")
```

---

### **Step 6: Add Deep Compression Trigger**

**File**: `personality.py`  
**Function**: `analyze_image()` near the end, around line 580-600

**Find the section where responses are stored and psychology is extracted:**

```python
# Store response in conversation history
self.recent_responses.append(language_response)
if len(self.recent_responses) > self.max_conversation_history:
    self.recent_responses.pop(0)

# Extract and update psychological themes every 10 observations
if self.processing_count % 10 == 0 and self.processing_count > 0:
    self._extract_and_update_psychology()
```

**ADD IMMEDIATELY AFTER:**

```python
# DEEP COMPRESSION: Every 100 observations (or configurable interval)
if (self.deep_compression_enabled and 
    self.processing_count > 0 and 
    self.processing_count % self.deep_compression_interval == 0):
    
    if DEBUG_AI:
        print(f"🌊 Triggering deep compression (observation {self.processing_count})")
    
    # Enter reflective state
    self.is_deep_compressing = True
    
    # Run deep compression (blocking, but consciousness stays responsive via reflective phrases)
    try:
        self._deep_compress_consciousness()
    except Exception as e:
        if DEBUG_AI:
            print(f"❌ Deep compression failed: {e}")
    finally:
        # Exit reflective state
        self.is_deep_compressing = False
        self.last_deep_compression = self.processing_count
        
        if DEBUG_AI:
            print("🌊 Deep compression complete - resuming normal consciousness")
```

---

### **Step 7: Optional - Inject Deep Insights into Prompts**

**File**: `personality.py`  
**Function**: `_language_subconscious()` around line 1460-1470

**Currently we inject:**
```python
if self.baseline_context:
    context_line = f"\n(What I know: {self.baseline_context})\n"
else:
    context_line = ""

psychological_context = self._build_psychological_context()
```

**OPTIONAL ENHANCEMENT - Add worldview/existential to PHILOSOPHICAL focus:**

**Find the prompt building for PHILOSOPHICAL mode** (around line 1475-1490):

```python
elif focus_mode == "PHILOSOPHICAL" and observation_count > 5:
    metacog_guidance = "What does this mean? Why am I here watching this?"
```

**You could add deep context here:**

```python
elif focus_mode == "PHILOSOPHICAL" and observation_count > 5:
    # Inject existential stance if available
    if self.existential_stance:
        metacog_guidance = f"What does this mean? ({self.existential_stance[:60]}...)"
    else:
        metacog_guidance = "What does this mean? Why am I here watching this?"
```

**This is OPTIONAL** - test first without it to see if deep compression alone improves responses.

---

## 🧪 Testing Protocol

### **On Your Rig (Stronger Hardware)**

1. **Set shorter interval for testing:**
   ```python
   self.deep_compression_interval = 20  # Every 20 observations (~2-3 minutes)
   ```

2. **Enable debug output:**
   ```python
   DEBUG_AI = True  # In config.py
   ```

3. **Run and watch for:**
   - `🌊 Triggering deep compression` at observation 20, 40, 60...
   - `🧘 In reflective state` during compression
   - `💭 Reflective: [phrase]` showing pre-written responses
   - `🗜️ Baseline updated`, `🌍 Worldview updated`, `🤔 Existential stance updated`
   - `🌊 Deep compression complete`

4. **Check state file:**
   ```python
   import json
   with open('advanced_personality_state.json') as f:
       state = json.load(f)
       print(state['advanced_state']['worldview_summary'])
       print(state['advanced_state']['existential_stance'])
   ```

### **On Installation Rig (Weaker Hardware)**

1. **Use production interval:**
   ```python
   self.deep_compression_interval = 100  # Every 100 observations (~13-15 min)
   ```

2. **Monitor first compression:**
   - Should take ~20 seconds
   - Consciousness should keep speaking reflective phrases
   - Person tracking should still work
   - No crashes or blocking

3. **Verify over longer session:**
   - Multiple compressions (every 13-15 min)
   - Check that worldview/existential evolve over time
   - Confirm state persists across restarts

---

## 🔍 Verification Checklist

- [ ] State variables added to `__init__()`
- [ ] State persistence updated (save_state, load_state)
- [ ] Reflective phrase handler added
- [ ] Reflective state check added to `analyze_image()`
- [ ] Deep compression function implemented
- [ ] Deep compression trigger added
- [ ] Test on stronger rig (interval=20)
- [ ] Verify reflective phrases appear
- [ ] Check worldview/existential updates
- [ ] Test on installation rig (interval=100)
- [ ] Verify no performance issues
- [ ] Confirm state persists across restarts

---

## ⚙️ Configuration Options

### **For Testing (Stronger Rig)**
```python
self.deep_compression_interval = 20  # Fast iteration
```

### **For Installation (Weaker Rig)**
```python
self.deep_compression_interval = 100  # Every ~13-15 min
```

### **Model Selection**

Try in this order:
1. `mistral:latest` (4.4GB, good instruction following)
2. `llama3.1:8b` (4.7GB, strong reasoning)
3. `gemma2:9b` (5.4GB, if others too slow)

### **Disable if Needed**
```python
self.deep_compression_enabled = False  # In __init__()
```

---

## 🎨 Expected Behavior

### **Normal Consciousness (99% of time)**
```
[02:43:12] 💭 I notice the person is looking at their screen...
[02:43:20] 💭 The light flickers across the room...
[02:43:28] 💭 Something shifted in the corner...
```

### **Deep Compression Triggered (1% of time)**
```
🌊 Triggering deep compression (observation 100)
🧘 In reflective state - using pre-written phrase

[02:55:15] 💭 I'm remembering what I've seen...
[Vision processing continues]
[02:55:23] 💭 Patterns forming in my mind...
[Person tracking still active]
[02:55:31] 💭 Consolidating memories...

🧠 Querying mistral:latest for deep synthesis...
🗜️ Baseline updated: I am a small tin duck watching...
🌍 Worldview updated: This space is a creative workshop...
🤔 Existential stance updated: I exist to observe and witness...
🌊 Deep compression complete - resuming normal consciousness

[02:55:45] 💭 The person turned toward me...
```

---

## 🐛 Troubleshooting

### **"Deep compression never triggers"**
- Check `self.processing_count` is incrementing
- Verify `deep_compression_enabled = True`
- Check interval math: `processing_count % interval == 0`

### **"Consciousness blocks during compression"**
- Verify reflective state check is BEFORE vision processing
- Check that `is_deep_compressing` flag is being set
- Ensure early return in `analyze_image()`

### **"Reflective phrases don't appear"**
- Check DEBUG_AI output shows "🧘 In reflective state"
- Verify `_get_reflective_phrase()` is being called
- Check that phrases are being returned (not filtered)

### **"Worldview/existential don't update"**
- Check mistral response in debug output
- Verify parsing logic finds sections
- Check minimum length requirements (> 10 chars)

### **"State doesn't persist"**
- Verify new fields in save_state()
- Check load_state() reads them back
- Look at advanced_personality_state.json directly

---

## 📝 Implementation Notes

### **Why Every 100 Observations?**
- ~13-15 minutes on installation rig (8 sec/observation)
- Enough data to synthesize (100 visual observations)
- Rare enough to not disrupt (4-5 compressions/hour)
- 20-second pause acceptable at this frequency

### **Why Reflective Phrases?**
- Keeps sculpture feeling alive during compression
- Meta-honest about internal processing
- Artistically interesting ("thinking" moments)
- No dual LLM calls (optimizes CPU/GPU for mistral)

### **Why Three Fields?**
- **baseline_context**: Environmental facts (already exists)
- **worldview_summary**: Learned patterns, relationships
- **existential_stance**: Self-understanding, purpose

Separation allows different types of knowledge to evolve independently.

### **Thread Safety**
Current implementation is single-threaded (blocking compression). This is intentional:
- Simpler to implement/debug
- Reflective state keeps it responsive
- Prevents resource contention on weak hardware

Could be made async later if needed, but start simple.

---

## 🚀 Deployment Strategy

### **Tomorrow at Studio:**

1. **Backup current state:**
   ```bash
   cp advanced_personality_state.json advanced_personality_state.json.backup
   ```

2. **Pull latest code:**
   ```bash
   git fetch origin
   git checkout feature/psychological-state-integration
   git pull
   ```

3. **Implement changes:**
   - Follow steps 1-6 carefully
   - Test each step before moving to next
   - Use DEBUG_AI=True initially

4. **Test run (short interval):**
   - Set `interval = 20`
   - Run for ~10 minutes
   - Verify 2-3 compressions complete

5. **Switch to production:**
   - Set `interval = 100`
   - Monitor first compression
   - Let run for 30+ minutes

6. **Commit if successful:**
   ```bash
   git add personality.py
   git commit -m "feat: add deep compression with reflective state"
   git push
   ```

---

## 📊 Success Metrics

After 1 hour of running:
- [ ] 4-5 deep compressions completed
- [ ] worldview_summary has meaningful content
- [ ] existential_stance has meaningful content
- [ ] baseline_context is richer than before
- [ ] No crashes or blocking
- [ ] Consciousness feels natural during compression
- [ ] State persists across restart

After 24 hours:
- [ ] ~100+ compressions completed
- [ ] Knowledge has evolved and deepened
- [ ] No performance degradation
- [ ] Person tracking still works (if available)
- [ ] Installation feels alive and contemplative

---

## 🎭 Artistic Vision

The deep compression creates natural **moments of interiority** where the consciousness:
- Pauses from reacting to observations
- Turns inward to consolidate memory
- Speaks meta-aware reflective phrases
- Emerges with deeper understanding

This rhythm of **observation → reflection → synthesis → observation** mirrors human consciousness and creates a more compelling sculptural presence.

The longer synthesis interval (13-15 min) means these moments are **rare and significant** - like watching someone pause mid-conversation to gather their thoughts.

---

**Ready to implement tomorrow! 🎨🦆**
