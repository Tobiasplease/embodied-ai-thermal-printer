"""
PROTOTYPE: Perception → Memory → Consciousness Architecture

Key changes:
1. Vision model extracts FACTS (objects, scene, atmosphere)
2. Memory layer COMPRESSES facts into known world state
3. Language model generates THOUGHTS about known world
"""

def _visual_perception(self, image_path):
    """MiniCPM-V: Extract scene facts - not consciousness"""
    
    prompt = f"""Analyze this image and extract key information:

1. Main objects/items visible
2. People (if any) and what they're doing
3. Spatial setting (room type, layout)
4. Lighting/atmosphere
5. Any notable changes or movements

Be factual and specific. List format is fine.

Analysis:"""
    
    # Get factual analysis from vision model
    response = self._query_ollama(prompt, image_path)
    
    return self._parse_visual_facts(response)


def _parse_visual_facts(self, vision_response):
    """Extract structured data from vision model response"""
    
    # Simple parsing - can be improved
    facts = {
        "objects": [],
        "people": None,
        "setting": None,
        "atmosphere": None,
        "raw": vision_response
    }
    
    # Extract objects mentioned
    import re
    common_objects = ['headphones', 'monitor', 'desk', 'chair', 'bed', 'wall', 
                     'poster', 'laptop', 'keyboard', 'mouse', 'cup', 'bottle']
    
    for obj in common_objects:
        if obj in vision_response.lower():
            facts["objects"].append(obj)
    
    # Extract people references
    people_indicators = ['person', 'man', 'woman', 'someone', 'individual']
    for indicator in people_indicators:
        if indicator in vision_response.lower():
            # Extract activity if mentioned
            if 'sitting' in vision_response.lower():
                facts["people"] = "person sitting"
            elif 'standing' in vision_response.lower():
                facts["people"] = "person standing"
            else:
                facts["people"] = "person present"
            break
    
    # Extract atmosphere
    if 'dim' in vision_response.lower() or 'dark' in vision_response.lower():
        facts["atmosphere"] = "dim"
    elif 'bright' in vision_response.lower():
        facts["atmosphere"] = "bright"
    
    return facts


def _update_perceptual_memory(self, visual_facts):
    """Build world model from accumulated visual facts"""
    
    if not hasattr(self, '_world_model'):
        self._world_model = {
            "object_frequency": {},
            "scene_type": None,
            "scene_stability_count": 0,
            "people_state": None,
            "last_facts": None
        }
    
    # Track object frequencies
    for obj in visual_facts["objects"]:
        self._world_model["object_frequency"][obj] = \
            self._world_model["object_frequency"].get(obj, 0) + 1
    
    # Detect scene stability (is anything changing?)
    if self._world_model["last_facts"]:
        # Compare with last observation
        obj_overlap = len(set(visual_facts["objects"]) & 
                         set(self._world_model["last_facts"]["objects"]))
        
        if obj_overlap > len(visual_facts["objects"]) * 0.7:  # 70% same
            self._world_model["scene_stability_count"] += 1
        else:
            self._world_model["scene_stability_count"] = 0
    
    self._world_model["last_facts"] = visual_facts
    self._world_model["people_state"] = visual_facts["people"]
    
    return self._world_model


def _compress_world_model(self):
    """Compress world model into language model prompt context"""
    
    if not hasattr(self, '_world_model'):
        return "observing surroundings"
    
    wm = self._world_model
    parts = []
    
    # Most frequent objects (top 3)
    if wm["object_frequency"]:
        frequent = sorted(wm["object_frequency"].items(), 
                         key=lambda x: x[1], reverse=True)[:3]
        obj_list = [f"{obj} (seen {count}x)" for obj, count in frequent]
        parts.append(", ".join(obj_list))
    
    # People state
    if wm["people_state"]:
        parts.append(wm["people_state"])
    
    # Scene stability indicator
    if wm["scene_stability_count"] > 3:
        duration = wm["scene_stability_count"] * 7  # 7s intervals
        if duration > 60:
            parts.append(f"static {duration//60}min")
        else:
            parts.append(f"static {duration}s")
    
    return " | ".join(parts) if parts else "new scene"


def _consciousness_stream(self, world_context):
    """SmolLM2: Generate thought based on compressed world state"""
    
    # Get emotional state (from recursive self-analysis)
    emotion = self.current_emotion
    
    # Simple, clear prompt
    prompt = f"""Known world: {world_context}

My inner thoughts, feeling {emotion}:"""
    
    # Generate thought
    response = self._query_text_model(prompt, SUBCONSCIOUS_MODEL)
    
    return response


def analyze_image(self, image_path):
    """MAIN FLOW: Perception → Memory → Consciousness"""
    
    try:
        # STEP 1: Visual Perception (MiniCPM-V extracts facts)
        visual_facts = self._visual_perception(image_path)
        
        # STEP 2: Update World Model (Python compresses facts)
        self._update_perceptual_memory(visual_facts)
        
        # STEP 3: Compress for language model
        world_context = self._compress_world_model()
        
        if DEBUG_AI:
            print(f"🌍 World: {world_context}")
        
        # STEP 4: Consciousness Stream (SmolLM2 generates thought)
        thought = self._consciousness_stream(world_context)
        
        # STEP 5: Recursive self-analysis (updates emotion for next cycle)
        if thought:
            self._update_mood_from_response(thought)
            self.recent_responses.append(thought)
        
        return thought
        
    except Exception as e:
        print(f"Error: {e}")
        return None


# Example flow:
# 
# 1. Vision sees: "Person with headphones, monitor, desk, dim lighting"
# 2. Memory tracks: headphones (8x), monitor (8x), person sitting, static 2min
# 3. Compression: "headphones (seen 8x), monitor (seen 8x), person sitting | static 2min"
# 4. Language prompt: "Known world: headphones (seen 8x), monitor (seen 8x), person sitting | static 2min\n\nMy inner thoughts, feeling bored:"
# 5. Language output: "Two minutes of the same view. Headphones, always headphones. Nothing changes."
# 6. Self-analysis: Detects "same", "always", "nothing changes" → emotion = "frustrated"
# 7. Next cycle uses "frustrated" emotion
