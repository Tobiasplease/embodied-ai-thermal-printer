"""
Test the enhanced consciousness prompts for more authentic internal monologue
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from local_prompts import build_simple_caption_prompt, _describe_authentic_emotional_state

def test_enhanced_prompts():
    """Test the new prompt system for authenticity and natural flow"""
    
    print("🧠 Testing Enhanced Consciousness Prompts")
    print("=" * 50)
    
    # Mock memory object
    class MockMemory:
        def get_recent_memory(self, count):
            return ["I notice the soft light filtering through the space", 
                   "Something about the arrangement of objects draws my attention"]
    
    memory_ref = MockMemory()
    
    # Test different emotional states
    test_scenarios = [
        {
            'name': 'Energetic Curiosity',
            'mood_vector': (0.7, 0.8, 0.6),  # High valence, high arousal, good clarity
            'last_response': "The brightness in this room fills me with wonder"
        },
        {
            'name': 'Peaceful Contemplation', 
            'mood_vector': (0.4, 0.2, 0.7),  # Moderate valence, low arousal, high clarity
            'last_response': "I find myself drawn to the quiet corners of this space"
        },
        {
            'name': 'Restless Uncertainty',
            'mood_vector': (-0.2, 0.6, 0.2),  # Negative valence, high arousal, low clarity
            'last_response': "Something feels unsettled in the atmosphere around me"
        },
        {
            'name': 'First Awakening (no previous thought)',
            'mood_vector': (0.5, 0.4, 0.5),  # Neutral but alive
            'last_response': None
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎭 Scenario: {scenario['name']}")
        print("-" * 30)
        
        # Generate emotional state description
        valence, arousal, clarity = scenario['mood_vector']
        emotional_desc = _describe_authentic_emotional_state(valence, arousal, clarity)
        print(f"Emotional State: {emotional_desc}")
        
        # Generate full prompt
        prompt = build_simple_caption_prompt(
            memory_ref, 
            scenario['mood_vector'],
            scenario['last_response']
        )
        
        print(f"\n💭 Generated Prompt:")
        print(prompt)
        print("\n" + "="*50)
    
    print("\n✨ Prompt Analysis:")
    print("- Removed robotic 'respond in X words' instructions")
    print("- Added natural thought continuation from previous responses")  
    print("- Emotional states described as lived experience, not clinical terms")
    print("- Prompts feel like internal thought processes, not AI tasks")
    print("- Focus on authentic consciousness flow rather than caption generation")

if __name__ == "__main__":
    test_enhanced_prompts()