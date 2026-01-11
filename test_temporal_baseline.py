"""
Test temporal baseline awareness STATE MACHINE for person presence/absence.

This test simulates the exact prompt injection logic to show what the duck
would actually receive in all person presence state transitions.
"""

import time

class MockPersonalityAI:
    """Mock personality with just the temporal baseline state machine logic"""

    def __init__(self):
        self.environmental_baseline = ""
        self.environmental_baseline_created_at = None
        self.true_session_start = time.time()
        self.current_session_start = time.time()
        self.last_significant_change_time = time.time()

    def build_knowledge_section_with_baseline(self, env_baseline, baseline_age_minutes, person_count):
        """
        Simulate the exact logic from personality.py lines 1693-1761
        Returns what would be injected into the prompt's knowledge section
        """
        import re

        knowledge_section = []

        # Simulate session time (e.g., 45 minutes awake)
        session_time_mins = 45
        knowledge_section.append(f"Awake {session_time_mins}m")

        # Environmental baseline processing (EXACT logic from personality.py)
        env_context = env_baseline

        if env_context:
            # Clean up any "The image shows" prefix if it leaked through
            env_clean = env_context.strip()
            env_clean = re.sub(r'^(the image shows|this image shows)\s*', '', env_clean, flags=re.IGNORECASE)

            # TEMPORAL AWARENESS STATE MACHINE: Track person presence changes
            baseline_mentions_person = any(word in env_clean.lower() for word in
                ['person', 'people', 'someone', 'visitor', 'human', 'man', 'woman', 'he ', 'she '])

            # Estimate how many people baseline described
            baseline_person_count = 0
            env_lower = env_clean.lower()
            if 'two people' in env_lower or 'both' in env_lower or 'pair' in env_lower:
                baseline_person_count = 2
            elif 'three people' in env_lower or 'several' in env_lower or 'multiple' in env_lower:
                baseline_person_count = 3
            elif baseline_mentions_person:
                baseline_person_count = 1

            # Get current person count
            current_person_count = person_count if person_count is not None else 0

            # TEMPORAL FRAMING STATE MACHINE: Rich person presence awareness
            if current_person_count == 0 and baseline_mentions_person:
                # STATE: DEPARTED - People left, now alone
                if baseline_age_minutes < 5:
                    env_clean = f"What you saw {baseline_age_minutes}min ago: {env_clean}\nNOW: You are alone. They left."
                else:
                    env_clean = f"Earlier memory ({baseline_age_minutes}min ago): {env_clean}\nNOW: You're alone - no one here anymore."

            elif current_person_count > 0 and not baseline_mentions_person:
                # STATE: NEW ARRIVAL - Someone arrived (baseline was empty)
                if current_person_count == 1:
                    env_clean = f"{env_clean}\nNOW: Someone just arrived."
                else:
                    env_clean = f"{env_clean}\nNOW: {current_person_count} people just arrived."

            elif current_person_count > 0 and baseline_mentions_person and current_person_count == baseline_person_count:
                # STATE: STILL PRESENT - Same people still here
                if current_person_count == 1:
                    env_clean = f"{env_clean}\nStill here - watching you."
                else:
                    env_clean = f"{env_clean}\nAll {current_person_count} still here."

            elif current_person_count > baseline_person_count and baseline_person_count > 0:
                # STATE: MORE ARRIVED - Additional people joined
                new_count = current_person_count - baseline_person_count
                if new_count == 1:
                    env_clean = f"Earlier: {env_clean}\nNOW: Someone else arrived (now {current_person_count} total)."
                else:
                    env_clean = f"Earlier: {env_clean}\nNOW: {new_count} more arrived (now {current_person_count} total)."

            elif current_person_count < baseline_person_count and current_person_count > 0:
                # STATE: SOME LEFT - Fewer people now
                left_count = baseline_person_count - current_person_count
                if current_person_count == 1:
                    env_clean = f"Earlier: {env_clean}\nNOW: Only one person remaining."
                else:
                    env_clean = f"Earlier: {env_clean}\nNOW: {left_count} left - {current_person_count} remaining."

            elif baseline_age_minutes > 2:
                # STATE: NO CHANGE - Normal aging markers (no person presence changes)
                if baseline_age_minutes < 5:
                    env_clean = f"{env_clean} [just established]"
                elif baseline_age_minutes < 15:
                    env_clean = f"{env_clean} [established {baseline_age_minutes}min ago]"
                else:
                    # Very old baseline - emphasize duration
                    env_clean = f"Still in the same space. {env_clean} [established {baseline_age_minutes}min ago]"

            knowledge_section.append(env_clean)

        # Simulate recent thoughts
        recent_thoughts = "(recent thoughts): dark hallway... spiral staircase... quiet..."

        # Build final context block (what model sees)
        what_you_know = ". ".join(knowledge_section) + "."

        context_block = f"""{what_you_know}

{recent_thoughts}"""

        return context_block


