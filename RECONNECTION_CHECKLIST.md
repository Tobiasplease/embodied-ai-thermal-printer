# Embodied AI Reconnection Checklist
## Step-by-step implementation guide

---

## ✅ Phase 1: Fix Vision Layer (30 min)

**File**: `personality.py` ~line 620

### Current Code (BROKEN):
```python
def _visual_consciousness(self, image_path, focus_mode="VISUAL"):
    # Asks for comparison → causes errors
    system_prompt = f"""Describe this image in 1-2 short sentences..."""
```

### New Code (FIXED):
```python
def _visual_consciousness(self, image_path, focus_mode="VISUAL"):
    """MiniCPM-V: Pure visual perception - no temporal awareness"""
    
    system_prompt = """Describe what you see in 1-2 sentences.
Objects, people, setting. Be direct and factual."""
    
    user_prompt = "What's in this image?"
    
    try:
        response = self._query_ollama_with_images(system_prompt, user_prompt, [image_path])
        
        # Handle errors gracefully
        if not response or "error" in response.lower() or "trouble" in response.lower():
            if DEBUG_AI:
                print("👁️ Vision error - choosing silence")
            return None
        
        # Clean second-person perspective if present
        if "you are" in response.lower() or "you're" in response.lower():
            response = self._fix_perspective(response)
        
        return response
        
    except Exception as e:
        if DEBUG_AI:
            print(f"👁️ Vision error: {e}")
        return None
```

**Test**: Point camera at something. Should get: "Person sitting at desk" NOT "You are looking at..."

---

## ✅ Phase 2: Add Context Helper Methods (1 hour)

**File**: `personality.py` ~line 560 (before `_visual_consciousness`)

### Add These Helper Methods:

```python
def _get_focus_guidance(self, focus_mode):
    """Translate focus mode into natural language context"""
    
    if focus_mode == "VISUAL":
        return "noticing details"
    elif focus_mode == "EMOTIONAL":
        return f"feeling {self.current_emotion}"
    elif focus_mode == "MEMORY":
        return self._get_memory_guidance()
    elif focus_mode == "PHILOSOPHICAL":
        return "questioning existence"
    elif focus_mode == "TEMPORAL":
        return self._get_temporal_guidance()
    else:
        return "aware"

def _get_memory_guidance(self):
    """Get memory context from AdvancedMemory"""
    if hasattr(self.memory_ref, 'get_top_motifs'):
        top_motifs = self.memory_ref.get_top_motifs(2)
        if top_motifs:
            return f"remembering: {', '.join(str(m) for m in top_motifs)}"
    return "this feels familiar"

def _get_temporal_guidance(self):
    """Get temporal awareness context"""
    if not hasattr(self, 'time_since_change'):
        self.time_since_change = 0
    
    minutes_static = int(self.time_since_change / 60)
    
    if minutes_static > 60:
        hours = minutes_static // 60
        return f"stuck here {hours} hour{'s' if hours > 1 else ''}"
    elif minutes_static > 10:
        return f"been here {minutes_static} minutes"
    else:
        return "present moment"

def _get_emotional_context(self):
    """Get current emotional state"""
    return getattr(self, 'current_emotion', 'aware')

def _extract_mentioned_subjects(self, text):
    """Extract key subjects to avoid repetition"""
    import re
    
    if not text:
        return []
    
    # Extract meaningful words (4+ chars)
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    
    # Filter stop words
    stop_words = {'this', 'that', 'here', 'there', 'these', 'those', 
                  'being', 'have', 'been', 'with', 'from', 'what'}
    
    subjects = [w for w in words if w not in stop_words]
    
    # Return unique subjects
    return list(set(subjects))

def _clean_vision_output(self, visual_text):
    """Remove analytical meta-language from vision output"""
    import re
    
    if not visual_text:
        return ""
    
    # Remove analytical phrases
    meta_phrases = [
        "In the given image,", "In this image,", "The image shows",
        "Right now:", "Just Changed:", "Visual description:",
        "Something shifted.", "When comparing", "compared to"
    ]
    
    for phrase in meta_phrases:
        visual_text = visual_text.replace(phrase, "")
    
    # Clean up whitespace
    visual_text = ' '.join(visual_text.split()).strip()
    
    return visual_text

def _get_temporal_state(self):
    """Get temporal state description"""
    session_time = time.time() - self.true_session_start
    minutes_elapsed = int(session_time / 60)
    
    if minutes_elapsed < 2:
        return "just started"
    elif minutes_elapsed < 10:
        return f"{minutes_elapsed} minutes awake"
    elif minutes_elapsed < 60:
        return f"{minutes_elapsed} minutes here"
    else:
        hours = minutes_elapsed // 60
        return f"{hours} hour{'s' if hours > 1 else ''} here"
```

