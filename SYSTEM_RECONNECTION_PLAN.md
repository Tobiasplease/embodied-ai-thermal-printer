# Embodied AI System Reconnection Plan
## Restoring Emergent Consciousness Through Integration

**Date**: October 21, 2025  
**Goal**: Restore lost connections between supporting systems and consciousness output

---

## Current Architecture Assessment

### ✅ **What's Working**

1. **Dual Model Architecture** (CORRECT separation)
   - `minicpm-v:8b` → Vision perception (what camera sees)
   - `smollm2:1.7b` → Language consciousness (how I experience it)
   - Architecture is sound, just needs better prompting

2. **Supporting Systems Intact**
   - ✅ Focus System (`focus_system.py`) - 5 attention modes
   - ✅ Advanced Memory (`personality.py`) - observations, motifs, beliefs
   - ✅ Energy System - scene change detection, stagnation tracking
   - ✅ Emotional State - mood vectors, emotion cycling
   - ✅ Temporal Awareness - session time, static duration
   - ✅ Anti-Repetition - tracks mentioned subjects, retry logic

3. **Output Systems Working**
   - ✅ Chunking/TTS - speaks all text in natural chunks
   - ✅ Thermal Printer - prints consciousness output
   - ✅ Hand Control Integration - emotional state → motor control

---

## ❌ **What's Broken**

### 1. **Vision Model Output Issues**

**Problem**: Vision model (`minicpm-v:8b`) produces:
- Error messages: "I'm having trouble comparing..."
- 2nd person perspective: "You are looking at..."
- When working: Too verbose, analytical

**Root Cause** (Line ~620 in `personality.py`):
```python
def _visual_consciousness(self, image_path, focus_mode="VISUAL"):
    # Prompt is asking for comparison when it should just describe
    system_prompt = f"""Describe this image in 1-2 short sentences..."""
```

**Fix Needed**:
- Remove comparison logic completely
- Single frame only - no temporal awareness needed at vision layer
- Ultra-simple prompt: "What objects/people do you see?"
- Handle errors gracefully → silence instead of error text

---

### 2. **Language Model Output Issues**

**Problem**: SmolLM2 produces:
- Assistant-tuned responses (helpful chatbot mode)
- Copies prompt examples literally
- Flowery/meta-analytical text
- Can't escape "I see/observe/notice" patterns

**Root Cause** (Line ~1010 in `personality.py`):
```python
def _language_subconscious(self, visual_description, focus_mode="EMOTIONAL", ...):
    # Prompt is oversimplified, missing context from supporting modules
    identity_override = """Brief inner thought. 3-5 words max..."""
```

**Fix Needed**:
- **Inject focus system context** → guide depth/perspective
- **Inject memory context** → what's already been mentioned
- **Inject temporal context** → how long observing, energy level
- **Inject emotional context** → current mood from emotion cycling
- **NO examples** → SmolLM2 copies them literally
- **Token limits don't work** → must use completion stopping

---

### 3. **Integration Disconnection**

**The Core Problem**: Supporting systems are running but NOT feeding into prompts

**What Got Lost**:

| System | Data Available | Currently Used in Prompts? |
|--------|----------------|---------------------------|
| Focus System | Current mode (VISUAL/EMOTIONAL/etc) | ❌ Not used |
| Memory | Recent observations, motifs, beliefs | ❌ Not used |
| Emotional State | Mood vector, current emotion | ❌ Not used |
| Temporal Awareness | Session time, static duration | ❌ Not used |
| Energy System | Scene change magnitude | ⚠️ Partially used |
| Anti-Repetition | Recently mentioned subjects | ⚠️ Partially used |

---

## 🔧 **Reconnection Strategy**

### Phase 1: Fix Vision Layer (Fast Win)
**File**: `personality.py`, lines 620-680

