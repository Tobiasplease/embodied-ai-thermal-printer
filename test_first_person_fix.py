"""
Test script to demonstrate the first-person perspective fix
"""

# Test phrases that should be caught by the filters
test_responses = [
    "I see a person sitting on a bed in what appears to be their bedroom",  # Third-person
    "As you look around the room, you notice various items",  # Conversational
    "In this image, there is a wall with circular designs",  # Analytical
    "I'm sitting here thinking about the patterns around me",  # Good - first person
    "The room feels quiet. Shadows move across the wall.",  # Good - first person
    "Consider exploring the furniture to find clues",  # Conversational instruction
    "Dim light from the lamp casts interesting shadows",  # Good - first person
]

from personality import PersonalityAI

# Create instance
ai = PersonalityAI()

print("=" * 70)
print("FIRST-PERSON PERSPECTIVE FILTER TEST")
print("=" * 70)

for i, response in enumerate(test_responses, 1):
    print(f"\n{i}. Testing: '{response[:60]}...'")
    
    # Test perspective break
    is_broken = ai._check_perspective_break(response)
    print(f"   Perspective break: {'❌ YES' if is_broken else '✅ NO'}")
    
    # Test conversational filter
    filtered = ai._filter_conversational_language(response)
    if filtered is None:
        print(f"   Conversational filter: ❌ REJECTED")
    elif filtered != response:
        print(f"   Conversational filter: ⚠️  MODIFIED")
        print(f"   → '{filtered[:60]}...'")
    else:
        print(f"   Conversational filter: ✅ PASSED")

print("\n" + "=" * 70)
print("EXPECTED RESULTS:")
print("=" * 70)
print("Responses 1, 2, 3, 6 should be rejected (third-person or conversational)")
print("Responses 4, 5, 7 should pass (authentic first-person)")
