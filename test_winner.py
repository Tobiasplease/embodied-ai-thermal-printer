"""
Test the WINNER prompt variation
"""
import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "smollm2:1.7b"

VISUAL_DESC = "A person with dark hair wearing a black hoodie sits at a desk. Behind them is a poster with circular patterns. A fish tank is visible on the left side of the room."

# THE WINNER from quick test
PROMPT = f"""You are experiencing this scene through a camera:

{VISUAL_DESC}

Your internal thought:"""

def query_model(prompt, temp=0.8):
    try:
        data = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temp,
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
print("TESTING WINNER: 'You are experiencing this scene through a camera'")
print("="*80 + "\n")

# Test 3 times to see consistency
for i in range(3):
    print(f"\nTEST RUN #{i+1}:")
    print("-" * 80)
    response = query_model(PROMPT)
    print(response)
    
    # Analysis
    first_50 = response.lower()[:80]
    is_first = any(word in first_50 for word in ['i ', "i'm", "i see", "i notice", "i think", "i observe", "i am"])
    is_meta = any(phrase in response.lower() for phrase in ['the image', 'you are describing', 'your description', 'as an ai', 'i cannot', 'chatbot', 'you provided'])
    
    print(f"\n{'✅' if is_first and not is_meta else '❌'} First-person: {is_first} | Not meta: {not is_meta}")
    print()

print("\n" + "="*80)
print("RECOMMENDED PROMPT FOR personality.py:")
print("="*80)
print('''
prompt = f"""You are experiencing this scene through a camera:

{visual_description}

{temporal_note}

Your internal thought:"""
''')