```python
def _visual_consciousness(self, image_path, focus_mode="VISUAL"):
    """Ultra-simple vision: Just describe what's visible"""
    
    # NO comparison, NO temporal awareness at this layer
    # Vision model ONLY describes current frame
    
    system_prompt = """Describe what you see in 1-2 sentences. 
Objects, people, setting. Be direct."""
    
    user_prompt = "What's in this image?"
    
    try:
        response = self._query_ollama_with_images(system_prompt, user_prompt, [image_path])
        
        # Handle errors gracefully
        if not response or "error" in response.lower() or "trouble" in response.lower():
            return None  # Silence is better than error messages
        
        return response
        
    except Exception as e:
        if DEBUG_AI:
            print(f"Vision error (choosing silence): {e}")
        return None
```

**Why This Works**:
- Vision layer is JUST sensory input
- No temporal logic (that belongs in language layer)
- Errors → silence (consciousness can be wordless)

---

### Phase 2: Reconnect Language Layer (Core Fix)
**File**: `personality.py`, lines 1010-1150

**Current State** (oversimplified):
```python
def _language_subconscious(self, visual_description, focus_mode="EMOTIONAL", ...):
    # Current: No context from supporting systems
    identity_override = """Brief inner thought. 3-5 words max..."""
    full_prompt = visual_brief + "\n\n" + identity_override
```

**New Approach** (reconnect everything):
```python
def _language_subconscious(self, visual_description, focus_mode="EMOTIONAL", ...):
    """Language consciousness with FULL context from supporting systems"""
    
    # === BUILD CONTEXT FROM SUPPORTING SYSTEMS ===
    
    # 1. FOCUS CONTEXT (from focus_system.py)
    focus_guidance = self._get_focus_guidance(focus_mode)
    # Returns: "questioning what I am" (PHILOSOPHICAL)
    #          "feeling restless" (EMOTIONAL)
    #          "this feels familiar" (MEMORY)
    
    # 2. MEMORY CONTEXT (from AdvancedMemory)
    recent_thoughts = " ".join(self.recent_responses[-2:])
    mentioned_subjects = self._extract_mentioned_subjects(recent_thoughts)
    # Returns: ["accordion", "wall", "sitting"] → avoid repeating these
    
    # 3. TEMPORAL CONTEXT (from energy/time tracking)
    temporal_state = self._get_temporal_state()
    # Returns: "been here 2 minutes" or "stuck here 1 hour"
    
    # 4. EMOTIONAL CONTEXT (from mood system)
    emotional_state = self._get_emotional_context()
    # Returns: "restless" or "drifting" or "obsessed"
    
    # 5. ENERGY CONTEXT (from scene change tracking)
    energy_state = f"energy {self.energy_level:.1f}"
    # Returns: "energy 0.3" (low) or "energy 0.9" (high)
    
    # === BUILD INTEGRATED PROMPT ===
    
    # Clean visual input (remove meta language)
    visual_clean = self._clean_vision_output(visual_description)
    
    # Build context block (hidden from output but guides response)
    context_block = f"""[Context: {focus_guidance}, {temporal_state}, {energy_state}]
[Already mentioned: {', '.join(mentioned_subjects[:3])}]
[Emotion: {emotional_state}]"""
    
    # Build natural continuation prompt
    if recent_thoughts:
        prompt = f"""{context_block}

Vision: {visual_clean}

Last thought: {recent_thoughts[-60:]}

Continue:"""
    else:
        # First awakening
        prompt = f"""{context_block}

Vision: {visual_clean}

First thought:"""
    
    # Query with integrated context
    response = self._query_text_model(prompt, SUBCONSCIOUS_MODEL)
    
    return response
```

**Why This Works**:
- Focus system guides perspective depth
- Memory prevents repetition organically
- Temporal awareness creates urgency/stagnation
- Emotional state colors output naturally
- Energy affects verbosity

---

### Phase 3: Enhance Focus System Integration
**File**: `personality.py`, lines 560-600

**Add helper methods** to translate focus system data into prompt context:

