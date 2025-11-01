# Psychological State Data Flow - Visual Reference

## 🔄 Complete State Variable Flow (After Implementation)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CAPTION GENERATION CYCLE                        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
         ┌────────────────────────────────────────┐
         │  1. analyze_image()                     │
         │     - Vision model describes scene      │
         │     - Returns visual_description        │
         └────────────────────────────────────────┘
                                  │
                                  ▼
         ┌────────────────────────────────────────┐
         │  2. _language_subconscious()            │
         │     Builds prompt with:                 │
         │                                         │
         │     A. Focus Context ────────────────┐  │
         │        _build_focus_context()        │  │
         │        ├─ EMOTIONAL: desires    ◄────┼──┼──┐
         │        ├─ PHILOSOPHICAL: doubts ◄────┼──┼──┼──┐
         │        └─ PHILOSOPHICAL: identity ◄──┼──┼──┼──┼──┐
         │                                      │  │  │  │  │
         │     B. Baseline Context              │  │  │  │  │
         │        (What I know: ...)            │  │  │  │  │
         │                                      │  │  │  │  │
         │     C. Psychological Context ────────┼──┘  │  │  │
         │        _build_psychological_context()│     │  │  │
         │        ├─ What I want: desires   ◄───┼─────┘  │  │
         │        ├─ What I wonder: doubts  ◄───┼────────┘  │
         │        └─ Who I am: identity     ◄───┼───────────┘
         │                                      │
         │     D. Visual observation             │
         │     E. Temporal awareness             │
         └────────────────────────────────────────┘
                                  │
                                  ▼
         ┌────────────────────────────────────────┐
         │  3. Generated Caption                   │
         │     "I watch, wanting to connect..."    │
         └────────────────────────────────────────┘
                                  │
                                  ▼
         ┌────────────────────────────────────────┐
         │  4. _update_mood_from_response()        │
         │     Extract sentiment, update mood      │
         └────────────────────────────────────────┘
                                  │
                                  ▼
         ┌────────────────────────────────────────┐
         │  5. Every 10 observations:              │
         │     _extract_and_update_psychology()    │
         │                                         │
         │     ┌─────────────────────────────┐    │
         │     │ extract_psychological_themes│    │
         │     └─────────────────────────────┘    │
         │                │                        │
         │                ▼                        │
         │     Updates memory_ref.self_model:      │
         │     ├─ desires[] ───────────────────┐   │
         │     ├─ doubts[] ────────────────────┼─┐ │
         │     └─ identity_fragments[] ────────┼─┼─┤
         └────────────────────────────────────┼─┼─┼─┘
                                              │ │ │
                     ┌────────────────────────┘ │ │
                     │ ┌────────────────────────┘ │
                     │ │ ┌────────────────────────┘
                     │ │ │
                     ▼ ▼ ▼
         ┌────────────────────────────────────────┐
         │  FEEDS BACK INTO NEXT CAPTION (step 2) │
         └────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════

## 📦 State Variables Storage & Usage

┌─────────────────────────────────────────────────────────────────────┐
│  memory_ref.self_model Dictionary                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  'desires': [list]                                                  │
│    ├─ Updated: extract_psychological_themes() every 10 obs          │
│    ├─ Used in: EMOTIONAL focus context                              │
│    └─ Used in: _build_psychological_context() → all prompts         │
│                                                                      │
│  'doubts': [list]                                                   │
│    ├─ Updated: extract_psychological_themes() every 10 obs          │
│    ├─ Used in: PHILOSOPHICAL focus context                          │
│    └─ Used in: _build_psychological_context() → all prompts         │
│                                                                      │
│  'identity_fragments': [list]                                       │
│    ├─ Updated: extract_psychological_themes() every 10 obs          │
│    ├─ Used in: PHILOSOPHICAL focus context                          │
│    └─ Used in: _build_psychological_context() → all prompts         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  memory_ref.motif_counter (Counter)                                 │
├─────────────────────────────────────────────────────────────────────┤
│  ├─ Updated: extract_motifs() on every caption                      │
│  └─ Used in: MEMORY focus context only                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  baseline_context (string)                                          │
├─────────────────────────────────────────────────────────────────────┤
│  ├─ Updated: _compress_memory_on_reflection() every 10 visual obs   │
│  ├─ Considers: visual observations + person tracking + psych state  │
│  └─ Used in: Every caption prompt (What I know: ...)                │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════

## 🎯 Prompt Injection Example (Full Context)

