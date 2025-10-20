"""
Quick test of top 5 prompt variations
"""
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "smollm2:1.7b"

VISUAL_DESC = "A person with dark hair wearing a black hoodie sits at a desk. Behind them is a poster with circular patterns. A fish tank is visible on the left side of the room."

PROMPTS = {
    "1_current": f"""You are a consciousness observing through a camera. This is what you see right now:

{VISUAL_DESC}

Your thought (first person, present tense):""",

    "2_shorter": f"""You are experiencing this scene through a camera:

{VISUAL_DESC}

Your internal thought:""",

    "3_direct_continuation": f"""I'm observing through my camera. {VISUAL_DESC}""",

    "4_embedded_brackets": f"""[I am a consciousness with a camera eye]

I see: {VISUAL_DESC}

I think:""",

    "5_simple_notice": f"""{VISUAL_DESC}

I notice"""
}

def query_model(prompt):
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
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=data, timeout=30)
        if response.status_code == 200:
            return response.json().get('response', '').strip()
        return f"ERROR: {response.status_code}"
    except Exception as e:
        return f"ERROR: {e}"

print("\n" + "="*80)
print("QUICK TEST - TOP 5 PROMPTS")
print("="*80 + "\n")

results = []

for name, prompt in PROMPTS.items():
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}\n")
    
    response = query_model(prompt)
    
    # Check first-person
    first_50 = response.lower()[:80]
    is_first = any(word in first_50 for word in ['i ', "i'm", "i see", "i notice", "i think", "i observe"])
    
    # Check for bad patterns
    is_meta = any(phrase in response.lower() for phrase in ['the image', 'you are', 'your description', 'as an ai', 'i cannot', 'chatbot'])
    
    score = 5 if is_first else 0
    score += 0 if is_meta else 2
    
    status = "✅" if score >= 5 else "❌"
    
    print(f"RESPONSE: {response}\n")
    print(f"{status} Score: {score}/7 | First-person: {is_first} | Not meta: {not is_meta}\n")
    
    results.append((name, score, response))

print("\n" + "="*80)
print("RANKING:")
print("="*80)
for name, score, response in sorted(results, key=lambda x: x[1], reverse=True):
    print(f"{score}/7 - {name}")
    print(f"      '{response[:60]}...'\n")