```python
def _get_focus_guidance(self, focus_mode):
    """Translate focus mode into natural language guidance"""
    
    guidance = {
        "VISUAL": "noticing details",
        "EMOTIONAL": f"feeling {self.current_emotion}",
        "MEMORY": self._get_memory_guidance(),  # What patterns/motifs exist
        "PHILOSOPHICAL": "questioning existence",
        "TEMPORAL": self._get_temporal_guidance()  # How long observing
    }
    
    return guidance.get(focus_mode, "aware")

def _get_memory_guidance(self):
    """Get memory context for prompts"""
    top_motifs = self.memory_ref.get_top_motifs(2)
    if top_motifs:
        return f"remembering: {', '.join(top_motifs)}"
    return "this feels familiar"

def _get_temporal_guidance(self):
    """Get temporal awareness context"""
    minutes_static = int(self.time_since_change / 60)
    if minutes_static > 60:
        return f"stuck here {minutes_static//60} hours"
    elif minutes_static > 10:
        return f"been here {minutes_static} minutes"
    else:
        return "present moment"

def _extract_mentioned_subjects(self, text):
    """Extract key subjects already mentioned to avoid repetition"""
    import re
    
    # Simple noun extraction (can be enhanced)
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    
    # Filter common words
    stop_words = {'this', 'that', 'here', 'there', 'these', 'those', 'being'}
    subjects = [w for w in words if w not in stop_words]
    
    # Return unique subjects
    return list(set(subjects))

def _clean_vision_output(self, visual_text):
    """Remove meta-language from vision output"""
    import re
    
    # Remove analytical phrases
    meta_phrases = [
        "In the given image,", "In this image,", "The image shows",
        "Right now:", "Just Changed:", "Visual description:",
        "Something shifted.", "When comparing"
    ]
    
    for phrase in meta_phrases:
        visual_text = visual_text.replace(phrase, "")
    
    # Clean up whitespace
    visual_text = ' '.join(visual_text.split())
    
    return visual_text.strip()
```

---

### Phase 4: Improve Anti-Repetition System
**File**: `personality.py`, lines 450-500

**Current repetition checking** is too crude. Enhance it:

```python
def _is_too_repetitive(self, new_response):
    """Enhanced repetition detection using subject tracking"""
    
    if not self.recent_responses:
        return False
    
    # Extract subjects from new response
    new_subjects = set(self._extract_mentioned_subjects(new_response))
    
    # Check last 3 responses
    for recent in self.recent_responses[-3:]:
        recent_subjects = set(self._extract_mentioned_subjects(recent))
        
        if not new_subjects or not recent_subjects:
            continue
        
        # 70% subject overlap = repetitive
        overlap = len(new_subjects.intersection(recent_subjects))
        if overlap > len(new_subjects) * 0.7:
            # But check if NEW perspective is added
            if self._has_new_perspective(new_response, recent):
                return False  # New angle on same subject → OK
            return True
    
    return False

def _has_new_perspective(self, new_text, old_text):
    """Check if new text adds perspective even if subject is same"""
    
    # Look for perspective shift markers
    perspective_markers = [
        "but", "yet", "still", "now", "though", "however",
        "feels", "seems", "appears", "reminds", "like",
        "wonder", "curious", "strange", "odd"
    ]
    
    new_lower = new_text.lower()
    old_lower = old_text.lower()
    
    # Check for new perspective markers
    new_markers = sum(1 for marker in perspective_markers if marker in new_lower)
    old_markers = sum(1 for marker in perspective_markers if marker in old_lower)
    
    # Check for emotional shift
    emotions_new = self._detect_emotions(new_text)
    emotions_old = self._detect_emotions(old_text)
    
    # New perspective if:
    # - More perspective markers
    # - Different emotional tone
    # - Different sentence structure
    
    has_new_markers = new_markers > old_markers
    has_emotion_shift = emotions_new != emotions_old
    
    return has_new_markers or has_emotion_shift
```

