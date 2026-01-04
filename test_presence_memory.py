"""Test presence memory system to prevent person rediscovery spam"""
import time
from focus_system import FocusEngine

def test_presence_memory():
    """Test that presence memory prevents rediscovery after max observations"""

    engine = FocusEngine()

    print("=== Test 1: New arrival resets memory ===")
    print(f"Initial state: presence_id={engine.current_presence_id}, observations={len(engine.current_presence_observations)}")

    # Simulate person arrival
    person_events = ['someone_arrived']
    novelty = engine._calculate_visual_novelty([], person_events, None)
    print(f"Person arrived: novelty={novelty}, presence_id={engine.current_presence_id}, observations={len(engine.current_presence_observations)}")
    assert novelty == 1.0, "Arrival should have max novelty"
    assert engine.current_presence_id == 1, "Presence ID should increment"
    assert len(engine.current_presence_observations) == 0, "Observations should reset"

    print("\n=== Test 2: Three observations allowed ===")
    for i in range(3):
        # Simulate PERSON mode observation
        state = {
            'novelty': 0.95,
            'temporal': {'static_duration': 0},
            'consciousness_readiness': {'philosophical': 0}
        }
        focus_mode, context = engine._focus_person(state, f"observation_{i+1}")
        print(f"Observation {i+1}: {len(engine.current_presence_observations)} recorded")
        assert len(engine.current_presence_observations) == i + 1

    print(f"\nAfter 3 observations: {len(engine.current_presence_observations)} total")
    assert len(engine.current_presence_observations) == 3, "Should have 3 observations"

    print("\n=== Test 3: Fourth observation should be blocked ===")
    # Check if limit reached
    observation_limit_reached = len(engine.current_presence_observations) >= engine.max_observations_per_presence
    print(f"Limit reached? {observation_limit_reached}")
    assert observation_limit_reached == True, "Limit should be reached after 3 observations"

    print("\n=== Test 4: Departure clears memory ===")
    person_events = ['now_alone']
    novelty = engine._calculate_visual_novelty([], person_events, None)
    print(f"Person left: novelty={novelty}, observations={len(engine.current_presence_observations)}")
    assert novelty == 1.0, "Departure should have max novelty"
    assert len(engine.current_presence_observations) == 0, "Observations should clear on departure"

    print("\n=== Test 5: New arrival creates new presence ID ===")
    person_events = ['someone_arrived']
    novelty = engine._calculate_visual_novelty([], person_events, None)
    print(f"New person arrived: presence_id={engine.current_presence_id}, observations={len(engine.current_presence_observations)}")
    assert engine.current_presence_id == 2, "Presence ID should increment to 2"
    assert len(engine.current_presence_observations) == 0, "Observations should be fresh"

    print("\n[OK] ALL TESTS PASSED")
    print(f"\nFinal state:")
    print(f"  - Presence ID: #{engine.current_presence_id}")
    print(f"  - Observations this presence: {len(engine.current_presence_observations)}")
    print(f"  - Cooldown: {engine.person_cooldown}s (was 120s)")
    print(f"  - Max observations per presence: {engine.max_observations_per_presence}")

if __name__ == "__main__":
    test_presence_memory()