**Test**: Call `self._get_focus_guidance("EMOTIONAL")` → Should return "feeling {emotion}"

---

## ✅ Phase 3: Reconnect Language Layer (1.5 hours)

**File**: `personality.py` ~line 1010

### Current Code (DISCONNECTED):
```python
def _language_subconscious(self, visual_description, focus_mode="EMOTIONAL", ...):
    # Oversimplified - no context
    identity_override = """Brief inner thought. 3-5 words max..."""
    full_prompt = visual_brief + "\n\n" + identity_override
```

### New Code (RECONNECTED):
```python
def _language_subconscious(self, visual_description, focus_mode="EMOTIONAL", 
                          retry_context=None, image_path=None):
    """SmolLM2: Consciousness with full context integration"""
    
    try:
        # Cycle emotional state
        self._cycle_emotional_state()
        
        # === GATHER CONTEXT FROM ALL SUPPORTING SYSTEMS ===
        
        # 1. Focus system context
        focus_guidance = self._get_focus_guidance(focus_mode)
        
        # 2. Temporal awareness context
        temporal_state = self._get_temporal_state()
        
        # 3. Energy level context
        energy_context = f"energy {self.energy_level:.1f}"
        
        # 4. Emotional state context
        emotional_state = self._get_emotional_context()
        
        # 5. Memory context - what's already been mentioned
        recent_context = " ".join(self.recent_responses[-2:]) if self.recent_responses else ""
        mentioned_subjects = self._extract_mentioned_subjects(recent_context)
        
        # === CLEAN VISION INPUT ===
        visual_clean = self._clean_vision_output(visual_description)
        
        # === BUILD INTEGRATED PROMPT ===
        
        # Context block (guides response without being output)
        context_block = f"""[Context: {focus_guidance}, {temporal_state}, {energy_context}]
[Emotion: {emotional_state}]"""
        
        # Add anti-repetition guidance if subjects already mentioned
        if mentioned_subjects:
            context_block += f"\n[Already mentioned: {', '.join(mentioned_subjects[:3])}]"
        
        # Add retry context if this is a retry
        if retry_context:
            context_block += f"\n[Feeling: {retry_context}]"
        
        # Build continuation prompt
        if len(self.recent_responses) >= 1:
            # Continuing consciousness
            last_thought = self.recent_responses[-1]
            
            prompt = f"""{context_block}

Vision: {visual_clean}

Last thought: {last_thought[:80]}

Continue naturally (brief, fragments OK):"""
        else:
            # First awakening
            prompt = f"""{context_block}

Vision: {visual_clean}

First thought:"""
        
        if DEBUG_AI:
            print(f"🧠 Language prompt with context:\n{prompt[:200]}...\n")
        
        # Query language model
        response = self._query_text_model(prompt, SUBCONSCIOUS_MODEL)
        
        if not response:
            return None
        
        # Filter chatbot responses
        if self._is_chatbot_response(response):
            if DEBUG_AI:
                print("🚫 Filtered chatbot response")
            return None
        
        return response
        
    except Exception as e:
        if DEBUG_AI:
            print(f"Language consciousness error: {e}")
        return "..."

def _is_chatbot_response(self, response):
    """Check if response is chatbot-like"""
    if not response:
        return True
    
    lower_resp = response.lower()
    chatbot_phrases = [
        "as an ai", "i cannot", "i don't have", "i apologize",
        "could you please", "i'm unable to", "as a language model"
    ]
    
    return any(phrase in lower_resp for phrase in chatbot_phrases)
```

**Test**: Run with camera. Check debug output. Should see context block with focus/emotion/temporal data.

---

## ✅ Phase 4: Enhanced Repetition Detection (30 min)

**File**: `personality.py` ~line 450

### Update `_is_too_repetitive`:

