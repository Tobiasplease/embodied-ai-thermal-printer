"""
Quick test to demonstrate brevity improvements
"""

# Example verbose responses that should now be prevented
verbose_examples = [
    ("As you look around the room, you notice various items on the wall including circular patterns...", "❌ TOO VERBOSE"),
    ("Patterns feel calming.", "✅ GOOD - Brief"),
    ("...", "✅ PERFECT - Natural silence"),
    ("I wonder about the symbolic meaning behind these decorative choices and what they might represent in terms of personal identity and aesthetic preferences.", "❌ TOO VERBOSE"),
    ("Mind wandering.", "✅ GOOD - Brief"),
    ("Still here.", "✅ GOOD - Brief"),
]

print("=" * 70)
print("BREVITY CHECK - Word Count Analysis")
print("=" * 70)

for response, assessment in verbose_examples:
    word_count = len(response.split())
    
    # Our target is 5-15 words, max 25
    if word_count <= 3:
        status = "✅ SILENCE"
        color = ""
    elif word_count <= 15:
        status = "✅ IDEAL"
        color = ""
    elif word_count <= 25:
        status = "⚠️  ACCEPTABLE"
        color = ""
    else:
        status = "❌ TOO LONG"
        color = ""
    
    print(f"\n{word_count:2d} words | {status} | {assessment}")
    print(f"   '{response[:60]}{'...' if len(response) > 60 else ''}'")

print("\n" + "=" * 70)
print("TARGET: 5-15 words (max 25)")
print("SILENCE: '...' or '.' or 'mmm' is encouraged")
print("=" * 70)
