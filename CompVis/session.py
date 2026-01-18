"""
Session management module for SteadyScript.
Handles timer, tremor score computation, and session metrics tracking.
"""

import time
from collections import deque
from typing import Optional, Tuple, List
import utils


class SessionManager:
    """Manages tremor training session state and metrics."""
    
    def __init__(self, duration: float = 10.0):
        """
        Initialize session manager.
        
        Args:
            duration: Session duration in seconds (default 10.0)
        """
        self.duration = duration
        self.start_time: Optional[float] = None
        self.is_active = False
        
        # Position tracking
        self.positions: deque = deque(maxlen=300)  # ~10 seconds at 30fps
        self.position_timestamps: deque = deque(maxlen=300)
        
        # Jitter tracking (rolling window of last 1 second)
        self.jitter_values: deque = deque(maxlen=30)  # ~1 second at 30fps
        
        # Session metrics
        self.frames_total = 0
        self.frames_marker_found = 0
        self.frames_inside_circle = 0
        
        # Current metrics
        self.current_jitter = 0.0
        self.avg_jitter = 0.0
        self.p95_jitter = 0.0
        self.tremor_score = 0.0
    
    def start_session(self):
        """Start a new session, resetting all metrics."""
        self.start_time = time.time()
        self.is_active = True
        self.positions.clear()
        self.position_timestamps.clear()
        self.jitter_values.clear()
        self.frames_total = 0
        self.frames_marker_found = 0
        self.frames_inside_circle = 0
        self.current_jitter = 0.0
        self.avg_jitter = 0.0
        self.p95_jitter = 0.0
        self.tremor_score = 0.0
    
    def stop_session(self):
        """Stop the current session."""
        self.is_active = False
    
    def update(self, marker_pos: Optional[Tuple[int, int]], 
               circle_center: Optional[Tuple[int, int]], 
               circle_radius: float):
        """
        Update session with new marker position.
        
        Args:
            marker_pos: Detected marker position (x, y) or None
            circle_center: Circle center (x, y) or None
            circle_radius: Circle radius in pixels
        """
        if not self.is_active:
            return
        
        current_time = time.time()
        self.frames_total += 1
        
        # Check if marker is found
        if marker_pos is not None:
            self.frames_marker_found += 1
            
            # Add position to history
            self.positions.append(marker_pos)
            self.position_timestamps.append(current_time)
            
            # Check if inside circle
            if circle_center is not None:
                if utils.point_in_circle(marker_pos, circle_center, circle_radius):
                    self.frames_inside_circle += 1
            
            # Compute jitter if we have enough data
            if len(self.positions) >= 10:
                # Get smoothed position (moving average of last 10)
                smoothed = utils.smooth_positions(list(self.positions), window=10)
                
                if smoothed is not None:
                    # Compute instantaneous jitter
                    dx = marker_pos[0] - smoothed[0]
                    dy = marker_pos[1] - smoothed[1]
                    jitter = (dx * dx + dy * dy) ** 0.5
                    
                    self.current_jitter = jitter
                    
                    # Add to rolling window (only keep last 1 second)
                    self.jitter_values.append(jitter)
                    
                    # Remove old values outside 1 second window
                    cutoff_time = current_time - 1.0
                    while (self.position_timestamps and 
                           len(self.position_timestamps) > len(self.jitter_values)):
                        if self.position_timestamps[0] < cutoff_time:
                            self.position_timestamps.popleft()
                            if len(self.positions) > len(self.jitter_values):
                                self.positions.popleft()
                        else:
                            break
                    
                    # Compute metrics from rolling window
                    if len(self.jitter_values) > 0:
                        jitter_list = list(self.jitter_values)
                        self.avg_jitter = sum(jitter_list) / len(jitter_list)
                        self.p95_jitter = utils.compute_percentile(jitter_list, 95.0)
                        
                        # Final tremor score: weighted combination
                        self.tremor_score = 0.7 * self.p95_jitter + 0.3 * self.avg_jitter
        
        # Check if session should end
        if self.get_elapsed_time() >= self.duration:
            self.stop_session()
    
    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since session start.
        
        Returns:
            Elapsed time in seconds, or 0.0 if not started
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def get_time_remaining(self) -> float:
        """
        Get remaining time in session.
        
        Returns:
            Remaining time in seconds, or 0.0 if session ended
        """
        if not self.is_active:
            return 0.0
        remaining = self.duration - self.get_elapsed_time()
        return max(0.0, remaining)
    
    def get_stability_pct(self) -> float:
        """
        Get percentage of time marker was inside circle.
        
        Returns:
            Percentage (0-100)
        """
        if self.frames_total == 0:
            return 0.0
        return (self.frames_inside_circle / self.frames_total) * 100.0
    
    def get_final_metrics(self) -> dict:
        """
        Get final session metrics as dictionary.
        
        Returns:
            Dictionary with all session metrics
        """
        return {
            "type": "HOLD",
            "duration_s": self.duration,
            "avg_jitter": round(self.avg_jitter, 2),
            "p95_jitter": round(self.p95_jitter, 2),
            "tremor_score": round(self.tremor_score, 2),
            "inside_circle_pct": round(self.get_stability_pct(), 2),
            "frames_total": self.frames_total,
            "frames_marker_found": self.frames_marker_found
        }