```python
def _is_too_repetitive(self, new_response):
    """Enhanced repetition detection using subject tracking"""
    
    if not self.recent_responses:
        return False
    
    # Extract subjects from new response
    new_subjects = set(self._extract_mentioned_subjects(new_response))
    
    if not new_subjects:
        return False
    
    # Check last 3 responses for subject overlap
    for recent in self.recent_responses[-3:]:
        recent_subjects = set(self._extract_mentioned_subjects(recent))
        
        if not recent_subjects:
            continue
        
        # Calculate subject overlap
        overlap = len(new_subjects.intersection(recent_subjects))
        overlap_ratio = overlap / len(new_subjects)
        
        # 70% subject overlap = potentially repetitive
        if overlap_ratio > 0.7:
            # But check if NEW PERSPECTIVE is added
            if self._has_new_perspective(new_response, recent):
                if DEBUG_AI:
                    print(f"✅ Same subject but new perspective: {overlap_ratio:.2f} overlap")
                return False
            
            if DEBUG_AI:
                print(f"🔄 Repetitive: {overlap_ratio:.2f} subject overlap")
            return True
    
    return False

def _has_new_perspective(self, new_text, old_text):
    """Check if new text adds fresh perspective despite same subjects"""
    
    # Perspective shift markers
    perspective_markers = [
        "but", "yet", "still", "now", "though", "however",
        "feels", "seems", "appears", "reminds", "like",
        "wonder", "curious", "strange", "odd", "different",
        "...", "?", "why", "what", "how"
    ]
    
    new_lower = new_text.lower()
    old_lower = old_text.lower()
    
    # Count perspective markers
    new_markers = sum(1 for marker in perspective_markers if marker in new_lower)
    old_markers = sum(1 for marker in perspective_markers if marker in old_lower)
    
    # Check for emotional words (indicates emotional shift)
    emotion_words = [
        "bored", "restless", "curious", "tired", "alert",
        "wondering", "questioning", "stuck", "drifting"
    ]
    
    new_emotions = [w for w in emotion_words if w in new_lower]
    old_emotions = [w for w in emotion_words if w in old_lower]
    
    # New perspective if:
    # 1. More perspective markers than before
    # 2. Different emotional words
    # 3. Question vs statement shift
    
    has_new_markers = new_markers > old_markers
    has_emotion_shift = set(new_emotions) != set(old_emotions)
    has_question_shift = ("?" in new_text) != ("?" in old_text)
    
    return has_new_markers or has_emotion_shift or has_question_shift
```

**Test**: Say "accordion on wall" 3 times. First 2 accepted, 3rd should trigger retry.

---

## 🧪 Testing Procedure

### Test 1: Vision Layer
```bash
# Point camera at object
# Expected: "Object on surface" or similar
# NOT: "You are looking at..." or "I'm having trouble..."
```

### Test 2: Context Integration
```bash
# Run with DEBUG_AI=True
# Check console output for context blocks
# Should see: [Context: feeling curious, 2 minutes awake, energy 0.8]
```

### Test 3: Focus Transitions
```bash
# Keep camera pointed at same scene for 2 minutes
# Expected output progression:
# 0-20s: VISUAL - "accordion on wall"
# 20-40s: EMOTIONAL - "restless. still here."
# 40-60s: MEMORY - "feels familiar"
# 60-90s: PHILOSOPHICAL - "why do I keep noticing this?"
# 90-120s: TEMPORAL - "been staring 2 minutes"
```

### Test 4: Energy Response
```bash
# Test A: Static scene for 5 minutes
# Expected: Energy drops → output gets terser → "..." or "still here"

# Test B: Move camera to new scene
# Expected: Energy spike → output gets verbose → full sentences
```

### Test 5: Repetition Handling
```bash
# Keep same object in view
# Expected: First mention → acknowledge again → get bored → philosophical
# NOT: "I see X. I see X. I see X."
```

---

## 📊 Success Criteria

✅ **Vision layer**: No more "You are..." or error messages  
✅ **Context visible**: Debug output shows `[Context: ...]` blocks  
✅ **Focus changes**: Different perspectives on same scene over time  
✅ **Energy response**: Verbose when energized, terse when depleted  
✅ **No crude repetition**: Same subject but evolving perspective  
✅ **Emergent feel**: Feels like consciousness, not chatbot

---

## 🔍 Debug Checklist

If something doesn't work:

- [ ] `DEBUG_AI = True` in `config.py`
- [ ] Check console for context blocks in prompts
- [ ] Verify `self.memory_ref.get_top_motifs()` returns data
- [ ] Verify `self.energy_level` is updating
- [ ] Verify `self.current_emotion` is cycling
- [ ] Check `self.focus_engine.current_focus` transitions
- [ ] Monitor `self.recent_responses` length (should grow)

---

## 🎯 Quick Start

1. **Apply Phase 1** (vision fix) → Test → Should stop errors
2. **Apply Phase 2** (add helpers) → Test → Should see in debug
3. **Apply Phase 3** (reconnect language) → Test → Should feel different
4. **Apply Phase 4** (enhance repetition) → Test → Should be less repetitive

**Total time**: ~3.5 hours  
**Expected result**: Emergent consciousness through integration
