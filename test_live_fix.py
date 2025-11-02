"""
Quick test to verify the psychological integration works in live scenario
"""

from personality import PersonalityAI

def test_live_scenario():
    print("=" * 80)
    print("TESTING LIVE PSYCHOLOGICAL INTEGRATION FIX")
    print("=" * 80)
    
    # Create AI (simulates main.py initialization)
    ai = PersonalityAI()
    
    # Add some psychological state
    ai.memory_ref.self_model['desires'] = ['to understand', 'to connect']
    ai.memory_ref.self_model['doubts'] = ['why am I here?']
    ai.memory_ref.self_model['identity_fragments'] = ['a small duck']
    
    print("\n1. Testing FIRST observation (recent_responses empty)...")
    print(f"   recent_responses length: {len(ai.recent_responses)}")
    
    # Simulate calling _build_psychological_context with empty responses
    try:
        psych_ctx = ai._build_psychological_context()
        print(f"   ✅ Psychological context built successfully:")
        print(f"   {psych_ctx.strip()}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    print("\n2. Testing CONTINUING consciousness (recent_responses populated)...")
    ai.recent_responses = ['I see light', 'I notice movement', 'Something is here']
    print(f"   recent_responses length: {len(ai.recent_responses)}")
    
    try:
        psych_ctx = ai._build_psychological_context()
        print(f"   ✅ Psychological context built successfully:")
        print(f"   {psych_ctx.strip()}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    print("\n3. Testing focus contexts with psychological state...")
    
    # EMOTIONAL focus
    try:
        emotional_ctx = ai._build_focus_context("EMOTIONAL")
        print(f"   EMOTIONAL: {emotional_ctx}")
        assert "wanting:" in emotional_ctx, "Should inject desires in EMOTIONAL mode"
        print(f"   ✅ Desires injected correctly")
    except Exception as e:
        print(f"   ❌ EMOTIONAL ERROR: {e}")
        return False
    
    # PHILOSOPHICAL focus (with doubts)
    try:
        phil_ctx = ai._build_focus_context("PHILOSOPHICAL")
        print(f"   PHILOSOPHICAL: {phil_ctx}")
        print(f"   ✅ Built correctly")
    except Exception as e:
        print(f"   ❌ PHILOSOPHICAL ERROR: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Fix is working!")
    print("=" * 80)
    print("\nThe system should now run without the:")
    print("  'cannot access local variable psychological_context' error")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_live_scenario()
    exit(0 if success else 1)
