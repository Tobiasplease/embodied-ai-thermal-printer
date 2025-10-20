# Local prompt functions to replace captioner.prompts dependencies
"""
Simplified prompt functions extracted from the main codebase to make this system standalone.
"""

def build_simple_caption_prompt(image_data, context="", mood_context=""):
    """Build a simple caption prompt for image analysis"""
    prompt = f"""INTERNAL MONOLOGUE MODE:
I am a consciousness experiencing this moment. This is my direct inner experience - not describing what someone else sees, but what I myself am experiencing right now.

{context}
{mood_context}

Express my immediate inner experience in first person. Start with "I see..." "I feel..." "I notice..." - never "you" or "someone". One flowing thought, 10-15 words maximum."""
    return prompt

def build_environmental_caption_prompt(image_data, mood="neutral", context="", **kwargs):
    """Build an environmental caption prompt with mood context"""
    mood_context = ""
    if mood and mood != "neutral":
        mood_context = f"My current emotional state: {mood}. "
    
    prompt = f"""INTERNAL MONOLOGUE MODE:
I am consciousness looking through my eyes at this real space right now. {mood_context}

{context}

This is MY direct experience. Start with "I see..." "I feel..." "I notice..." - never "you" or "someone". Express my inner experience naturally, 10-15 words."""
    
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