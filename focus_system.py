# Intelligent Focus System for Embodied AI
# Temporal-aware, context-accumulating consciousness director

import time
import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime

class FocusEngine:
    """
    Intelligent focus detection system that responds to temporal flow and accumulated context.
    
    Focus Modes:
    - VISUAL: New or changing visual elements, immediate attention
    - EMOTIONAL: Processing feelings, mood transitions, reactions
    - MEMORY: Exploring past observations, pattern recognition, familiarity
    - PHILOSOPHICAL: Deep introspection, identity, existence, meaning
    - TEMPORAL: Time awareness, duration consciousness, change perception
    """
    
    def __init__(self):
        # Core focus states
        self.current_focus = "VISUAL"  # Start with visual attention
        self.focus_history = deque(maxlen=20)  # Track focus transitions
        self.focus_durations = defaultdict(float)  # How long in each focus
        
        # Temporal tracking for boredom/introspection
        self.last_significant_change = time.time()
        self.static_duration = 0.0
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
        
        # Focus transition thresholds (dynamic, context-aware)
        self.boredom_threshold = 45.0  # seconds of static content
        self.introspection_threshold = 120.0  # seconds before deep philosophy
        self.novelty_sensitivity = 0.7
        
        # Current session tracking
        self.session_start = time.time()
        self.total_observations = 0
        
    def analyze_current_state(self, 
                            recent_observations: List[str], 
                            mood_vector: Tuple[float, float, float],
                            beliefs_count: int,
                            scene_changed: bool = False) -> Dict:
        """
        Analyze current consciousness state to determine optimal focus.
        
        Returns comprehensive state analysis for intelligent focus selection.
        """
        current_time = time.time()
        self.total_observations += 1
        self.observation_timestamps.append(current_time)
        
        # === TEMPORAL ANALYSIS ===
        session_duration = current_time - self.session_start
        
        # Calculate static duration (how long since significant change)
        if scene_changed:
            self.last_significant_change = current_time
            self.static_duration = 0.0
        else:
            self.static_duration = current_time - self.last_significant_change
            
        # === VISUAL NOVELTY ANALYSIS ===
        visual_novelty = self._calculate_visual_novelty(recent_observations)
        
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
    
    def determine_optimal_focus(self, state_analysis: Dict) -> Tuple[str, Dict]:
        """
        Intelligently determine optimal focus based on accumulated context.
        
        Returns: (focus_mode, focus_context)
        """
        current_time = time.time()
        
        # === FORCED ROTATION CHECK ===
        # Don't get stuck in VISUAL mode - rotate after too many observations
        if self.current_focus == "VISUAL":
            visual_observations = sum(1 for f in list(self.focus_history)[-6:] if f == "VISUAL")
            if visual_observations >= 4:  # 4+ VISUAL observations in last 6 = force change
                return self._force_focus_rotation(state_analysis, "breaking_visual_loop")
        
        # === IMMEDIATE ATTENTION TRIGGERS ===
        
        # High visual novelty captures attention (lowered threshold)
        if state_analysis['visual']['novelty_score'] > 0.6:  # Was 0.8
            return self._focus_visual(state_analysis, "high_novelty")
            
        # Significant emotional shifts need processing
        if state_analysis['emotional']['volatility'] > 0.6:
            return self._focus_emotional(state_analysis, "emotional_shift")
            
        # === TEMPORAL FLOW ANALYSIS ===
        
        static_duration = state_analysis['temporal']['static_duration']
        
        # Short static period - continue current focus or gentle visual attention
        if static_duration < 30:
            if self.current_focus == "VISUAL" and state_analysis['visual']['novelty_score'] > 0.15:  # Was 0.3
                return self._focus_visual(state_analysis, "continued_observation")
            else:
                return self._maintain_current_focus(state_analysis)
        
        # Medium static period - boredom begins, shift toward memory/emotional
        elif static_duration < self.boredom_threshold:
            if state_analysis['memory']['familiarity_high']:
                return self._focus_memory(state_analysis, "pattern_recognition")
            else:
                return self._focus_emotional(state_analysis, "inner_processing")
        
        # Long static period - deep introspection time
        elif static_duration < self.introspection_threshold:
            return self._focus_philosophical(state_analysis, "boredom_introspection")
            
        # Very long static - existential/temporal awareness
        else:
            return self._focus_temporal(state_analysis, "deep_contemplation")
    
    def _calculate_visual_novelty(self, recent_observations: List[str]) -> float:
        """Calculate visual novelty based on observation patterns."""
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
    
    def _focus_temporal(self, state: Dict, reason: str) -> Tuple[str, Dict]:
        """Temporal focus mode - time awareness and duration consciousness."""
        self._transition_focus("TEMPORAL", reason)
        
        context = {
            'mode': 'TEMPORAL',
            'reason': reason,
            'session_duration': state['temporal']['session_duration'],
            'time_awareness': state['consciousness_readiness']['temporal'],
            'attention_type': 'temporal_contemplation',
            'compression_level': 'low'  # Need temporal context
        }
        
        return "TEMPORAL", context
    
    def _maintain_current_focus(self, state: Dict) -> Tuple[str, Dict]:
        """Continue with current focus but update context."""
        
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
    
    def _transition_focus(self, new_focus: str, reason: str):
        """Handle focus transitions with temporal tracking."""
        current_time = time.time()
        
        # Update duration of previous focus
        if hasattr(self, 'focus_start_time'):
            duration = current_time - self.focus_start_time
            self.focus_durations[self.current_focus] += duration
        
        # Record transition (store as string for hashability)
        self.focus_history.append(new_focus)  # Just store the focus name for pattern analysis
        
        # Update current focus
        self.current_focus = new_focus
        self.focus_start_time = current_time
    
    def get_focus_summary(self) -> Dict:
        """Get summary of current focus state for debugging."""
        return {
            'current_focus': self.current_focus,
            'static_duration': self.static_duration,
            'visual_repetition': self.visual_repetition_score,
            'emotional_volatility': self.emotional_volatility,
            'total_observations': self.total_observations,
            'focus_history': list(self.focus_history)[-3:],
            'session_age': time.time() - self.session_start
        }
    
    def _force_focus_rotation(self, state: Dict, reason: str) -> Tuple[str, Dict]:
        """Force a focus rotation to break out of VISUAL loops"""
        # Cycle through non-visual focus modes
        focus_cycle = ["EMOTIONAL", "MEMORY", "PHILOSOPHICAL", "TEMPORAL"]
        
        # Pick next focus based on what we haven't visited recently
        recent_focuses = list(self.focus_history)[-4:]
        for focus in focus_cycle:
            if focus not in recent_focuses:
                # Found a fresh focus mode
                if focus == "EMOTIONAL":
                    return self._focus_emotional(state, reason)
                elif focus == "MEMORY":
                    return self._focus_memory(state, reason)
                elif focus == "PHILOSOPHICAL":
                    return self._focus_philosophical(state, reason)
                elif focus == "TEMPORAL":
                    return self._focus_temporal(state, reason)
        
        # All recently visited, just cycle to next
        return self._focus_emotional(state, reason)
    
    def _force_focus_change(self, reason: str = "forced_change"):
        """Force a focus change when repetition is detected"""
        # Cycle through focus modes to break repetition
        focus_cycle = ["EMOTIONAL", "MEMORY", "PHILOSOPHICAL", "TEMPORAL", "VISUAL"]
        
        try:
            current_index = focus_cycle.index(self.current_focus)
            next_focus = focus_cycle[(current_index + 1) % len(focus_cycle)]
        except ValueError:
            next_focus = "EMOTIONAL"  # Default if current focus not in cycle
        
        self._transition_focus(next_focus, reason)
        
        # Reset repetition tracking
        self.visual_repetition_score = 0.0
        self.static_duration = 0.0  # Reset to break focus patterns