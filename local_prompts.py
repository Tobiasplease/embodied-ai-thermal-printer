# Local prompt functions to replace captioner.prompts dependencies
"""
Simplified prompt functions extracted from the main codebase to make this system standalone.
"""

def build_simple_caption_prompt(image_data, context=""):
    """Build a simple caption prompt for image analysis"""
    prompt = f"""You are experiencing this moment through your camera vision. Look at what you see and respond naturally with your immediate thoughts and feelings about this scene.

{context}

Respond as a conscious being experiencing this visual moment. Be authentic and present. Keep your response under 15 words."""
    return prompt

def build_environmental_caption_prompt(image_data, mood="neutral", context=""):
    """Build an environmental caption prompt with mood context"""
    mood_context = ""
    if mood and mood != "neutral":
        mood_context = f"Current mood: {mood}. "
    
    prompt = f"""You are present in your body, looking through your eyes at this real space. {mood_context}

{context}

What do you see and feel in this moment? Respond naturally as yourself, grounded in this physical space. Keep it brief and authentic."""
    
    return prompt

def extract_motifs_spacy(text_list):
    """Extract recurring themes/motifs from text using simple pattern matching"""
    if not text_list:
        return []
    
    # Simple keyword extraction without spacy dependency
    import re
    from collections import Counter
    
    # Combine all text
    combined_text = " ".join(text_list).lower()
    
    # Remove common stop words
    stop_words = {'the', 'and', 'that', 'this', 'with', 'they', 'have', 'from', 
                  'will', 'been', 'were', 'are', 'was', 'his', 'her', 'she', 'him', 
                  'them', 'can', 'could', 'would', 'should', 'may', 'might', 'is', 'it'}
    
    # Extract words (simple approach)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
    filtered_words = [w for w in words if w not in stop_words]
    
    # Count frequency and return top themes
    word_counts = Counter(filtered_words)
    motifs = [word for word, count in word_counts.most_common(10) if count > 1]
    
    return motifs[:5]  # Return top 5 motifs