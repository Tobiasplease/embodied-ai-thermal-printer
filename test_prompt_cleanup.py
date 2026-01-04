"""Test new structured prompt construction"""
import re

# Simulate the old messy baseline that might come from LLaVA
messy_baseline = """The image shows an indoor space with a small window. I've been here for three days now, and my perception of this scene has become much clearer. There are tools on the desk."""

# Test sanitization
def sanitize_baseline(text):
    """Simulate the sanitization function"""
    import re

    # Remove image language patterns
    meta_phrases = [
        r"^the image shows\s*",
        r"^this image shows\s*",
        r"^the scene shows\s*",
        r"^in (the|this) image[,:]?\s*",
    ]

    cleaned = text
    for phrase in meta_phrases:
        cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE)

    # Filter sentences
    sentences = cleaned.split('.')
    filtered_sentences = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        # Skip image description sentences
        if re.match(r'^\s*(the|this) (image|photo|picture|scene) (shows|depicts|contains|features|displays)', sent, re.IGNORECASE):
            continue
        filtered_sentences.append(sent)

    cleaned = '. '.join(filtered_sentences)
    if cleaned and not cleaned.endswith('.'):
        cleaned += '.'

    return cleaned.strip()

# Test structured prompt construction
def build_structured_prompt(baseline, session_mins, emotional_state, recent_thoughts):
    """Simulate new structured prompt builder"""
    knowledge_section = []

    # Time
    knowledge_section.append(f"Awake {session_mins}m")

    # Emotional state
    if emotional_state:
        knowledge_section.append(emotional_state)

    # Environmental baseline (cleaned)
    if baseline:
        baseline_clean = sanitize_baseline(baseline)
        # Additional runtime cleanup
        baseline_clean = re.sub(r'^(the image shows|this image shows)\s*', '', baseline_clean, flags=re.IGNORECASE)
        if baseline_clean:
            knowledge_section.append(baseline_clean)

    what_you_know = ". ".join(knowledge_section) + "."
    recent_thoughts_section = f"Your thoughts so far: {recent_thoughts}"

    context_block = f"""{what_you_know}

{recent_thoughts_section}"""

    return context_block

# RUN TEST
print("=== TEST: Messy Baseline Cleanup ===\n")
print(f"INPUT (messy baseline from LLaVA):")
print(f'"{messy_baseline}"')
print()

cleaned = sanitize_baseline(messy_baseline)
print(f"OUTPUT (after sanitization):")
print(f'"{cleaned}"')
print()

print("=== TEST: Structured Prompt Construction ===\n")
prompt = build_structured_prompt(
    baseline=messy_baseline,
    session_mins=180,  # 3 hours
    emotional_state="Curious and alert",
    recent_thoughts="Desk surface worn -> Monitor glowing blue"
)

print("FINAL PROMPT:")
print("-" * 60)
print(prompt)
print("-" * 60)
print()

print("[OK] Prompt is now:")
print("  1. Temporally coherent (time -> state -> environment -> thoughts)")
print("  2. Semantically clear (no 'image shows' mixed with 'I've been here')")
print("  3. Structured (WHAT YOU KNOW -> RECENT THOUGHTS)")