def test_scenario(description, baseline, baseline_age_mins, person_count):
    """Run a test scenario and show the output"""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {description}")
    print(f"{'='*80}")
    print(f"Environmental Baseline: \"{baseline}\"")
    print(f"Baseline Age: {baseline_age_mins} minutes")
    print(f"Current Person Count: {person_count}")
    print(f"\n{'---'*25}")
    print("PROMPT INJECTION (what the model receives):")
    print(f"{'---'*25}\n")

    mock = MockPersonalityAI()
    result = mock.build_knowledge_section_with_baseline(baseline, baseline_age_mins, person_count)

    print(result)
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TEMPORAL BASELINE AWARENESS STATE MACHINE TEST")
    print("Testing all person presence state transitions")
    print("="*80)

    # STATE 1: DEPARTED - Person left
    test_scenario(
        description="STATE: DEPARTED - Person left (recent)",
        baseline="A room with a spiral staircase. A person is standing at the bottom.",
        baseline_age_mins=3,
        person_count=0
    )

    test_scenario(
        description="STATE: DEPARTED - Person left (old memory)",
        baseline="Dark hallway. Someone was examining the railing closely.",
        baseline_age_mins=7,
        person_count=0
    )

    # STATE 2: NEW ARRIVAL - Someone just arrived
    test_scenario(
        description="STATE: NEW ARRIVAL - One person arrived",
        baseline="A spiral staircase curves upward. Worn wooden steps. Dim lighting.",
        baseline_age_mins=4,
        person_count=1
    )

    test_scenario(
        description="STATE: NEW ARRIVAL - Multiple people arrived",
        baseline="Empty gallery space with artwork on walls.",
        baseline_age_mins=3,
        person_count=3
    )

    # STATE 3: STILL PRESENT - Same person/people still here
    test_scenario(
        description="STATE: STILL PRESENT - One person still here",
        baseline="Workshop. Someone working at a desk.",
        baseline_age_mins=3,
        person_count=1
    )

    test_scenario(
        description="STATE: STILL PRESENT - Multiple people still here",
        baseline="Gallery space. Two people examining the artwork on the walls.",
        baseline_age_mins=5,
        person_count=2
    )

    # STATE 4: MORE ARRIVED - Additional people joined
    test_scenario(
        description="STATE: MORE ARRIVED - One person was here, now two",
        baseline="Workshop. Someone working at a desk.",
        baseline_age_mins=4,
        person_count=2
    )

    test_scenario(
        description="STATE: MORE ARRIVED - Two were here, now five",
        baseline="Gallery space. Two people examining the artwork.",
        baseline_age_mins=3,
        person_count=5
    )

    # STATE 5: SOME LEFT - Fewer people now
    test_scenario(
        description="STATE: SOME LEFT - Two were here, now one remains",
        baseline="Gallery space. Two people examining the artwork on the walls.",
        baseline_age_mins=4,
        person_count=1
    )

    test_scenario(
        description="STATE: SOME LEFT - Three were here, now two remain",
        baseline="Workshop. Several people gathered around a table.",
        baseline_age_mins=5,
        person_count=2
    )

    # STATE 6: NO CHANGE - Normal aging (no person changes)
    test_scenario(
        description="STATE: NO CHANGE - Empty room, still empty",
        baseline="A spiral staircase curves upward. Worn wooden steps.",
        baseline_age_mins=4,
        person_count=0
    )

    test_scenario(
        description="STATE: NO CHANGE - Fresh baseline, no changes",
        baseline="Workshop with tools scattered around.",
        baseline_age_mins=1,
        person_count=0
    )

    print("\n" + "="*80)
    print("TEST COMPLETE - ALL STATES COVERED")
    print("="*80)
    print("\nSTATE TRANSITIONS:")
    print("1. DEPARTED: Person left → 'NOW: You are alone. They left.'")
    print("2. NEW ARRIVAL: Someone arrived → 'NOW: Someone just arrived.'")
    print("3. STILL PRESENT: Same people still here → 'Still here - watching you.'")
    print("4. MORE ARRIVED: Additional people → 'NOW: X more arrived (now Y total).'")
    print("5. SOME LEFT: Fewer people → 'NOW: X left - Y remaining.'")
    print("6. NO CHANGE: No person changes → Normal aging markers")
    print("="*80 + "\n")
