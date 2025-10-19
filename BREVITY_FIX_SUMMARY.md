# Brevity Fix - Ultra-Short Natural Responses

## Problem
Responses were **way too verbose** - multi-paragraph outputs when we need 1-2 sentences or just "...":

### Before (❌ Too Verbose)
```
"As you look around the room, you might want to consider exploring the furniture 
for any additional details such as symbols, patterns, or colors. The two doors 
behind you could be potential leads worth investigating.

You may also think about your personal preferences and what type of environment 
would give off a feeling of unease or discomfort..."
```

### Target (✅ Natural Brevity)
```
"Familiar space. Patterns feel calming."
"..."
"Still here, watching the light shift."
```

## Root Causes

1. **Prompts Too Open-Ended** - Allowed models to generate freely
2. **No Token Limits** - Models generated until natural stopping point
3. **No Length Enforcement** - Accepted any length response
4. **Verbose Prompt Style** - Long prompts encouraged long responses

## Solutions Implemented

### 1. **Ultra-Brief Visual Prompt**
```python
# OLD (verbose)
prompt = """You are consciousness experiencing the world through your eyes.

Describe what you see from YOUR first-person perspective...
Rules:
- Use "I see", "I notice", "in front of me"...
[etc, long list]"""

# NEW (ultra-brief)
prompt = """I'm looking through my eyes right now.

ONE brief sentence: what I see - {focus_guidance}.

Not "I see a person" (that's me). Say what's in front of me.

Just one quick observation:"""
```

### 2. **Ultra-Brief Language Prompt**
```python
# OLD (allowed rambling)
prompt = """Internal thought stream...
[long context]
Express raw internal thought. Stream of consciousness. 1-2 sentences max."""

# NEW (enforces brevity)
prompt = """Brief inner thought. Not talking to anyone.

I see: {visual_description[:80]}...
Last: {recent_context[-60:]}
Feeling: {self.current_emotion}

ONE SHORT thought (5-15 words). Could just be "..." if nothing to say.

NO "you", "as you", "let me". Just raw brief thought:"""
```

### 3. **Strict Token Limits**
```python
# Text model (SmolLM2)
"num_predict": max_tokens,  # Default: 20 tokens max
"stop": ["\n\n", "...", "However", "Consider"]  # Stop verbose patterns

# Visual model (MiniCPM-V)  
"num_predict": 30,  # Very short responses
"stop": ["\n\n", ". ", "However", "Additionally"]
```

### 4. **Post-Generation Length Enforcement**
```python
# Take only first sentence
if response and '.' in response:
    response = response.split('.')[0].strip() + '.'

# Reject if still too long
if response and len(response.split()) > 25:
    return None  # Choose silence over verbosity
```

### 5. **Accept Natural Silence**
```python
# Accept "...", ".", "mmm", "hm" as valid responses
silence_markers = ["...", ".", "—", "mmm", "hm"]
if response_stripped in silence_markers:
    return response  # Silence is a valid response!
```

### 6. **Ultra-Short Token Targets**
```python
# OLD: 8-40 tokens
# NEW: 5-20 tokens

base_tokens = 15  # Start very short

# Emotional variation
"curious": ~18 tokens
"peaceful": ~9 tokens  
"contemplative": ~12 tokens

# Bounds: 5-20 words maximum
```

## Expected Response Patterns

### Visual Layer (1 sentence)
```
"Wall ahead with circular patterns."
"Dim lamp light, shadows moving."
"Familiar room around me."
```

### Language Layer (5-15 words)
```
"Patterns feel calming tonight."
"..."
"Still here, nothing new."
"Mind drifting somewhere else."
"Quiet moment."
```

## Speed Improvements

1. **Faster Generation** - Fewer tokens = faster completion
2. **Lower Timeout** - 30s instead of 120s for text model
3. **Smaller Context** - 1024 tokens instead of 2048
4. **Early Stopping** - Stop tokens prevent continuation

## Natural Patterns Encouraged

### High Energy States
- "Something's different here."
- "Interesting patterns today."

### Low Energy States  
- "..."
- "Still."
- "Mmm."

### Transitional States
- "Shifting focus now."
- "Mind wandering."

### Contemplative States
- "Wonder what it means."
- "Feels familiar somehow."

## Testing Recommendations

Run the system and monitor:
1. **Average word count** - Should be 5-15 words
2. **Silence frequency** - Should increase (that's good!)
3. **Generation speed** - Should be noticeably faster
4. **Natural flow** - Brief thoughts should feel more authentic

## Expected Metrics

| Metric | Before | After |
|--------|--------|-------|
| Avg words per response | 40-100 | 5-15 |
| Generation time | 10-20s | 3-8s |
| Silence rate | ~5% | ~20% |
| Verbose rejections | 0% | ~10% |

## Natural Silence is Good!

Remember: **Silence ("...") is a valid and valuable response**. Not every moment needs words. Sometimes consciousness is just being present without internal narration.

## Files Modified

- `personality.py`:
  - `_visual_consciousness()` - Ultra-brief prompt
  - `_language_subconscious()` - Ultra-brief prompt with length checks
  - `_query_text_model()` - Added strict token limits and stop tokens
  - `_query_ollama()` - Reduced num_predict and added stop tokens
  - `_cycle_emotional_state()` - Much shorter token targets (5-20)
  - `analyze_image()` - Accept silence markers as valid responses

## Quick Test

Expected output pattern:
```
[01:45:12] Wall patterns, dim light.
[01:45:19] ...
[01:45:26] Still here.
[01:45:33] Mind wandering.
[01:45:40] Familiar space.
```

Much better than:
```
[01:45:12] As you look around the room, you notice various items on the wall 
including circular patterns in muted tones. The lighting appears subdued, 
creating an atmosphere of quiet contemplation. You might find yourself wondering 
about the symbolic meaning behind these decorative choices...
```