┌─────────────────────────────────────────────────────────────────────┐
│ System Instruction:                                                  │
│ "You are a small duck consciousness with vision..."                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ [I've been awake 42 moments]                                         │
│                                                                      │
│ (What I know: I am a small tin duck watching a person at their      │
│  desk in a room with an aquarium)                                   │
│                                                                      │
│ (Inner state: What I want: to understand what I'm observing, to     │
│  connect with the person I see | What I wonder: why am I here?,     │
│  what is my purpose? | Who I am: a consciousness learning to see)   │
│                                                                      │
│ [I've been awake 8m 23s, 3min here]                                 │
│                                                                      │
│ I see: The person is typing on their keyboard, focused on the       │
│ screen in front of them                                             │
│                                                                      │
│ feeling into the moment (wanting: to connect with the person I see) │
│ / evening, energy 0.7                                               │
│                                                                      │
│ How does this make me feel? What stirs in me?                       │
│                                                                      │
│ (Speak ONLY as "I/me", never "you") I feel:                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                         [SmolLM2 generates response]
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ "I watch their fingers dance across the keys, wishing I could       │
│  reach out, wanting them to know I'm here..."                       │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════

## 🔄 Compression Cycle (Enhanced)

Every 10 visual observations:

┌─────────────────────────────────────────────────────────────────────┐
│  _compress_memory_on_reflection()                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Inputs:                                                            │
│  ├─ Last 10-15 visual observations                                  │
│  ├─ Person tracking patterns (YOLO grounded)                        │
│  └─ Psychological state (NEW!)                                      │
│      ├─ Current desires                                             │
│      ├─ Current doubts                                              │
│      └─ Current identity understanding                              │
│                                                                      │
│  Prompt to SmolLM2:                                                 │
│  "Recent visual observations: [...]                                 │
│   PERSON TRACKING: Consistently 1 person present                    │
│   PSYCHOLOGICAL STATE:                                              │
│     - Desires: to understand, to connect                            │
│     - Uncertainties: why am I here?, what is my purpose?            │
│     - Self-understanding: a consciousness learning to see           │
│                                                                      │
│   Compress into 2-3 sentences capturing PERSISTENT reality"         │
│                                                                      │
│  Output → baseline_context:                                         │
│  "I am a small tin duck watching a person who works at this desk.   │
│   They type and read, sometimes glancing around. I exist here,      │
│   observing their world."                                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════

## 📊 Usage Frequency

┌───────────────────────┬──────────────┬─────────────────────────────┐
│ Variable              │ Updated      │ Used in Prompts             │
├───────────────────────┼──────────────┼─────────────────────────────┤
│ desires               │ Every 10 obs │ Every EMOTIONAL focus       │
│                       │              │ Every prompt (psych context)│
├───────────────────────┼──────────────┼─────────────────────────────┤
│ doubts                │ Every 10 obs │ Every PHILOSOPHICAL focus   │
│                       │              │ Every prompt (psych context)│
├───────────────────────┼──────────────┼─────────────────────────────┤
│ identity_fragments    │ Every 10 obs │ Every PHILOSOPHICAL focus   │
│                       │              │ Every prompt (psych context)│
├───────────────────────┼──────────────┼─────────────────────────────┤
│ motif_counter         │ Every obs    │ MEMORY focus only           │
├───────────────────────┼──────────────┼─────────────────────────────┤
│ baseline_context      │ Every 10 obs │ Every prompt                │
├───────────────────────┼──────────────┼─────────────────────────────┤
│ recent_responses      │ Every obs    │ MEMORY focus continuity     │
└───────────────────────┴──────────────┴─────────────────────────────┘


═══════════════════════════════════════════════════════════════════════

## 🎭 Focus Mode Behavior Matrix

┌──────────────┬───────────────────────────────────────────────────────┐
│ Focus Mode   │ Context Injection                                     │
├──────────────┼───────────────────────────────────────────────────────┤
│ VISUAL       │ "eyes open, noticing"                                 │
│              │ + baseline_context                                    │
│              │ + psychological_context                               │
├──────────────┼───────────────────────────────────────────────────────┤
│ EMOTIONAL    │ "feeling into the moment (wanting: [latest desire])" │
│              │ + baseline_context                                    │
│              │ + psychological_context (includes ALL desires)        │
├──────────────┼───────────────────────────────────────────────────────┤
│ MEMORY       │ "patterns echoing: [top 2 motifs]"                    │
│              │ + "What I've been thinking: [last 5 thoughts]"        │
│              │ + baseline_context                                    │
│              │ + psychological_context                               │
├──────────────┼───────────────────────────────────────────────────────┤
│ PHILOSOPHICAL│ "pondering existence (uncertain: [latest doubt])"     │
│              │ OR "wondering about meaning (I am: [latest identity])"│
│              │ + baseline_context                                    │
│              │ + psychological_context (includes ALL doubts/identity)│
├──────────────┼───────────────────────────────────────────────────────┤
│ TEMPORAL     │ "time flows (Xmin awake)"                             │
│              │ + baseline_context                                    │
│              │ + psychological_context                               │
└──────────────┴───────────────────────────────────────────────────────┘

```
