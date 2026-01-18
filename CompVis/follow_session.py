"""
Follow session management module for Level 2 FOLLOW mode.
Handles movement quality metrics: jitter, jerk (smoothness), and path efficiency.
"""

import time
import math
from collections import deque
from typing import Optional, Tuple, List
import utils


# Configuration constants for movement quality scoring
FOLLOW_CONFIG = {
    "duration": 20.0,  # 20 seconds for FOLLOW mode
    "jitter_ref": 6.0,  # Reference jitter threshold (pixels) - adjusted for movement tasks
    "jerk_ref": 80.0,  # Reference jerk threshold (pixels/s³) - adjusted for movement tasks
    "wobble_ref": 0.4,  # Reference wobble ratio threshold - adjusted for movement tasks
    "smoothing_window": 10,  # Frames for moving average
    "rolling_window_seconds": 1.0,  # Rolling window duration
}


class FollowSessionManager:
    """Manages FOLLOW mode session state and movement quality metrics."""
    
    def __init__(self, duration: float = None):
        """Initialize follow session manager."""
        self.duration = duration or FOLLOW_CONFIG["duration"]
        self.start_time: Optional[float] = None
        self.is_active = False
        
        # Position tracking
        self.positions: deque = deque(maxlen=600)  # ~20 seconds at 30fps
        self.position_timestamps: deque = deque(maxlen=600)
        
        # Velocity and acceleration tracking
        self.velocities: deque = deque(maxlen=600)
        self.accelerations: deque = deque(maxlen=600)
        
        # Jitter tracking (rolling window of last 1 second)
        self.jitter_values: deque = deque(maxlen=30)  # ~1 second at 30fps
        
        # Jerk tracking (rolling window)
        self.jerk_values: deque = deque(maxlen=30)
        
        # Path tracking for wobble ratio
        self.total_path_length = 0.0
        self.first_position: Optional[Tuple[float, float]] = None
        
        # Target error tracking (optional)
        self.target_errors: deque = deque(maxlen=600)
        
        # Session metrics
        self.frames_total = 0
        self.frames_marker_found = 0
        
        # Current metrics
        self.current_jitter = 0.0
        self.avg_jitter = 0.0
        self.p95_jitter = 0.0
        
        self.current_jerk = 0.0
        self.avg_jerk = 0.0
        self.p95_jerk = 0.0
        
        self.wobble_ratio = 0.0
        
        self.avg_target_error = 0.0
        self.p95_target_error = 0.0
        
        self.movement_quality_score = 0.0
    
    def start_session(self):
        """Start a new session, resetting all metrics."""
        self.start_time = time.time()
        self.is_active = True
        self.positions.clear()
        self.position_timestamps.clear()
        self.velocities.clear()
        self.accelerations.clear()
        self.jitter_values.clear()
        self.jerk_values.clear()
        self.target_errors.clear()
        
        self.frames_total = 0
        self.frames_marker_found = 0
        
        self.total_path_length = 0.0
        self.first_position = None
        
        self.current_jitter = 0.0
        self.avg_jitter = 0.0
        self.p95_jitter = 0.0
        self.current_jerk = 0.0
        self.avg_jerk = 0.0
        self.p95_jerk = 0.0
        self.wobble_ratio = 0.0
        self.avg_target_error = 0.0
        self.p95_target_error = 0.0
        self.movement_quality_score = 0.0
    
    def stop_session(self):
        """Stop the current session and compute final metrics."""
        self.is_active = False
        self._compute_final_metrics()
    
    def update(self, marker_pos: Optional[Tuple[int, int]], 
               target_pos: Optional[Tuple[int, int]] = None,
               dt: float = 1.0/30.0):
        """Update session with new marker position."""
        if not self.is_active:
            return
        
        current_time = time.time()
        self.frames_total += 1
        
        # Check if marker is found
        if marker_pos is not None:
            self.frames_marker_found += 1
            
            # Store first position for path efficiency
            if self.first_position is None:
                self.first_position = (float(marker_pos[0]), float(marker_pos[1]))
            
            # Add position to history
            pos_float = (float(marker_pos[0]), float(marker_pos[1]))
            self.positions.append(pos_float)
            self.position_timestamps.append(current_time)
            
            # Update path length
            if len(self.positions) > 1:
                prev_pos = self.positions[-2]
                dx = pos_float[0] - prev_pos[0]
                dy = pos_float[1] - prev_pos[1]
                segment_length = math.sqrt(dx*dx + dy*dy)
                self.total_path_length += segment_length
            
            # Compute velocity
            if len(self.positions) >= 2:
                prev_pos = self.positions[-2]
                vx = (pos_float[0] - prev_pos[0]) / dt
                vy = (pos_float[1] - prev_pos[1]) / dt
                velocity = (vx, vy)
                self.velocities.append(velocity)
            
            # Compute acceleration
            if len(self.velocities) >= 2:
                prev_vel = self.velocities[-2]
                curr_vel = self.velocities[-1]
                ax = (curr_vel[0] - prev_vel[0]) / dt
                ay = (curr_vel[1] - prev_vel[1]) / dt
                acceleration = (ax, ay)
                self.accelerations.append(acceleration)
            
            # Compute jerk
            if len(self.accelerations) >= 2:
                prev_acc = self.accelerations[-2]
                curr_acc = self.accelerations[-1]
                jx = (curr_acc[0] - prev_acc[0]) / dt
                jy = (curr_acc[1] - prev_acc[1]) / dt
                jerk_magnitude = math.sqrt(jx*jx + jy*jy)
                self.current_jerk = jerk_magnitude
                self.jerk_values.append(jerk_magnitude)
            
            # Compute jitter if we have enough data
            if len(self.positions) >= FOLLOW_CONFIG["smoothing_window"]:
                smoothed = utils.smooth_positions(
                    list(self.positions), 
                    window=FOLLOW_CONFIG["smoothing_window"]
                )
                
                if smoothed is not None:
                    dx = pos_float[0] - smoothed[0]
                    dy = pos_float[1] - smoothed[1]
                    jitter = math.sqrt(dx*dx + dy*dy)
                    
                    self.current_jitter = jitter
                    self.jitter_values.append(jitter)
            
            # Compute target error (optional - for display only, not penalized)
            # We don't penalize for target accuracy, just track it for info
            if target_pos is not None:
                dx = pos_float[0] - target_pos[0]
                dy = pos_float[1] - target_pos[1]
                error = math.sqrt(dx*dx + dy*dy)
                self.target_errors.append(error)
            
            # Update rolling window metrics
            self._update_rolling_metrics(current_time)
        
        # Check if session should end
        if self.get_elapsed_time() >= self.duration:
            self.stop_session()
    
    def _update_rolling_metrics(self, current_time: float):
        """Update rolling window metrics (last 1 second)."""
        cutoff_time = current_time - FOLLOW_CONFIG["rolling_window_seconds"]
        
        # Clean old jitter values
        while (self.position_timestamps and 
               len(self.position_timestamps) > len(self.jitter_values)):
            if self.position_timestamps[0] < cutoff_time:
                self.position_timestamps.popleft()
                if len(self.positions) > len(self.jitter_values):
                    self.positions.popleft()
            else:
                break
        
        # Compute jitter metrics from rolling window
        if len(self.jitter_values) > 0:
            jitter_list = list(self.jitter_values)
            self.avg_jitter = sum(jitter_list) / len(jitter_list)
            self.p95_jitter = utils.compute_percentile(jitter_list, 95.0)
        
        # Compute jerk metrics from rolling window
        if len(self.jerk_values) > 0:
            jerk_list = list(self.jerk_values)
            self.avg_jerk = sum(jerk_list) / len(jerk_list)
            self.p95_jerk = utils.compute_percentile(jerk_list, 95.0)
    
    def _compute_final_metrics(self):
        """Compute final session metrics including wobble ratio and movement quality score."""
        # Compute wobble ratio
        if len(self.positions) >= 2 and self.total_path_length > 0:
            smooth_path_length = 0.0
            smoothed_positions = []
            
            for i in range(len(self.positions)):
                window_start = max(0, i - FOLLOW_CONFIG["smoothing_window"])
                window_positions = list(self.positions)[window_start:i+1]
                smoothed = utils.smooth_positions(window_positions, window=len(window_positions))
                if smoothed:
                    smoothed_positions.append(smoothed)
            
            for i in range(1, len(smoothed_positions)):
                dx = smoothed_positions[i][0] - smoothed_positions[i-1][0]
                dy = smoothed_positions[i][1] - smoothed_positions[i-1][1]
                smooth_path_length += math.sqrt(dx*dx + dy*dy)
            
            if self.total_path_length > 0:
                self.wobble_ratio = (self.total_path_length - smooth_path_length) / (self.total_path_length + 1e-6)
        
        # Compute target error metrics (if available)
        if len(self.target_errors) > 0:
            error_list = list(self.target_errors)
            self.avg_target_error = sum(error_list) / len(error_list)
            self.p95_target_error = utils.compute_percentile(error_list, 95.0)
        
        # Compute movement quality score
        self._compute_movement_quality_score()
    
    def _compute_movement_quality_score(self):
        """Compute final movement quality score [0, 100]."""
        jitter_norm = min(self.p95_jitter / FOLLOW_CONFIG["jitter_ref"], 2.0)
        jerk_norm = min(self.p95_jerk / FOLLOW_CONFIG["jerk_ref"], 2.0)
        wobble_norm = min(self.wobble_ratio / FOLLOW_CONFIG["wobble_ref"], 2.0)
        
        badness = 0.45 * jitter_norm + 0.45 * jerk_norm + 0.10 * wobble_norm
        score = 100.0 * max(0.0, min(1.0, 1.0 - badness / 2.0))
        self.movement_quality_score = score
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since session start."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def get_time_remaining(self) -> float:
        """Get remaining time in session."""
        if not self.is_active:
            return 0.0
        remaining = self.duration - self.get_elapsed_time()
        return max(0.0, remaining)
    
    def get_final_metrics(self) -> dict:
        """Get final session metrics as dictionary."""
        return {
            "type": "FOLLOW",
            "duration_s": self.duration,
            "avg_jitter": round(self.avg_jitter, 2),
            "p95_jitter": round(self.p95_jitter, 2),
            "avg_jerk": round(self.avg_jerk, 2),
            "p95_jerk": round(self.p95_jerk, 2),
            "wobble_ratio": round(self.wobble_ratio, 3),
            "movement_quality_score": round(self.movement_quality_score, 2),
            "avg_target_error": round(self.avg_target_error, 2),
            "p95_target_error": round(self.p95_target_error, 2),
            "frames_total": self.frames_total,
            "frames_marker_found": self.frames_marker_found
        }
