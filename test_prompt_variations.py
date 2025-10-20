"""
Test different prompt variations to find what works best with SmolLM2
"""
import requests
import time

OLLAMA_URL = "http://localhost:11434"
MODEL = "smollm2:1.7b"

# Sample visual description (what vision model would output)
VISUAL_DESC = "A person with dark hair wearing a black hoodie sits at a desk. Behind them is a poster with circular patterns. A fish tank is visible on the left side of the room."

# Test different prompt structures
PROMPTS = {
    "1_roleplay_explicit": f"""You are a consciousness observing through a camera. This is what you see right now:

{VISUAL_DESC}

Your thought (first person, present tense):""",

    "2_roleplay_short": f"""You are experiencing this scene through a camera:

{VISUAL_DESC}

Your internal thought:""",

    "3_continuation": f"""I'm observing through my camera. {VISUAL_DESC}""",

    "4_embedded": f"""[I am a consciousness with a camera eye]

I see: {VISUAL_DESC}

I think:""",

    "5_direct": f"""{VISUAL_DESC}

My thought about this:""",

    "6_stream": f"""Through my camera lens: {VISUAL_DESC}

[continuing internal monologue]""",

    "7_character": f"""Character: A consciousness observing through a camera
Scene: {VISUAL_DESC}

My thought:""",

    "8_now": f"""Right now I'm seeing: {VISUAL_DESC}

And I'm thinking""",

    "9_simple": f"""{VISUAL_DESC}

I notice""",

    "10_perspective": f"""From my perspective through the camera:
{VISUAL_DESC}

My internal reaction:"""
}

def query_model(prompt):
    """Query SmolLM2 with a prompt"""
    try:
        data = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "num_predict": 50
            }
        }
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            return f"ERROR: {response.status_code}"
            
    except Exception as e:
        return f"ERROR: {e}"

def test_all_prompts():
    """Test all prompt variations"""
    print("\n" + "="*80)
    print("TESTING PROMPT VARIATIONS FOR SMOLLM2")
    print("="*80 + "\n")
    
    results = {}
    
    for name, prompt in PROMPTS.items():
        print(f"\n{'='*80}")
        print(f"TEST: {name}")
        print(f"{'='*80}")
        print(f"\nPROMPT:")
        print("-" * 80)
        print(prompt)
        print("-" * 80)
        
        print("\nQuerying model...")
        response = query_model(prompt)
        
        print("\nRESPONSE:")
        print("-" * 80)
        print(response)
        print("-" * 80)
        
        # Analyze response
        is_first_person = any(word in response.lower()[:50] for word in ['i ', "i'm", "i see", "i notice", "i think"])
        is_meta = any(phrase in response.lower() for phrase in ['the image', 'you are', 'your description', 'this describes', 'based on'])
        is_conversational = any(phrase in response.lower() for phrase in ['you provided', 'you described', 'according to'])
        
        score = 0
        if is_first_person: score += 3
        if not is_meta: score += 2
        if not is_conversational: score += 2
        
        analysis = []
        if is_first_person: analysis.append("✓ First person")
        else: analysis.append("✗ Not first person")
        if not is_meta: analysis.append("✓ Not meta")
        else: analysis.append("✗ Meta/analytical")
        if not is_conversational: analysis.append("✓ Not conversational")
        else: analysis.append("✗ Conversational")
        
        print(f"\nANALYSIS: {' | '.join(analysis)} | Score: {score}/7")
        
        results[name] = {
            'response': response,
            'score': score,
            'first_person': is_first_person,
            'not_meta': not is_meta,
            'not_conversational': not is_conversational
        }
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY - RANKED BY SCORE")
    print("="*80 + "\n")
    
    ranked = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)
    
    for i, (name, data) in enumerate(ranked, 1):
        print(f"{i}. {name:30s} Score: {data['score']}/7")
        print(f"   Response: {data['response'][:80]}{'...' if len(data['response']) > 80 else ''}")
        print()
    
    print("\n" + "="*80)
    print(f"BEST PERFORMER: {ranked[0][0]}")
    print("="*80)

if __name__ == "__main__":
    test_all_prompts()
