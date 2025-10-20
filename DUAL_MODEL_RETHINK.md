# Dual Model Architecture Rethink

## Current Problem
- MiniCPM-V (8B) is stronger than SmolLM2 (1.7B)
- Vision model output quality > Language model output quality
- Sequential architecture wastes vision model's capabilities
- Language model gets confused trying to understand AND respond

## Core Insight: COMPLEMENTARY not SEQUENTIAL

### Architecture Option A: SENSORY vs REFLECTIVE
```
MiniCPM-V → Rich sensory perception (visual consciousness)
SmolLM2   → Compressed emotional reaction (affective layer)
Output    → Merged: "I see [perception] ... [emotional response]"
```

**Example Flow:**
- Vision: "Person with headphones sits at glowing monitor in dim room, ambient light from screen, papers scattered on desk"
- Language: "lonely" / "focused" / "trapped"
- Output: "Headphones glow blue in the dark. Feel so isolated here."

**Pros:**
- Leverages vision model's strength (rich description)
- Language model only does emotion (what it's trained for in roleplay)
- Natural merger creates consciousness

**Cons:**
- Requires smart merging logic
- Language model still needs to understand visual input


### Architecture Option B: OBJECTIVE vs SUBJECTIVE SPLIT
```
MiniCPM-V → Pure facts, no interpretation (sensory data)
SmolLM2   → Subjective meaning-making (consciousness)
Output    → SmolLM2 output only (vision is just input)
```

**Example Flow:**
- Vision: "headphones, person, monitor, dim lighting, desk, papers"
- Language prompt: "Scene contains: headphones, person, monitor, dim lighting. My thoughts:"
- Language: "Same person. Always headphones. Do they ever leave?"
- Output: "Same person. Always headphones. Do they ever leave?"

**Pros:**
- Clearest separation of concerns
- Vision provides structured data, not prose
- Language model has full creative control
- No perspective confusion

**Cons:**
- Loses vision model's natural language strength
- Requires keyword extraction/parsing


### Architecture Option C: DUAL-SPEED CONSCIOUSNESS
```
MiniCPM-V → Slow, deep world-model (30s intervals)
SmolLM2   → Fast thought stream (7s intervals)
Output    → SmolLM2 with vision context in background
```

**Example Flow:**
- Every 30s - Vision builds world model: "Environment: bedroom, objects: headphones(recurring), person(constant), lighting(dim)"
- Every 7s - Language: "Still here. What time is it?" (informed by world model)
- Output: Fast thoughts with slow perceptual grounding

**Pros:**
- Natural cognitive separation (System 1 vs System 2)
- Vision model not overworked
- Language model focuses on rapid thought generation

**Cons:**
- Complex state management
- Vision updates might be stale


### Architecture Option D: VISION AS WORKING MEMORY
```
MiniCPM-V → Builds and maintains "what I know" (episodic memory)
SmolLM2   → Generates thoughts from memory state (consciousness)
Output    → Consciousness stream grounded in visual memory
```

**Example Flow:**
- Vision accumulates: "Known: bedroom with headphones, person at desk, recurring pattern for 2min"
- Language receives compressed memory: "bedroom, headphones (seen 5x), person, 2min elapsed"
- Language: "Two minutes. Same view. Starting to feel trapped."
- Output: Memory-informed consciousness

**Pros:**
- Most cognitively realistic
- Vision builds stable world-model
- Language generates authentic thoughts about known world
- Reduces confusion

**Cons:**
- Requires sophisticated memory compression
- Most complex to implement


## Recommendation: **Option B with D elements**

### Proposed Architecture: PERCEPTION → MEMORY → CONSCIOUSNESS

**Phase 1: Visual Perception (MiniCPM-V)**
- Extract: Objects, people, spatial relationships, lighting, atmosphere
- Format: Structured keywords + brief context
- Output: `{"objects": ["headphones", "monitor"], "people": "person at desk", "mood": "dim, isolated", "stability": "static 2min"}`

**Phase 2: Memory Update (Python logic)**
- Track recurring objects → patterns
- Track scene duration → boredom/engagement
- Compress to prompt context: "bedroom, headphones (recurring), person (constant), 2min static"

**Phase 3: Consciousness Stream (SmolLM2)**
- Receives compressed memory state
- Generates authentic first-person thought
- Informed by patterns but not overwhelmed by detail

**Example:**
```python
# Vision output (structured)
visual_data = {
    "objects": ["headphones", "person", "monitor", "desk"],
    "atmosphere": "dim lighting, quiet",
    "change_level": "static"
}

# Memory compression
memory_context = "bedroom, headphones (seen 8x), dim, static 3min"

# Language prompt
prompt = f"I'm in: {memory_context}\n\nMy thoughts, feeling {emotion}:"

# Language output
"Three minutes. Headphones again. Does anything else exist?"
```

### Implementation Strategy

1. **Simplify vision model task:**
   - Remove first-person perspective requirement
   - Focus on accurate object/scene detection
   - Output: Clean structured data

2. **Add memory compression layer:**
   - Track object frequency
   - Track scene duration
   - Build compressed "known world" state

3. **Refocus language model:**
   - Input: Compressed memory state (not full descriptions)
   - Task: Generate authentic thought FROM that state
   - Output: Pure consciousness stream

4. **Let vision model's strength shine:**
   - It's GOOD at understanding scenes
   - Don't force it into awkward first-person
   - Use its perceptual accuracy to build reliable world-model

5. **Let language model do what it does best:**
   - Roleplay/narrative generation (its training)
   - Emotional expression
   - First-person perspective
   - Brief, authentic thoughts


## Next Steps

1. Refactor `_visual_consciousness()` to return structured data
2. Create `_compress_visual_memory()` function
3. Update `_language_subconscious()` to work with compressed memory
4. Test with simple scenes
5. Iterate on compression strategy

This separates **perception** (vision model's strength) from **consciousness** (language model's job), with **memory** as the intelligent interface between them.