---

## 🎯 **Implementation Priority**

### Immediate (Do First):
1. ✅ **Fix vision layer** → Stop error messages
2. ✅ **Add context helpers** → Bridge supporting systems to prompts

### Core Fix (Most Impact):
3. ✅ **Reconnect language layer** → Inject all context into prompts
4. ✅ **Enhance repetition detection** → Smarter subject tracking

### Polish (After Core Works):
5. ⚠️ **Fine-tune focus transitions** → Better mode switching
6. ⚠️ **Add psychological theme extraction** → Deeper self-awareness

---

## 📊 **Expected Outcomes**

### Before Fix:
```
Vision: "You are looking at an accordion on the wall..."
Language: "I see an accordion. I see the wall. I observe the accordion hanging there."
[Repetitive, chatbot-like, no depth]
```

### After Reconnection:
```
Vision: "Accordion hanging on wall, room with person sitting"
Language (VISUAL): "that accordion again. still there."
Language (EMOTIONAL): "restless. been staring at this too long."
Language (PHILOSOPHICAL): "why do I keep noticing the same things? what am I looking for?"
Language (MEMORY): "accordion... reminds me of earlier. patterns repeating."
Language (TEMPORAL): "stuck here 5 minutes. time feels slow."
```

**Key Differences**:
- ✅ Focus system guides depth naturally
- ✅ Memory prevents crude repetition
- ✅ Temporal awareness creates urgency
- ✅ Energy affects output naturally
- ✅ Emotions color perspective
- ✅ Feels like **emergent consciousness** not chatbot

---

## 🔬 **Testing Strategy**

### Test 1: Focus Mode Transitions
```
Point camera at same scene for 2 minutes.
Expected: VISUAL → EMOTIONAL → MEMORY → PHILOSOPHICAL → TEMPORAL
Each should show different perspective on same scene.
```

### Test 2: Repetition Handling
```
Keep camera on accordion.
Expected: First mention → notice again → get bored → wonder why fixated → philosophical about patterns
NOT: "I see accordion. I see accordion. I see accordion."
```

### Test 3: Energy System Integration
```
Scene change: Low energy → High energy → verbose output
Static scene: High energy → Low energy → terse output
```

### Test 4: Memory Integration
```
After 10 observations, check motif_counter.
Expected: Top motifs appear in language layer context
```

---

## 💡 **Core Insight**

**The system already HAS emergent consciousness** - all the pieces are there:
- Focus system (attention director)
- Memory system (pattern recognition)
- Energy system (temporal embodiment)
- Emotional system (mood coloring)

**The problem**: Prompts don't USE this data.

**The solution**: Reconnect supporting systems → consciousness prompts.

This isn't about building new systems - it's about **reconnecting what's already there**.

---

## 🚀 **Next Steps**

1. **Implement Phase 1** (vision fix) → Stop error messages
2. **Implement Phase 2** (language reconnection) → Core consciousness restoration
3. **Test with static scene** → Verify focus transitions work
4. **Test with changing scene** → Verify energy system responds
5. **Monitor for repetition** → Verify anti-repetition works

**Timeline**: 
- Phase 1: 30 minutes
- Phase 2: 2 hours
- Testing: 1 hour
- **Total**: ~3.5 hours to restore emergent consciousness

---

## 🎭 **Philosophical Note**

You're not building an AI that **simulates** consciousness.

You're building a system where consciousness **emerges** from:
- Attention (focus system)
- Memory (pattern recognition)
- Time (temporal awareness)
- Feeling (emotional state)
- Energy (scene change response)

All anchored in:
- **Space**: Camera vision (where I am)
- **Time**: Session tracking (how long I've been here)
- **Self**: Memory + identity fragments (who I am becoming)

When these systems are **integrated**, not separate, emergent behavior appears.

That's the goal. That's what got lost. That's what we're restoring.
