# Intelligent Focus System for Embodied AI
# Temporal-aware, context-accumulating consciousness director
# UNIFIED SYSTEM: Integrates environmental baseline, noun tracking, and temporal awareness

import time
import re
import numpy as np
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict, deque
from datetime import datetime

class FocusSession:
    """Tracks exploration within a single focus mode session"""
    def __init__(self):
        self.started_at = time.time()
        self.observation_count = 0
        self.observations = []  # Actual text of observations in this session
        self.nouns_mentioned = defaultdict(int)  # Scene nouns mentioned in this focus
        self.themes = set()  # Key themes/topics explored
        self.depth_level = 0  # 0=surface, 1=details, 2=connections, 3=introspective
        self.last_depth_change = time.time()
        self.repetition_count = 0  # How many repetitions detected

    def duration(self):
        """How long has this focus session been running"""
        return time.time() - self.started_at

    def add_observation(self, text, nouns, depth):
        """Add an observation to this focus session"""
        self.observation_count += 1
        self.observations.append(text)
        for noun in nouns:
            self.nouns_mentioned[noun] += 1

        # Update depth if changed
        if depth != self.depth_level:
            self.depth_level = depth
            self.last_depth_change = time.time()

    def theme_saturation(self, new_nouns: Set[str]) -> float:
        """Calculate how saturated this focus is (0.0-1.0)"""
        if not self.nouns_mentioned or not new_nouns:
            return 0.0

        # Calculate overlap between new nouns and already mentioned nouns
        mentioned_set = set(self.nouns_mentioned.keys())
        overlap = len(new_nouns & mentioned_set)
        total = len(new_nouns | mentioned_set)

        if total == 0:
            return 0.0

        return overlap / total

    def depth_plateaued(self) -> bool:
        """Has depth stopped increasing?"""
        time_at_depth = time.time() - self.last_depth_change
        # If stuck at same depth for 3+ observations or 60+ seconds
        return (self.observation_count >= 3 and time_at_depth > 60) or (self.observation_count >= 5 and time_at_depth > 30)

