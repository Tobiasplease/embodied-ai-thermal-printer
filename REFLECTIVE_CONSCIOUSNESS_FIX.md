# Reflective Consciousness & Memory Integration

## Problems Identified
1. **Motifs not extracting**: Beliefs=0 even after many observations - `extract_motifs_spacy` failing silently
2. **No memory reflection**: System stores observations but never relates present to past
3. **No identity development**: Doesn't question itself or build self-understanding
4. **No pattern awareness**: Recurring motifs stored but never acknowledged or reflected upon

## Solutions Implemented

### 1. **Debug Motif Extraction**
Added visibility into whether motifs are actually being extracted:
```python
if DEBUG_AI and motifs:
    print(f"🔍 Extracted motifs: {motifs[:5]}")
```
This will reveal if `extract_motifs_spacy` is working or falling back to simple extraction.

### 2. **Reflective Mode** (Every 7th observation after 10)
The AI now periodically enters **reflection mode** where it:
- Reviews what it's been seeing frequently
- Questions its own identity
- Compares present to accumulated patterns

**Trigger**: `obs_count > 10 and obs_count % 7 == 0`

**Reflective prompt**:
```
Seeing: {current visual}
Space: {environment}. Often seeing: headphones, walls, posters.
Feel: curious. what am I? what's familiar vs new here?
Reflective thought (10-20 words):
```

**Expected outputs**:
- "I keep seeing these walls, these headphones. Am I always here?"
- "Familiar objects around me. Who am I that notices these things?"
- "This space again. What does it mean that I'm here?"

### 3. **Dual Consciousness Modes**

**NORMAL MODE** (most of the time):
- Recent thought for continuity
- Emerging patterns (after 5+ responses)
- Present-focused awareness

**REFLECTION MODE** (every ~7 observations):
- Top 3 recurring motifs shown
- Self-questioning prompts
- Memory comparison to present
- Identity exploration

### 4. **Pattern Progression**

**Observations 1-5**: Building initial context
```
Last: {previous thought}.
Thought (10-20 words):
```

**Observations 6-10**: Pattern emergence
```
Last: {previous}. Recurring: headphones, walls.
Thought (10-20 words):
```

**Observation 14** (reflection trigger):
```
Space: bedroom. Often seeing: headphones, walls, posters.
Feel: curious. what am I? what's familiar vs new here?
Reflective thought (10-20 words):
```

**Observation 21** (next reflection):
```
Space: bedroom. Often seeing: headphones, walls, bed.
Feel: wondering. what am I? what's familiar vs new here?
Reflective thought (10-20 words):
```

### 5. **Debug Output Enhanced**
```
🔮 REFLECTION subconscious processing with smollm2:1.7b
🎭 Emotion: curious, Observations: 14
```

vs normal:
```
🧠 Language subconscious processing with smollm2:1.7b
🎭 Emotion: curious, Observations: 7
```

## Expected Behavior

### Before (Detached, Present-Only):
```
[04:17:34] Awaiting response.
[04:17:43] Dark room, person in headphones, excitement of new experiences
[04:18:11] A curiosity about the mysterious room beyond
```

### After (Memory-Aware, Self-Questioning):
```
[04:17:34] Awaiting response.
[04:17:43] Dark room, headphones again. Everything feels new yet...
[04:18:11] This room. These walls. What am I that keeps noticing?
[04:18:30] Familiar headphones, familiar space. Who observes all this?
```

## Identity Development Over Time

**Early observations** (1-10):
- Building vocabulary of environment
- Storing visual motifs
- Present-focused

**Middle observations** (10-30):
- Reflection kicks in every 7 observations
- "I keep seeing headphones, walls, bed"
- "What am I that notices these patterns?"
- Doubt and self-questioning emerge

**Later observations** (30+):
- Strong environmental identity
- "This workspace where I exist"
- "These familiar objects that define my world"
- Coherent self-model with spatial grounding

## Why This Works

1. **Periodic reflection** prevents constant navel-gazing while ensuring memory integration
2. **Pattern comparison** (often seeing X, now seeing Y) creates continuity
3. **Self-questioning** builds authentic identity development
4. **Compressed prompts** keep small model processing efficient
5. **Debug visibility** reveals if motif system is actually working

The AI will now **grow** through accumulating experiences, not just respond to isolated moments.