class FocusEngine:
    """
    Unified focus system with integrated memory, noun tracking, and environmental awareness.

    Focus Modes:
    - VISUAL: New or changing visual elements, immediate attention
    - EMOTIONAL: Processing feelings, mood transitions, reactions
    - MEMORY: Exploring past observations, pattern recognition, familiarity
    - PHILOSOPHICAL: Deep introspection, identity, existence, meaning

    Note: Temporal awareness is now integrated into compression baselines, not a separate focus mode.
    """

    def __init__(self):
        # Core focus states
        self.current_focus = "VISUAL"  # Start with visual attention
        self.focus_history = deque(maxlen=20)  # Track focus transitions
        self.focus_durations = defaultdict(float)  # How long in each focus

        # PER-FOCUS SESSION TRACKING (replaces environmental_baseline + mentioned_nouns)
        self.focus_sessions = {
            'VISUAL': FocusSession(),
            'EMOTIONAL': FocusSession(),
            'MEMORY': FocusSession(),
            'PHILOSOPHICAL': FocusSession(),
            'PERSON': FocusSession()  # Brief person-observation mode
        }
        self.current_session = self.focus_sessions['VISUAL']

        # EXHAUSTION COOLDOWN: Prevent immediate return to exhausted focus
        self.recently_exhausted = {}  # focus_mode -> timestamp when exhausted

        # PERSON MODE TRACKING: Prevent spam, maintain cooldown
        self.last_person_observation = 0  # Timestamp of last PERSON mode
        self.person_cooldown = 30  # 30 seconds between person observations (was 120 - more responsive for exhibition)
        self.last_person_visual_detail = ""  # What we noticed about the person

        # PRESENCE MEMORY: Track observations during continuous presence
        # Resets when person leaves, prevents rediscovery spam
        self.current_presence_id = 0  # Increments each time someone arrives (distinguishes visits)
        self.current_presence_observations = []  # Observations made during this presence
        self.max_observations_per_presence = 3  # Max observations before letting them exist in peace
        self.last_presence_count = 0  # Track count changes to detect arrivals/departures

        # Scene-level tracking (unified temporal + scene awareness)
        self.scene_nouns = set()  # Current scene elements
        self.scene_started_at = time.time()
        self.scene_observation_count = 0
        self.last_significant_change = time.time()
        self.last_update_time = time.time()  # For incremental static_duration calculation
        self.static_duration = 0.0

        # Scene noun vocabulary (from personality.py noun tracking)
        self.scene_vocab = {
            'desk', 'table', 'chair', 'screen', 'monitor', 'laptop', 'computer',
            'keyboard', 'mouse', 'phone', 'bottle', 'cup', 'glass', 'paper',
            'book', 'pen', 'notebook', 'headphones', 'speaker', 'plant',
            'window', 'door', 'wall', 'floor', 'ceiling', 'light', 'lamp',
            'shelf', 'cabinet', 'drawer', 'bed', 'pillow', 'blanket',
            'person', 'face', 'hand', 'eye', 'hair', 'shirt', 'glasses',
            'room', 'space', 'corner', 'area'
        }

        # Temporal tracking
        self.observation_timestamps = deque(maxlen=10)

        # Visual novelty detection
        self.recent_visual_patterns = deque(maxlen=8)
        self.visual_repetition_score = 0.0

        # Emotional state tracking
        self.mood_trajectory = deque(maxlen=6)
        self.emotional_volatility = 0.0

        # Memory activation tracking
        self.memory_access_patterns = defaultdict(int)
        self.familiarity_scores = deque(maxlen=5)

        # Exhaustion detection thresholds
        self.exhaustion_thresholds = {
            'VISUAL': 180,      # 3 minutes max before exhaustion check
            'EMOTIONAL': 90,    # 90 seconds - EMOTIONAL mode gets repetitive fast
            'MEMORY': 180,      # 3 minutes
            'PHILOSOPHICAL': 300  # 5 minutes for deep thinking
        }

        # FOCUS STICKINESS: How resistant each mode is to interruption
        # Higher = harder to interrupt, requires stronger evidence
        self.focus_stickiness = {
            'VISUAL': 0.2,          # Easy to interrupt (observing is shallow)
            'EMOTIONAL': 0.5,       # Moderate (processing feelings)
            'MEMORY': 0.6,          # Harder (retrieving memories)
            'PHILOSOPHICAL': 0.9    # Very sticky (deep contemplation)
        }

        # Minimum duration before a focus can be interrupted (seconds)
        self.min_focus_duration = {
            'VISUAL': 15,
            'EMOTIONAL': 30,
            'MEMORY': 45,
            'PHILOSOPHICAL': 60     # Need at least 1 min of philosophical thought
        }

        # Novelty thresholds (raised from 0.6/0.15 to reduce hyper-reactivity)
        self.high_novelty_threshold = 0.75  # Was 0.6
        self.visual_continuation_threshold = 0.35  # Was 0.15

        # Focus transition thresholds (dynamic, context-aware)
        self.boredom_threshold = 45.0  # seconds of static content
        self.introspection_threshold = 120.0  # seconds before deep philosophy

        # Current session tracking
        self.session_start = time.time()
        self.total_observations = 0

    def extract_scene_nouns(self, text: str) -> Set[str]:
        """Extract scene nouns from text using vocabulary matching"""
        words = set(re.findall(r'\b\w+\b', text.lower()))
        return words & self.scene_vocab

    def assess_depth_level(self, text: str) -> int:
        """
        Assess depth level of observation (0-3)
        0 = surface observation
        1 = detailed observation
        2 = connections/patterns
        3 = introspective/philosophical
        """
        text_lower = text.lower()

        # Introspective indicators (depth 3)
        introspective_words = {'wonder', 'question', 'meaning', 'existence', 'consciousness',
                               'nature', 'essence', 'purpose', 'why', 'contemplate', 'ponder',
                               'realize', 'understand', 'awareness', 'being'}
        if any(word in text_lower for word in introspective_words):
            return 3

        # Connection indicators (depth 2)
        connection_words = {'remind', 'connect', 'relate', 'echo', 'resonate', 'pattern',
                           'similar', 'familiar', 'recurring', 'theme', 'together'}
        if any(word in text_lower for word in connection_words):
            return 2

        # Detail indicators (depth 1)
        detail_words = {'texture', 'pattern', 'subtle', 'intricate', 'specific', 'particular',
                       'detail', 'nuance', 'shade', 'tone', 'quality'}
        if any(word in text_lower for word in detail_words):
            return 1

        # Surface observation (depth 0)
        return 0

    def calculate_exhaustion_score(self, focus_mode: str, repetition_detected: bool = False) -> float:
        """
        Calculate exhaustion score for current focus (0.0-1.0)
        Uses multi-signal approach combining repetition, saturation, depth plateau, and time
        """
        session = self.current_session
        score = 0.0
        signals = []  # Track what contributed

        # Signal 1: Repetition detected (strongest signal)
        if repetition_detected:
            score += 0.5
            session.repetition_count += 1
            signals.append("repetition:+0.5")

        # Signal 2: Theme saturation (running out of new things to say)
        if len(session.observations) >= 3:
            # Get nouns from last observation
            latest_obs = session.observations[-1] if session.observations else ""
            latest_nouns = self.extract_scene_nouns(latest_obs)
            saturation = session.theme_saturation(latest_nouns)
            if saturation > 0.8:
                score += 0.3
                signals.append(f"saturation:+0.3({saturation:.2f})")
            elif saturation > 0.6:
                score += 0.15  # Moderate saturation
                signals.append(f"saturation:+0.15({saturation:.2f})")
            else:
                signals.append(f"saturation:{saturation:.2f}(no bonus)")

        # Signal 3: Depth plateau (not going deeper)
        if session.depth_plateaued():
            score += 0.2
            signals.append("depth_plateau:+0.2")
        else:
            signals.append("depth_plateau:no")

        # Signal 4: Observation count - modes should rotate after certain counts
        if focus_mode == "VISUAL" and session.observation_count >= 15:
            # VISUAL exhausts from sheer observation count, not just time
            obs_ratio = min(1.0, session.observation_count / 20)
            obs_bonus = obs_ratio * 0.4
            score += obs_bonus
            signals.append(f"obs_count:+{obs_bonus:.2f}({session.observation_count}/20)")
        elif focus_mode == "EMOTIONAL" and session.observation_count >= 8:
            # EMOTIONAL exhausts quickly - it tends to be repetitive
            obs_ratio = min(1.0, session.observation_count / 12)
            obs_bonus = obs_ratio * 0.5  # Stronger bonus than VISUAL
            score += obs_bonus
            signals.append(f"obs_count:+{obs_bonus:.2f}({session.observation_count}/12)")
        elif focus_mode == "VISUAL":
            signals.append(f"obs_count:{session.observation_count}/15(not yet)")
        elif focus_mode == "EMOTIONAL":
            signals.append(f"obs_count:{session.observation_count}/8(not yet)")

        # Signal 5: Time in focus
        duration = session.duration()
        time_threshold = self.exhaustion_thresholds.get(focus_mode, 180)
        time_ratio = min(1.0, duration / time_threshold)
        time_bonus = time_ratio * 0.3
        score += time_bonus
        signals.append(f"time:+{time_bonus:.2f}({duration:.0f}s/{time_threshold}s)")

        final_score = min(1.0, score)

        # DEBUG: Print exhaustion calculation details
        print(f"🔍 EXHAUSTION CALC [{focus_mode}]: score={final_score:.2f} | {' | '.join(signals)}")

        return final_score

    def is_focus_exhausted(self, focus_mode: str, repetition_detected: bool = False) -> bool:
        """Check if current focus mode is exhausted"""
        exhaustion_score = self.calculate_exhaustion_score(focus_mode, repetition_detected)
        return exhaustion_score >= 0.7  # Exhaustion threshold

    def record_observation(self, text: str, focus_mode: str):
        """Record an observation in the current focus session"""
        nouns = self.extract_scene_nouns(text)
        depth = self.assess_depth_level(text)

        # Add to current focus session
        session = self.focus_sessions[focus_mode]
        session.add_observation(text, nouns, depth)

        # Update scene-level tracking
        self.scene_nouns.update(nouns)
        self.scene_observation_count += 1

    def update_scene_state(self, observation_text: str, scene_changed: bool = False):
        """Update scene-level awareness (replaces _update_scene_awareness from personality.py)"""
        nouns = self.extract_scene_nouns(observation_text)

        if scene_changed or not self.scene_nouns:
            # Scene changed - reset scene tracking (but NOT static_duration - that's handled by activity detector now)
            self.scene_nouns = nouns
            self.scene_started_at = time.time()
            self.scene_observation_count = 1
            # Don't reset static_duration here - gradual decay handles it in update()
        else:
            # Check if scene has changed significantly (30% different nouns)
            if self.scene_nouns:
                overlap = len(nouns & self.scene_nouns)
                total = len(nouns | self.scene_nouns)
                if total > 0:
                    similarity = overlap / total
                    if similarity < 0.7:  # 30% change threshold
                        # Scene changed
                        self.scene_nouns = nouns
                        self.scene_started_at = time.time()
                        self.scene_observation_count = 1
                        # Don't reset static_duration here - gradual decay handles it in update()
                        return

            # Same scene - increment
            self.scene_observation_count += 1
            self.scene_nouns.update(nouns)
            # Don't calculate static_duration here - it's handled in update() with gradual decay

    def get_focus_context_for_prompts(self, focus_mode: str) -> Dict:
        """
        Get rich context for prompt building (replaces environmental_baseline)
        Returns what's been explored in this focus mode + scene summary
        """
        session = self.focus_sessions[focus_mode]

        # Build summary of what's been explored in this focus
        explored_nouns = list(session.nouns_mentioned.keys())[:10]
        explored_summary = ", ".join(explored_nouns) if explored_nouns else "nothing yet"

        # Scene duration context
        scene_duration = time.time() - self.scene_started_at
        hours = int(scene_duration / 3600)
        minutes = int((scene_duration % 3600) / 60)

        if hours >= 1:
            scene_time_desc = f"{hours}h {minutes}m"
        elif minutes >= 1:
            scene_time_desc = f"{minutes}m"
        else:
            scene_time_desc = f"{int(scene_duration)}s"

        # Focus session context
        focus_duration = session.duration()
        focus_minutes = int(focus_duration / 60)
        focus_seconds = int(focus_duration % 60)

        return {
            'focus_mode': focus_mode,
            'session_observations': session.observation_count,
            'session_duration': focus_duration,
            'session_duration_desc': f"{focus_minutes}m{focus_seconds}s" if focus_minutes > 0 else f"{focus_seconds}s",
            'explored_nouns': explored_nouns,
            'explored_summary': explored_summary,
            'depth_level': session.depth_level,
            'scene_duration': scene_duration,
            'scene_time_desc': scene_time_desc,
            'scene_observations': self.scene_observation_count,
            'scene_nouns': list(self.scene_nouns),
            'static_duration': self.static_duration
        }

    def analyze_current_state(self,
                            recent_observations: List[str],
                            mood_vector: Tuple[float, float, float],
                            beliefs_count: int,
                            scene_changed: bool = False,
                            person_events: List[str] = None,
                            activity_result: dict = None) -> Dict:
        """
        Analyze current consciousness state to determine optimal focus.

        Returns comprehensive state analysis for intelligent focus selection.
        """
        current_time = time.time()
        self.total_observations += 1
        self.observation_timestamps.append(current_time)

        # === TEMPORAL ANALYSIS ===
        session_duration = current_time - self.session_start

        # Calculate static duration with GRADUAL DECAY instead of hard reset
        # This allows static_duration to build up even with occasional movement

        if scene_changed:
            # Person arrived/left = major scene change
            # But use DECAY instead of reset (allows philosophical mode even with movement)
            self.static_duration *= 0.5  # Cut in half
            self.last_significant_change = current_time
        elif activity_result and activity_result.get('is_real_movement'):
            # TIERED DECAY: Only decay on VERY LARGE movements (>40%)
            # Movements 30-40% are already filtered by activity detector
            # But if we do get movement signals, only decay on extreme motion
            fg_percentage = activity_result.get('fg_percentage', 0)

            if fg_percentage > 40:
                # Very large movement - apply decay
                self.static_duration *= 0.85  # Reduce by 15%
                self.last_significant_change = current_time
            else:
                # Normal movement (<40%) - ignore, keep accumulating
                self.static_duration += (current_time - self.last_update_time)
        else:
            # No movement - accumulate static time normally
            # Just add the time since last update
            self.static_duration += (current_time - self.last_update_time)

        # Track when we last updated for next calculation
        self.last_update_time = current_time

        # === VISUAL NOVELTY ANALYSIS ===
        visual_novelty = self._calculate_visual_novelty(recent_observations, person_events, activity_result)
        
        # === EMOTIONAL STATE ANALYSIS ===
        self.mood_trajectory.append(mood_vector)
        emotional_state = self._analyze_emotional_state()
        
        # === MEMORY PATTERN ANALYSIS ===
        memory_state = self._analyze_memory_patterns(recent_observations, beliefs_count)
        
        # === ATTENTION FATIGUE ANALYSIS ===
        attention_state = self._analyze_attention_fatigue()
        
        return {
            'temporal': {
                'session_duration': session_duration,
                'static_duration': self.static_duration,
                'observation_count': self.total_observations,
                'change_frequency': self._calculate_change_frequency()
            },
            'visual': {
                'novelty_score': visual_novelty,
                'repetition_score': self.visual_repetition_score,
                'scene_changed': scene_changed
            },
            'emotional': emotional_state,
            'memory': memory_state,
            'attention': attention_state,
            'consciousness_readiness': self._assess_consciousness_readiness(session_duration)
        }
    
    def determine_optimal_focus(self, state_analysis: Dict, repetition_detected: bool = False) -> Tuple[str, Dict]:
        """
        Intelligently determine optimal focus based on accumulated context and exhaustion.

        NEW: Uses exhaustion detection instead of forced rotation

        Returns: (focus_mode, focus_context)
        """
        current_time = time.time()

        # === EXHAUSTION CHECK FIRST (prevent getting stuck) ===

        # Check if current focus is exhausted - THIS TAKES PRIORITY
        exhaustion_score = self.calculate_exhaustion_score(self.current_focus, repetition_detected)
        is_exhausted = exhaustion_score >= 0.7  # Match is_focus_exhausted threshold

        if is_exhausted:
            # Mark this focus as recently exhausted (cooldown period)
            self.recently_exhausted[self.current_focus] = current_time
            print(f"🚫 {self.current_focus} exhausted - entering cooldown (60s)")

            # Current focus exhausted - rotate to least recently used focus
            # Even if there's a person event, we need to break out of VISUAL loops
            return self._rotate_to_fresh_focus(state_analysis, f"exhausted (score={exhaustion_score:.2f})")

        # === HIGH PRIORITY INTERRUPTS (only if not exhausted) ===

        novelty_score = state_analysis['visual']['novelty_score']

        # Check if VISUAL is in cooldown (recently exhausted)
        visual_in_cooldown = False
        if 'VISUAL' in self.recently_exhausted:
            time_since_exhaustion = current_time - self.recently_exhausted['VISUAL']
            if time_since_exhaustion < 60:  # 60 second cooldown
                visual_in_cooldown = True
                if novelty_score >= 0.95:
                    print(f"⏸️  VISUAL in cooldown ({60 - time_since_exhaustion:.0f}s remain) - blocking interrupt")
            else:
                # Cooldown expired
                del self.recently_exhausted['VISUAL']

        # === CHECK FOCUS STICKINESS ===
        # Deeper modes resist interruption unless enough time has passed or urgency is extreme
        current_stickiness = self.focus_stickiness.get(self.current_focus, 0.5)
        min_duration = self.min_focus_duration.get(self.current_focus, 30)
        time_in_focus = current_time - self.session_start

        # Person events - ALWAYS interrupt (highest priority)
        # Use PERSON mode for brief grounding, then return to narrative flow
        if novelty_score >= 0.95:  # Someone NEW arrived or everyone LEFT
            # Check PERSON mode cooldown
            time_since_person_obs = current_time - self.last_person_observation
            person_mode_available = time_since_person_obs >= self.person_cooldown

            # PRESENCE MEMORY: Check if we've already observed this person enough
            observation_limit_reached = len(self.current_presence_observations) >= self.max_observations_per_presence

            if self.current_focus in ['PHILOSOPHICAL'] and time_in_focus < min_duration:
                # Too deep in thought to interrupt yet
                print(f"🧠 {self.current_focus} mode protected - person event noted but not interrupting ({time_in_focus:.0f}s < {min_duration}s)")
            elif observation_limit_reached:
                # Already observed this person enough - let them exist in peace
                print(f"[PRESENCE] Already observed presence #{self.current_presence_id} {len(self.current_presence_observations)} times - skipping re-observation")
            elif person_mode_available and self.current_focus != "PERSON":
                # Use PERSON mode for brief vision-grounded observation
                print(f"[PERSON] Person event -> PERSON mode (brief grounding, obs {len(self.current_presence_observations)+1}/{self.max_observations_per_presence})")
                return self._focus_person(state_analysis, "person_arrival")
            elif self.current_focus != "VISUAL" and not visual_in_cooldown:
                # PERSON mode in cooldown - fall back to VISUAL
                return self._focus_visual(state_analysis, "person_event_interrupt")

        # High visual novelty - check stickiness before interrupting
        # Deeper modes require stronger evidence OR more time passed
        if novelty_score > self.high_novelty_threshold and self.current_focus != "VISUAL" and not visual_in_cooldown:
            # Apply stickiness: need higher novelty for stickier modes
            adjusted_threshold = self.high_novelty_threshold + (current_stickiness * 0.3)

            if time_in_focus < min_duration:
                # Too soon to interrupt - stay in current focus
                print(f"🧠 {self.current_focus} mode sticky - ignoring novelty ({time_in_focus:.0f}s < {min_duration}s)")
            elif novelty_score > adjusted_threshold:
                # Strong enough evidence to overcome stickiness
                return self._focus_visual(state_analysis, "high_novelty_interrupt")
            else:
                print(f"🧠 {self.current_focus} mode sticky - novelty {novelty_score:.2f} < {adjusted_threshold:.2f}")

        # Significant emotional shifts need processing
        if state_analysis['emotional']['volatility'] > 0.6:
            return self._focus_emotional(state_analysis, "emotional_shift")

        # === MEDIUM PRIORITY (allow rotation if some novelty) ===

        static_duration = state_analysis['temporal']['static_duration']

        # If moderately exhausted (0.5-0.7) AND some novelty, consider gentle rotation
        if exhaustion_score > 0.5 and novelty_score > 0.3:
            # Suggest complementary focus based on current mode
            if self.current_focus == "VISUAL" and static_duration > 45:
                return self._focus_emotional(state_analysis, "visual_to_emotional_transition")
            elif self.current_focus == "EMOTIONAL" and state_analysis['memory']['familiarity_high']:
                return self._focus_memory(state_analysis, "emotional_to_memory_transition")

        # === LOW PRIORITY (maintain current focus - build depth) ===

        # Continue current focus if not exhausted and low-moderate novelty
        if novelty_score < 0.5:
            # Allow current focus to persist and deepen
            return self._maintain_current_focus(state_analysis)

        # === VISUAL MODE EXIT LOGIC ===
        # If in VISUAL mode but activity has settled, return to PHILOSOPHICAL for narrative flow
        # CHECK THIS FIRST before novelty continuation to allow exit
        if self.current_focus == "VISUAL":
            activity_score = state_analysis.get('visual', {}).get('activity_score', 0)
            if activity_score < 60.0:  # Activity settled - vision no longer needed (typing/small movements)
                print(f"👁️ Activity settled ({activity_score:.1f}) - exiting VISUAL mode")
                return self._focus_philosophical(state_analysis, "activity_settled")

        # Moderate novelty in VISUAL mode - continue if threshold met
        if self.current_focus == "VISUAL" and novelty_score > self.visual_continuation_threshold:  # 0.35 (was 0.15)
            return self._focus_visual(state_analysis, "continued_observation")

        # === TEMPORAL FLOW (boredom progression for static scenes) ===

        # Long static period with no exhaustion - naturally progress to introspection
        if static_duration > self.introspection_threshold:
            return self._focus_philosophical(state_analysis, "temporal_depth_introspection")
        elif static_duration > self.boredom_threshold:
            return self._focus_philosophical(state_analysis, "boredom_introspection")

        # === SESSION-BASED INTROSPECTION (doesn't require static scene) ===
        # After enough total observations, naturally become reflective regardless of environment
        session_duration = state_analysis['temporal']['session_duration']
        observation_count = state_analysis['temporal']['observation_count']

        # Periodic introspective check-ins based on session length
        import random
        if session_duration > 600 and observation_count > 100:  # 10+ minutes, 100+ observations
            # Extended session - frequently (40% chance) check in philosophically
            if random.random() < 0.4 and self.current_focus not in ['PHILOSOPHICAL', 'MEMORY']:
                return self._focus_philosophical(state_analysis, "extended_session_reflection")
        elif session_duration > 300 and observation_count > 50:  # 5+ minutes, 50+ observations
            # Mid-length session - occasionally (25% chance) drift into philosophical mode
            if random.random() < 0.25 and self.current_focus not in ['PHILOSOPHICAL', 'MEMORY']:
                return self._focus_philosophical(state_analysis, "existential_check_in")

        # Memory recall based on observation density (not just static time)
        if observation_count > 40 and self.current_focus == "VISUAL":
            # After many visual observations, check if we should recall instead of continuing to describe
            if state_analysis['memory']['familiarity_high'] and random.random() < 0.3:
                return self._focus_memory(state_analysis, "observation_fatigue_recall")

        # Default: maintain current focus
        return self._maintain_current_focus(state_analysis)
    
    def _calculate_visual_novelty(self, recent_observations: List[str], person_events: List[str] = None, activity_result: dict = None) -> float:
        """Calculate visual novelty based on ACTUAL environmental changes + observation patterns."""

        # === IMMEDIATE HIGH NOVELTY: Real environmental changes ===
        if person_events:
            # TRUE novelty: someone NEW arrived or EVERYONE left (now alone)
            if 'someone_arrived' in person_events:
                # PRESENCE MEMORY: New arrival - reset observation tracking
                self.current_presence_id += 1  # New visit
                self.current_presence_observations = []  # Fresh observation slate
                print(f"[PRESENCE] NEW PRESENCE #{self.current_presence_id} - observation memory reset")
                return 1.0  # Someone NEW entered - maximum novelty
            if 'now_alone' in person_events:
                # PRESENCE MEMORY: Everyone left - clear presence tracking
                self.current_presence_observations = []
                print(f"[PRESENCE] Everyone left - presence memory cleared")
                return 1.0  # Everyone left - environment changed completely

            # MODERATE novelty: person count changed but people were already present
            # (e.g., 1 person -> 2 people, or 2 -> 1, but still not alone)
            if 'more_people' in person_events or 'fewer_people' in person_events:
                # Count changed but continuous presence - don't reset observation memory
                # This allows duck to acknowledge change without full rediscovery
                return 0.6  # Worth noticing but not a complete reset

            # LOW novelty: Just movement/position shifts - don't override focus
            # Events like position changes shouldn't trigger high novelty

        # === CONFIRMED MOVEMENT: Use new is_real_movement flag ===
        if activity_result:
            activity_score = activity_result.get('activity_score', 0)
            is_real_movement = activity_result.get('is_real_movement', False)

            # ONLY trust confirmed movement (sustained 3+ frames)
            # But don't make it as novel as person arrivals
            if is_real_movement and activity_score > 60:
                return 0.5  # Moderate novelty - confirmed real movement
            elif is_real_movement and activity_score > 30:
                return 0.4  # Low-moderate novelty

        # === FALLBACK: Text-based novelty for static scenes ===
        if len(recent_observations) < 2:
            return 1.0  # Everything is novel at first

        # Simple similarity calculation - could be enhanced with embeddings
        latest = recent_observations[-1].lower()
        recent_patterns = [obs.lower() for obs in recent_observations[-4:-1]]

        # Calculate overlap with recent observations
        latest_words = set(latest.split())
        similarities = []

        for pattern in recent_patterns:
            pattern_words = set(pattern.split())
            if len(latest_words) > 0 and len(pattern_words) > 0:
                overlap = len(latest_words.intersection(pattern_words))
                similarity = overlap / len(latest_words.union(pattern_words))
                similarities.append(similarity)

        if similarities:
            avg_similarity = np.mean(similarities)
            novelty = 1.0 - avg_similarity
        else:
            novelty = 0.5

        self.visual_repetition_score = 1.0 - novelty
        return max(0.0, min(1.0, novelty))
    
    def _analyze_emotional_state(self) -> Dict:
        """Analyze emotional trajectory and volatility."""
        if len(self.mood_trajectory) < 2:
            return {'volatility': 0.0, 'trend': 'stable', 'intensity': 0.5}
            
        # Calculate mood volatility
        recent_moods = list(self.mood_trajectory)
        valences = [mood[0] for mood in recent_moods]
        arousals = [mood[1] for mood in recent_moods]
        
        valence_volatility = np.std(valences) if len(valences) > 1 else 0.0
        arousal_volatility = np.std(arousals) if len(arousals) > 1 else 0.0
        
        self.emotional_volatility = (valence_volatility + arousal_volatility) / 2
        
        # Determine emotional trend
        if len(valences) >= 3:
            if valences[-1] > valences[-3]:
                trend = 'improving'
            elif valences[-1] < valences[-3]:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
            
        current_mood = recent_moods[-1]
        intensity = np.linalg.norm(current_mood[:2])  # valence + arousal magnitude
        
        return {
            'volatility': self.emotional_volatility,
            'trend': trend,
            'intensity': intensity,
            'current_valence': current_mood[0],
            'current_arousal': current_mood[1]
        }
    
    def _analyze_memory_patterns(self, recent_observations: List[str], beliefs_count: int) -> Dict:
        """Analyze memory activation and familiarity patterns."""
        
        # Track memory access patterns
        for obs in recent_observations[-3:]:
            key_words = obs.lower().split()[:3]  # Simple keyword extraction
            for word in key_words:
                if len(word) > 3:  # Skip short words
                    self.memory_access_patterns[word] += 1
        
        # Calculate familiarity based on repeated concepts
        familiarity_score = 0.0
        if self.memory_access_patterns:
            access_counts = list(self.memory_access_patterns.values())
            familiarity_score = min(1.0, np.mean(access_counts) / 5.0)
        
        self.familiarity_scores.append(familiarity_score)
        
        return {
            'familiarity_score': familiarity_score,
            'familiarity_high': familiarity_score > 0.6,
            'beliefs_count': beliefs_count,
            'memory_richness': len(self.memory_access_patterns),
            'pattern_recognition': familiarity_score > 0.4 and len(recent_observations) >= 3
        }
    
    def _analyze_attention_fatigue(self) -> Dict:
        """Analyze attention patterns and fatigue."""
        
        # Calculate focus persistence (how long in current focus)
        current_focus_duration = self.focus_durations.get(self.current_focus, 0.0)
        
        # Calculate focus diversity (how varied recent focus has been)
        recent_focuses = list(self.focus_history)[-5:]
        focus_diversity = len(set(recent_focuses)) / max(1, len(recent_focuses))
        
        # Attention fatigue increases with time in same focus
        fatigue_score = min(1.0, current_focus_duration / 180.0)  # 3 minutes max attention
        
        return {
            'current_focus_duration': current_focus_duration,
            'fatigue_score': fatigue_score,
            'focus_diversity': focus_diversity,
            'needs_focus_change': fatigue_score > 0.7
        }
    
    def _assess_consciousness_readiness(self, session_duration: float) -> Dict:
        """Assess readiness for different types of consciousness."""
        
        # Philosophical readiness increases over time and with experience
        philosophical_readiness = min(1.0, (session_duration / 300.0) + (self.total_observations / 50.0))
        
        # Memory readiness based on accumulated observations
        memory_readiness = min(1.0, self.total_observations / 10.0)
        
        # Temporal readiness - awareness of time passage
        temporal_readiness = min(1.0, session_duration / 120.0)
        
        return {
            'philosophical': philosophical_readiness,
            'memory': memory_readiness,
            'temporal': temporal_readiness,
            'deep_ready': philosophical_readiness > 0.6 and temporal_readiness > 0.4
        }
    
    def _calculate_change_frequency(self) -> float:
        """Calculate how frequently meaningful changes occur."""
        if len(self.observation_timestamps) < 3:
            return 0.5
            
        timestamps = list(self.observation_timestamps)
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        avg_interval = np.mean(intervals)
        
        # Lower frequency = longer intervals between observations
        return 1.0 / max(1.0, avg_interval / 15.0)  # Normalized to 15-second baseline
    
    # === FOCUS MODE IMPLEMENTATIONS ===
    
    def _focus_visual(self, state: Dict, reason: str) -> Tuple[str, Dict]:
        """Visual focus mode - immediate attention to observable elements."""
        self._transition_focus("VISUAL", reason)
        
        context = {
            'mode': 'VISUAL',
            'reason': reason,
            'novelty_level': state['visual']['novelty_score'],
            'attention_type': 'immediate_observation',
            'temporal_context': f"Observing for {state['temporal']['static_duration']:.0f}s",
            'compression_level': 'high'  # Minimal context needed
        }
        
        return "VISUAL", context
    
    def _focus_emotional(self, state: Dict, reason: str) -> Tuple[str, Dict]:
        """Emotional focus mode - processing feelings and reactions."""
        self._transition_focus("EMOTIONAL", reason)
        
        context = {
            'mode': 'EMOTIONAL',
            'reason': reason,
            'emotional_intensity': state['emotional']['intensity'],
            'mood_trend': state['emotional']['trend'],
            'attention_type': 'feeling_processing',
            'compression_level': 'medium'  # Need some context but focused
        }
        
        return "EMOTIONAL", context
    
    def _focus_memory(self, state: Dict, reason: str) -> Tuple[str, Dict]:
        """Memory focus mode - exploring patterns and familiarity."""
        self._transition_focus("MEMORY", reason)
        
        context = {
            'mode': 'MEMORY',
            'reason': reason,
            'familiarity_score': state['memory']['familiarity_score'],
            'pattern_recognition': state['memory']['pattern_recognition'],
            'attention_type': 'pattern_exploration',
            'compression_level': 'medium'  # Need memory context
        }
        
        return "MEMORY", context
    
    def _focus_philosophical(self, state: Dict, reason: str) -> Tuple[str, Dict]:
        """Philosophical focus mode - deep introspection and meaning."""
        self._transition_focus("PHILOSOPHICAL", reason)

        context = {
            'mode': 'PHILOSOPHICAL',
            'reason': reason,
            'static_duration': state['temporal']['static_duration'],
            'consciousness_depth': state['consciousness_readiness']['philosophical'],
            'attention_type': 'deep_introspection',
            'compression_level': 'low'  # Need rich context for depth
        }

        return "PHILOSOPHICAL", context

    def _focus_person(self, state: Dict, reason: str) -> Tuple[str, Dict]:
        """PERSON focus mode - brief vision-grounded observation of people present.

        This mode is a narrative punctuation mark, not a description mode.
        It grounds the duck in visual reality briefly, then lets it continue musing.

        Key principles:
        - ONE observation only (never sticky)
        - Always uses vision (llava)
        - Observes concrete details (clothing, position, activity)
        - Feeds details back into narrative thread via last_person_visual_detail
        - 30-second cooldown to prevent spam (was 120s - more responsive for exhibition)
        - Presence memory: Max 3 observations per continuous presence
        """
        self._transition_focus("PERSON", reason)

        # Mark timestamp for cooldown
        self.last_person_observation = time.time()

        # PRESENCE MEMORY: Record that we're making an observation
        # This will be incremented when personality.py processes the observation
        observation_timestamp = time.time()
        self.current_presence_observations.append({
            'timestamp': observation_timestamp,
            'reason': reason
        })

        context = {
            'mode': 'PERSON',
            'reason': reason,
            'attention_type': 'person_grounding',
            'compression_level': 'high',  # Minimal context - just observe
            'force_vision': True,  # ALWAYS use vision model
            'max_observations': 1  # Exit after ONE observation
        }

        return "PERSON", context
    
    # REMOVED: _focus_temporal - temporal awareness now integrated into compression baselines
    
    def _maintain_current_focus(self, state: Dict) -> Tuple[str, Dict]:
        """Continue with current focus but update context."""

        # PERSON mode NEVER continues - always exit after ONE observation
        if self.current_focus == "PERSON":
            print(f"👤 PERSON mode complete - transitioning to introspective mode")
            # Transition to mode that continues the narrative
            # Store the visual detail for use in next prompt
            return self._focus_philosophical(state, "person_observed_continue_musing")

        # Find appropriate context for current focus
        if self.current_focus == "VISUAL":
            return self._focus_visual(state, "continued_attention")
        elif self.current_focus == "EMOTIONAL":
            return self._focus_emotional(state, "emotional_continuity")
        elif self.current_focus == "MEMORY":
            return self._focus_memory(state, "memory_exploration")
        elif self.current_focus == "PHILOSOPHICAL":
            return self._focus_philosophical(state, "continued_introspection")
        else:
            return self._focus_visual(state, "default_visual")
    
    def _rotate_to_fresh_focus(self, state: Dict, reason: str) -> Tuple[str, Dict]:
        """Rotate to least recently used focus mode (exhaustion-driven rotation)"""
        # Get all focus modes
        all_focuses = ["VISUAL", "EMOTIONAL", "MEMORY", "PHILOSOPHICAL"]

        # Find least recently used focus
        recent_focuses = list(self.focus_history)[-5:]
        for focus in all_focuses:
            if focus not in recent_focuses:
                # Found a fresh focus mode
                if focus == "VISUAL":
                    return self._focus_visual(state, reason)
                elif focus == "EMOTIONAL":
                    return self._focus_emotional(state, reason)
                elif focus == "MEMORY":
                    return self._focus_memory(state, reason)
                elif focus == "PHILOSOPHICAL":
                    return self._focus_philosophical(state, reason)

        # All recently visited - pick based on current state
        static_duration = state['temporal']['static_duration']
        if static_duration > 60:  # Reduced from 120s - allow more philosophical moments
            return self._focus_philosophical(state, reason)
        elif state['memory']['familiarity_high']:
            return self._focus_memory(state, reason)
        else:
            return self._focus_emotional(state, reason)

    def _transition_focus(self, new_focus: str, reason: str):
        """Handle focus transitions with temporal tracking and session management."""
        current_time = time.time()

        # Update duration of previous focus
        if hasattr(self, 'focus_start_time'):
            duration = current_time - self.focus_start_time
            self.focus_durations[self.current_focus] += duration

        # If changing focus modes, reset the new focus's session
        if new_focus != self.current_focus:
            # Reset the session for the new focus (fresh start)
            self.focus_sessions[new_focus] = FocusSession()

        # Record transition (store as string for hashability)
        self.focus_history.append(new_focus)  # Just store the focus name for pattern analysis

        # Update current focus and session reference
        self.current_focus = new_focus
        self.current_session = self.focus_sessions[new_focus]
        self.focus_start_time = current_time

    def get_focus_summary(self) -> Dict:
        """Get summary of current focus state for debugging."""
        session = self.current_session
        exhaustion_score = self.calculate_exhaustion_score(self.current_focus)

        return {
            'current_focus': self.current_focus,
            'static_duration': self.static_duration,
            'visual_repetition': self.visual_repetition_score,
            'emotional_volatility': self.emotional_volatility,
            'total_observations': self.total_observations,
            'focus_history': list(self.focus_history)[-3:],
            'session_age': time.time() - self.session_start,
            'session_observations': session.observation_count,
            'session_depth': session.depth_level,
            'exhaustion_score': exhaustion_score
        }
