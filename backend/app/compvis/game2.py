#!/usr/bin/env python3
"""
SteadyScript Game2 - Standalone OpenCV App

Modes:
- HOLD: keep marker steady inside a circle
- FOLLOW: move between A/B targets on a metronome beat

Controls:
  1 - HOLD mode
  2 - FOLLOW mode
  SPACE - Start/Stop session
  UP/DOWN - BPM +/- 5
  T - Toggle HSV trackbars
  M - Toggle mask debug
  Q - Quit
"""

import os
import time
import json
import math
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, List, Dict
from collections import deque
from datetime import datetime, timezone

import cv2
import numpy as np

# ===============================
# CONFIG
# ===============================

CONFIG = {
    "camera_id": 0,
    "frame_width": 640,
    "frame_height": 480,

    # HSV defaults (blue marker)
    "hsv_lower": [100, 50, 50],
    "hsv_upper": [130, 255, 255],

    "min_contour_area": 100,

    # HOLD mode
    "hold_duration": 10.0,
    "default_circle_radius": 80,

    # FOLLOW mode
    "follow_duration": 30.0,
    "default_bpm": 60,
    "target_size": 60,
    "target_margin": 80,
    "path_tolerance": 50,

    # Jitter algorithm (same as Mode 1)
    "smoothing_window": 10,
    "jitter_stable_threshold": 5.0,
    "jitter_warning_threshold": 15.0,
    "jitter_max_threshold": 30.0,

    # Lateral jitter thresholds (Mode 2 - only measures perpendicular wobble)
    "lateral_jitter_stable_threshold": 3.0,
    "lateral_jitter_warning_threshold": 8.0,
    "lateral_jitter_max_threshold": 20.0,
    "direction_window": 5,  # frames to compute movement direction

    # Scoring weights
    "jitter_weight": 0.5,
    "path_weight": 0.5,

    # Data
    "sessions_file": os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "CompVis", "data", "sessions.json"
    ),
}

# ===============================
# AUDIO (Metronome)
# ===============================


def play_beep():
    try:
        # macOS system beep
        os.system('afplay /System/Library/Sounds/Tink.aiff &')
    except Exception:
        pass


class Metronome:
    def __init__(self, bpm: int = 60):
        self.bpm = bpm
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_beat_time = 0.0
        self.beat_count = 0

    def set_bpm(self, bpm: int):
        self.bpm = max(20, min(200, bpm))

    def start(self):
        if self.running:
            return
        self.running = True
        self.beat_count = 0
        self.last_beat_time = time.time()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
            self.thread = None

    def _run(self):
        interval = 60.0 / self.bpm
        next_beat = time.time()
        while self.running:
            now = time.time()
            if now >= next_beat:
                play_beep()
                self.beat_count += 1
                self.last_beat_time = now
                next_beat += interval
            time.sleep(0.01)

    def get_beat_count(self) -> int:
        return self.beat_count

# ===============================
# UTILS
# ===============================


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def compute_percentile(values: List[float], percentile: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    index = (percentile / 100.0) * (len(sorted_vals) - 1)
    if index.is_integer():
        return sorted_vals[int(index)]
    lower = sorted_vals[int(index)]
    upper = sorted_vals[min(int(index) + 1, len(sorted_vals) - 1)]
    return lower + (upper - lower) * (index - int(index))


def point_in_rect(point: Tuple[float, float], rect_center: Tuple[int, int], size: int) -> bool:
    half = size // 2
    return (rect_center[0] - half <= point[0] <= rect_center[0] + half and
            rect_center[1] - half <= point[1] <= rect_center[1] + half)


def point_in_circle(point: Tuple[float, float], center: Tuple[float, float], radius: float) -> bool:
    return distance(point, center) <= radius


def point_to_line_distance(point: Tuple[float, float], line_start: Tuple[float, float], line_end: Tuple[float, float]) -> float:
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end
    line_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
    if line_len_sq == 0:
        return distance(point, line_start)
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = math.sqrt(line_len_sq)
    return numerator / denominator

# ===============================
# DETECTION
# ===============================


def detect_marker(frame: np.ndarray, hsv_lower: np.ndarray, hsv_upper: np.ndarray) -> Optional[Tuple[int, int]]:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < CONFIG["min_contour_area"]:
        return None

    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)


def get_mask(frame: np.ndarray, hsv_lower: np.ndarray, hsv_upper: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask

# ===============================
# ENUMS / DATA
# ===============================

class AppMode(Enum):
    HOLD = "HOLD"
    FOLLOW = "FOLLOW"


class SessionState(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"


@dataclass
class FrameSample:
    position: Tuple[float, float]
    timestamp: float

# ===============================
# A/B TARGETS
# ===============================

class ABTargets:
    def __init__(self, frame_width: int, frame_height: int):
        margin = CONFIG["target_margin"]
        size = CONFIG["target_size"]
        self.target_a = (margin + size // 2, frame_height // 2)
        self.target_b = (frame_width - margin - size // 2, frame_height // 2)
        self.size = size
        self.current_target = 'A'

    def switch_target(self):
        self.current_target = 'B' if self.current_target == 'A' else 'A'

    def is_in_target(self, position: Tuple[float, float], target: str) -> bool:
        center = self.target_a if target == 'A' else self.target_b
        return point_in_rect(position, center, self.size)

    def get_path_deviation(self, position: Tuple[float, float]) -> float:
        return point_to_line_distance(position, self.target_a, self.target_b)

# ===============================
# JITTER TRACKER (Mode 1 algorithm)
# ===============================

"""
Jitter algorithm:
- Maintain a rolling window of the last N positions (smoothing_window)
- Compute smoothed position = average of those N positions
- Jitter = distance(current_position, smoothed_position)
This measures deviation from the recent trend; larger deviation = more tremor.
"""

class JitterTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.positions: deque = deque(maxlen=300)
        self.jitter_values: List[float] = []
        self.lateral_jitter_values: List[float] = []
        self.rolling_jitter: deque = deque(maxlen=30)
        self.rolling_lateral_jitter: deque = deque(maxlen=30)
        self.current_jitter = 0.0
        self.current_lateral_jitter = 0.0
        self.avg_jitter = 0.0
        self.avg_lateral_jitter = 0.0
        self.p95_jitter = 0.0
        self.p95_lateral_jitter = 0.0
        self.frames_total = 0
        self.frames_marker_found = 0

    def _compute_movement_direction(self) -> Optional[Tuple[float, float]]:
        """Compute normalized movement direction from recent positions."""
        dir_window = CONFIG["direction_window"]
        if len(self.positions) < dir_window:
            return None
        
        recent = list(self.positions)[-dir_window:]
        # Direction = from oldest to newest position in window
        dx = recent[-1][0] - recent[0][0]
        dy = recent[-1][1] - recent[0][1]
        magnitude = math.sqrt(dx * dx + dy * dy)
        
        if magnitude < 1.0:  # Nearly stationary, no clear direction
            return None
        
        return (dx / magnitude, dy / magnitude)

    def _compute_lateral_jitter(self, position: Tuple[int, int], smoothed: Tuple[float, float]) -> float:
        """Compute lateral (perpendicular) jitter - ignores forward movement."""
        direction = self._compute_movement_direction()
        
        if direction is None:
            # No clear movement direction, fall back to regular jitter
            return distance(position, smoothed)
        
        # Deviation vector from smoothed position to current position
        dev_x = position[0] - smoothed[0]
        dev_y = position[1] - smoothed[1]
        
        # Project deviation onto movement direction (forward component)
        forward_component = dev_x * direction[0] + dev_y * direction[1]
        
        # Lateral component = deviation - forward component along direction
        lateral_x = dev_x - forward_component * direction[0]
        lateral_y = dev_y - forward_component * direction[1]
        
        # Lateral jitter = magnitude of lateral component
        lateral_jitter = math.sqrt(lateral_x * lateral_x + lateral_y * lateral_y)
        return lateral_jitter

    def update(self, position: Optional[Tuple[int, int]]) -> float:
        self.frames_total += 1
        if position is None:
            return self.current_jitter
        self.frames_marker_found += 1
        self.positions.append(position)

        window = CONFIG["smoothing_window"]
        if len(self.positions) < window:
            return 0.0

        recent = list(self.positions)[-window:]
        avg_x = sum(p[0] for p in recent) / len(recent)
        avg_y = sum(p[1] for p in recent) / len(recent)
        smoothed = (avg_x, avg_y)

        # Regular jitter (total deviation)
        jitter = distance(position, smoothed)
        self.current_jitter = jitter
        self.jitter_values.append(jitter)
        self.rolling_jitter.append(jitter)

        # Lateral jitter (perpendicular wobble only)
        lateral_jitter = self._compute_lateral_jitter(position, smoothed)
        self.current_lateral_jitter = lateral_jitter
        self.lateral_jitter_values.append(lateral_jitter)
        self.rolling_lateral_jitter.append(lateral_jitter)

        if self.rolling_jitter:
            vals = list(self.rolling_jitter)
            self.avg_jitter = sum(vals) / len(vals)
            self.p95_jitter = compute_percentile(vals, 95.0)

        if self.rolling_lateral_jitter:
            vals = list(self.rolling_lateral_jitter)
            self.avg_lateral_jitter = sum(vals) / len(vals)
            self.p95_lateral_jitter = compute_percentile(vals, 95.0)

        return jitter

    def get_jitter_score(self) -> float:
        if not self.jitter_values:
            return 100.0
        p95 = compute_percentile(self.jitter_values, 95.0)
        if p95 <= CONFIG["jitter_stable_threshold"]:
            return 100.0
        if p95 >= CONFIG["jitter_max_threshold"]:
            return 0.0
        range_val = CONFIG["jitter_max_threshold"] - CONFIG["jitter_stable_threshold"]
        normalized = (p95 - CONFIG["jitter_stable_threshold"]) / range_val
        return 100.0 * (1.0 - normalized)

    def get_lateral_jitter_score(self) -> float:
        """Score based on lateral jitter only - for Mode 2 (movement)."""
        if not self.lateral_jitter_values:
            return 100.0
        p95 = compute_percentile(self.lateral_jitter_values, 95.0)
        if p95 <= CONFIG["lateral_jitter_stable_threshold"]:
            return 100.0
        if p95 >= CONFIG["lateral_jitter_max_threshold"]:
            return 0.0
        range_val = CONFIG["lateral_jitter_max_threshold"] - CONFIG["lateral_jitter_stable_threshold"]
        normalized = (p95 - CONFIG["lateral_jitter_stable_threshold"]) / range_val
        return 100.0 * (1.0 - normalized)

    def get_lateral_stability_level(self) -> str:
        """Stability level based on lateral jitter."""
        if self.current_lateral_jitter <= CONFIG["lateral_jitter_stable_threshold"]:
            return "stable"
        if self.current_lateral_jitter <= CONFIG["lateral_jitter_warning_threshold"]:
            return "warning"
        return "unstable"

    def get_stability_level(self) -> str:
        if self.current_jitter <= CONFIG["jitter_stable_threshold"]:
            return "stable"
        if self.current_jitter <= CONFIG["jitter_warning_threshold"]:
            return "warning"
        return "unstable"

    def get_summary(self) -> Dict:
        return {
            "avg_jitter": round(self.avg_jitter, 2),
            "p95_jitter": round(self.p95_jitter, 2),
            "max_jitter": round(max(self.jitter_values) if self.jitter_values else 0, 2),
            "jitter_score": round(self.get_jitter_score(), 1),
            "avg_lateral_jitter": round(self.avg_lateral_jitter, 2),
            "p95_lateral_jitter": round(self.p95_lateral_jitter, 2),
            "max_lateral_jitter": round(max(self.lateral_jitter_values) if self.lateral_jitter_values else 0, 2),
            "lateral_jitter_score": round(self.get_lateral_jitter_score(), 1),
            "frames_total": self.frames_total,
            "frames_marker_found": self.frames_marker_found,
        }

# ===============================
# METRICS
# ===============================

class HoldMetrics:
    def __init__(self):
        self.jitter_tracker = JitterTracker()
        self.reset()

    def reset(self):
        self.jitter_tracker.reset()
        self.frames_total = 0

    def update(self, position: Optional[Tuple[int, int]]):
        self.frames_total += 1
        self.jitter_tracker.update(position)

    def get_stability_score(self) -> int:
        return int(self.jitter_tracker.get_jitter_score())

    def get_summary(self) -> Dict:
        jitter_summary = self.jitter_tracker.get_summary()
        return {
            "tremor_score": round(self.jitter_tracker.get_jitter_score(), 1),
            "avg_jitter": jitter_summary["avg_jitter"],
            "p95_jitter": jitter_summary["p95_jitter"],
            "frames_total": self.frames_total,
            "frames_marker_found": jitter_summary["frames_marker_found"],
        }


class FollowMetrics:
    def __init__(self):
        self.jitter_tracker = JitterTracker()
        self.reset()

    def reset(self):
        self.jitter_tracker.reset()
        self.positions: List[Tuple[int, int]] = []
        self.frames_total = 0
        self.last_beat_count = 0

    def update(self, position: Optional[Tuple[int, int]], beat_count: int):
        self.frames_total += 1
        self.jitter_tracker.update(position)
        if position is None:
            return
        self.positions.append(position)
        self.last_beat_count = beat_count

    def get_combined_score(self) -> float:
        # 100% lateral jitter-based scoring (ignores forward movement)
        return self.jitter_tracker.get_lateral_jitter_score()

    def get_feedback_status(self) -> str:
        # Use lateral jitter for feedback during movement
        if self.jitter_tracker.current_lateral_jitter <= CONFIG["lateral_jitter_stable_threshold"]:
            return "good"
        if self.jitter_tracker.current_lateral_jitter <= CONFIG["lateral_jitter_warning_threshold"]:
            return "warning"
        return "poor"

    def get_summary(self) -> Dict:
        jitter_summary = self.jitter_tracker.get_summary()
        return {
            "tremor_score": round(self.get_combined_score(), 1),
            "avg_lateral_jitter": jitter_summary["avg_lateral_jitter"],
            "p95_lateral_jitter": jitter_summary["p95_lateral_jitter"],
            "max_lateral_jitter": jitter_summary["max_lateral_jitter"],
            "avg_jitter_total": jitter_summary["avg_jitter"],
            "beats_total": self.last_beat_count,
            "frames_total": self.frames_total,
            "frames_marker_found": jitter_summary["frames_marker_found"],
        }

# ===============================
# SESSION IO
# ===============================


def load_sessions() -> List[Dict]:
    filepath = CONFIG["sessions_file"]
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_session(session_data: Dict):
    filepath = CONFIG["sessions_file"]
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    sessions = load_sessions()
    sessions.append(session_data)
    with open(filepath, 'w') as f:
        json.dump(sessions, f, indent=2)
    print(f"\n[LOG] Session saved to {filepath}")

# ===============================
# UI DRAWING
# ===============================


def draw_mode_header(frame: np.ndarray, mode: AppMode, state: SessionState,
                     time_remaining: float = 0.0, bpm: int = 60) -> np.ndarray:
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 70), (40, 40, 40), -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

    mode_color = (0, 255, 255) if mode == AppMode.HOLD else (255, 165, 0)
    cv2.putText(frame, f"Mode: {mode.value}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)

    if mode == AppMode.FOLLOW:
        cv2.putText(frame, f"BPM: {bpm}", (150, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

    if state == SessionState.RUNNING:
        cv2.putText(frame, f"RUNNING - {time_remaining:.1f}s", (280, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    elif state == SessionState.COMPLETE:
        cv2.putText(frame, "SESSION COMPLETE!", (280, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    if state != SessionState.RUNNING:
        cv2.putText(frame, "[1] HOLD  [2] FOLLOW  [SPACE] Start  [UP/DN] BPM  [Q] Quit",
                    (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
    else:
        cv2.putText(frame, "[SPACE] Stop Session", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

    return frame


def draw_hold_mode(frame: np.ndarray, pen_pos: Optional[Tuple[int, int]],
                   metrics: HoldMetrics, state: SessionState) -> np.ndarray:
    h, w = frame.shape[:2]

    if pen_pos:
        level = metrics.jitter_tracker.get_stability_level()
        colors = {"stable": (0, 255, 0), "warning": (0, 255, 255), "unstable": (0, 0, 255)}
        color = colors.get(level, (0, 255, 0))
        cv2.circle(frame, pen_pos, 20, color, 2)
        cv2.circle(frame, pen_pos, 5, color, -1)

    if state == SessionState.RUNNING:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 80), (250, h), (30, 30, 30), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)

        level = metrics.jitter_tracker.get_stability_level()
        colors = {"stable": (0, 255, 0), "warning": (0, 255, 255), "unstable": (0, 0, 255)}
        color = colors.get(level, (200, 200, 200))

        y = h - 60
        cv2.putText(frame, f"Jitter: {metrics.jitter_tracker.current_jitter:.1f} px", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20
        cv2.putText(frame, f"Score: {metrics.get_stability_score()}", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20
        cv2.putText(frame, f"Status: {level.upper()}", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    else:
        cv2.putText(frame, "Hold marker steady - Press SPACE to start", (w // 2 - 180, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

    return frame


def draw_follow_mode(frame: np.ndarray, pen_pos: Optional[Tuple[int, int]],
                     metrics: FollowMetrics,
                     state: SessionState, beat_count: int) -> np.ndarray:
    h, w = frame.shape[:2]

    if state == SessionState.RUNNING:
        # Draw the trail with lateral jitter-based coloring
        if len(metrics.positions) > 1:
            for i in range(1, len(metrics.positions)):
                pt1 = metrics.positions[i - 1]
                pt2 = metrics.positions[i]
                idx = i - 1
                if idx < len(metrics.jitter_tracker.lateral_jitter_values):
                    lateral_jitter = metrics.jitter_tracker.lateral_jitter_values[idx]
                    if lateral_jitter <= CONFIG["lateral_jitter_stable_threshold"]:
                        color = (0, 255, 0)  # Green = smooth
                    elif lateral_jitter <= CONFIG["lateral_jitter_warning_threshold"]:
                        color = (0, 255, 255)  # Yellow = warning
                    else:
                        color = (0, 0, 255)  # Red = shaky
                else:
                    color = (0, 255, 0)
                cv2.line(frame, pt1, pt2, color, 2)

        # Draw current pen position
        if pen_pos:
            status = metrics.get_feedback_status()
            pen_colors = {"good": (0, 255, 0), "warning": (0, 255, 255), "poor": (0, 0, 255)}
            pen_color = pen_colors.get(status, (0, 255, 0))
            cv2.circle(frame, pen_pos, 12, pen_color, 3)
            cv2.circle(frame, pen_pos, 4, pen_color, -1)

        # Metrics panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 120), (250, h), (30, 30, 30), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)

        status = metrics.get_feedback_status()
        status_colors = {"good": (0, 255, 0), "warning": (0, 255, 255), "poor": (0, 0, 255)}
        status_color = status_colors.get(status, (200, 200, 200))

        y = h - 100
        cv2.putText(frame, f"Lateral Jitter: {metrics.jitter_tracker.current_lateral_jitter:.1f} px", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20
        cv2.putText(frame, f"Avg Lateral: {metrics.jitter_tracker.avg_lateral_jitter:.1f} px", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20
        cv2.putText(frame, f"Beat: {beat_count}", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20
        cv2.putText(frame, f"Status: {status.upper()}", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        y += 25
        cv2.putText(frame, f"Score: {metrics.get_combined_score():.0f}/100", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Instructions
        cv2.putText(frame, "Draw smoothly to the metronome beat!", (w // 2 - 180, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    else:
        if pen_pos:
            cv2.circle(frame, pen_pos, 15, (0, 255, 0), 2)
            cv2.circle(frame, pen_pos, 4, (0, 255, 0), -1)

        cv2.putText(frame, "Press SPACE to start smooth drawing", (w // 2 - 180, h // 2 - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        cv2.putText(frame, "Draw lines smoothly with the metronome", (w // 2 - 200, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        cv2.putText(frame, "Green = smooth, Red = shaky", (w // 2 - 140, h // 2 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        cv2.putText(frame, "Use UP/DOWN arrows to adjust BPM", (w // 2 - 170, h // 2 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

    return frame


def draw_results(frame: np.ndarray, mode: AppMode, metrics_summary: Dict) -> np.ndarray:
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (w // 2 - 200, h // 2 - 150), (w // 2 + 200, h // 2 + 150), (40, 40, 40), -1)
    frame = cv2.addWeighted(overlay, 0.9, frame, 0.1, 0)

    title = "HOLD Results" if mode == AppMode.HOLD else "FOLLOW Results"
    cv2.putText(frame, title, (w // 2 - 80, h // 2 - 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    y = h // 2 - 80
    score = metrics_summary.get('tremor_score', 0)
    score_color = (0, 255, 0) if score >= 70 else (0, 255, 255) if score >= 40 else (0, 0, 255)
    cv2.putText(frame, f"Tremor Score: {score:.0f}/100", (w // 2 - 110, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, score_color, 2)
    y += 35

    if mode == AppMode.HOLD:
        items = [
            f"Avg Jitter: {metrics_summary.get('avg_jitter', 0):.1f} px",
            f"P95 Jitter: {metrics_summary.get('p95_jitter', 0):.1f} px",
            f"Detection: {metrics_summary.get('frames_marker_found', 0)}/{metrics_summary.get('frames_total', 0)}",
        ]
    else:
        items = [
            f"Avg Lateral Jitter: {metrics_summary.get('avg_lateral_jitter', 0):.1f} px",
            f"P95 Lateral Jitter: {metrics_summary.get('p95_lateral_jitter', 0):.1f} px",
            f"Max Lateral Jitter: {metrics_summary.get('max_lateral_jitter', 0):.1f} px",
            f"Beats: {metrics_summary.get('beats_total', 0)}",
            f"Detection: {metrics_summary.get('frames_marker_found', 0)}/{metrics_summary.get('frames_total', 0)}",
        ]

    for item in items:
        cv2.putText(frame, item, (w // 2 - 150, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 22

    cv2.putText(frame, "Press SPACE to continue", (w // 2 - 100, h // 2 + 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

    return frame

# ===============================
# HSV TRACKBARS
# ===============================


def nothing(x):
    pass


def create_hsv_trackbars(window_name: str = "HSV Tuning"):
    cv2.namedWindow(window_name)
    cv2.createTrackbar("H Lower", window_name, CONFIG["hsv_lower"][0], 179, nothing)
    cv2.createTrackbar("S Lower", window_name, CONFIG["hsv_lower"][1], 255, nothing)
    cv2.createTrackbar("V Lower", window_name, CONFIG["hsv_lower"][2], 255, nothing)
    cv2.createTrackbar("H Upper", window_name, CONFIG["hsv_upper"][0], 179, nothing)
    cv2.createTrackbar("S Upper", window_name, CONFIG["hsv_upper"][1], 255, nothing)
    cv2.createTrackbar("V Upper", window_name, CONFIG["hsv_upper"][2], 255, nothing)


def get_hsv_from_trackbars(window_name: str = "HSV Tuning") -> Tuple[np.ndarray, np.ndarray]:
    h_lower = cv2.getTrackbarPos("H Lower", window_name)
    s_lower = cv2.getTrackbarPos("S Lower", window_name)
    v_lower = cv2.getTrackbarPos("V Lower", window_name)
    h_upper = cv2.getTrackbarPos("H Upper", window_name)
    s_upper = cv2.getTrackbarPos("S Upper", window_name)
    v_upper = cv2.getTrackbarPos("V Upper", window_name)
    return (np.array([h_lower, s_lower, v_lower]), np.array([h_upper, s_upper, v_upper]))

# ===============================
# CALIBRATION
# ===============================

class CalibrationState:
    def __init__(self):
        self.center: Optional[Tuple[int, int]] = None
        self.radius: float = CONFIG["default_circle_radius"]
        self.click_count: int = 0

    def reset(self):
        self.center = None
        self.radius = CONFIG["default_circle_radius"]
        self.click_count = 0

    def handle_click(self, x: int, y: int):
        if self.click_count == 0:
            self.center = (x, y)
            self.click_count = 1
            print(f"[CALIBRATION] Center set to ({x}, {y}). Click again for edge.")
        elif self.click_count == 1:
            if self.center:
                self.radius = distance(self.center, (x, y))
                self.click_count = 2
                print(f"[CALIBRATION] Radius set to {self.radius:.1f} px. Calibration complete.")


calibration_state = CalibrationState()


def mouse_callback(event, x, y, flags, param):
    global calibration_state
    if event == cv2.EVENT_LBUTTONDOWN:
        mode = param.get("mode", AppMode.HOLD)
        state = param.get("state", SessionState.IDLE)
        if mode == AppMode.HOLD and state != SessionState.RUNNING:
            calibration_state.handle_click(x, y)

# ===============================
# MAIN
# ===============================


def main():
    global calibration_state

    print("\n" + "=" * 60)
    print("  SteadyScript Game2 - Training Application")
    print("=" * 60)
    print("\nJITTER ALGORITHM:")
    print("  Mode 1 (HOLD): Total jitter = deviation from smoothed position")
    print("  Mode 2 (FOLLOW): Lateral jitter = perpendicular wobble only")
    print("    - Computes movement direction from recent frames")
    print("    - Only measures sideways tremor, ignores forward motion")
    print("  Lower jitter = more stable = higher score")
    print("=" * 60 + "\n")

    cap = cv2.VideoCapture(CONFIG["camera_id"])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CONFIG["frame_width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG["frame_height"])

    if not cap.isOpened():
        print("ERROR: Could not open camera")
        return

    # Wait for camera to warm up and verify it's working
    print("Initializing camera...")
    for _ in range(30):  # Try up to 30 frames (~1 second)
        ret, frame = cap.read()
        if ret and frame is not None:
            break
        time.sleep(0.05)
    else:
        print("ERROR: Camera failed to produce frames")
        cap.release()
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera ready: {frame_width}x{frame_height}")

    hsv_lower = np.array(CONFIG["hsv_lower"])
    hsv_upper = np.array(CONFIG["hsv_upper"])

    hold_metrics = HoldMetrics()
    follow_metrics = FollowMetrics()
    metronome = Metronome(CONFIG["default_bpm"])

    current_mode = AppMode.HOLD
    session_state = SessionState.IDLE
    session_start_time = 0.0
    last_results: Optional[Dict] = None
    current_bpm = CONFIG["default_bpm"]

    show_hsv_trackbars = False
    show_mask = False
    hsv_window_created = False

    window_name = "SteadyScript Game2"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback, {"mode": current_mode, "state": session_state})

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            # Try to recover by re-reading
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)

        if show_hsv_trackbars and hsv_window_created:
            hsv_lower, hsv_upper = get_hsv_from_trackbars()

        pen_pos = detect_marker(frame, hsv_lower, hsv_upper)

        cv2.setMouseCallback(window_name, mouse_callback, {"mode": current_mode, "state": session_state})

        elapsed_time = 0.0
        time_remaining = 0.0
        beat_count = 0

        if session_state == SessionState.RUNNING:
            elapsed_time = time.time() - session_start_time
            duration = CONFIG["hold_duration"] if current_mode == AppMode.HOLD else CONFIG["follow_duration"]
            time_remaining = max(0.0, duration - elapsed_time)

            if current_mode == AppMode.FOLLOW:
                beat_count = metronome.get_beat_count()

            if elapsed_time >= duration:
                session_state = SessionState.COMPLETE
                if current_mode == AppMode.FOLLOW:
                    metronome.stop()

                if current_mode == AppMode.HOLD:
                    last_results = hold_metrics.get_summary()
                    session_data = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "HOLD",
                        "duration_s": CONFIG["hold_duration"],
                        **last_results,
                    }
                else:
                    last_results = follow_metrics.get_summary()
                    session_data = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "FOLLOW",
                        "duration_s": CONFIG["follow_duration"],
                        "bpm": current_bpm,
                        **last_results,
                    }

                save_session(session_data)

        if session_state == SessionState.RUNNING:
            if current_mode == AppMode.HOLD:
                hold_metrics.update(pen_pos)
            else:
                follow_metrics.update(pen_pos, beat_count)

        frame = draw_mode_header(frame, current_mode, session_state, time_remaining, current_bpm)

        if session_state == SessionState.COMPLETE and last_results:
            frame = draw_results(frame, current_mode, last_results)
        elif current_mode == AppMode.HOLD:
            frame = draw_hold_mode(frame, pen_pos, hold_metrics, session_state)
        else:
            frame = draw_follow_mode(frame, pen_pos, follow_metrics, session_state, beat_count)

        cv2.imshow(window_name, frame)

        if show_mask:
            mask = get_mask(frame, hsv_lower, hsv_upper)
            cv2.imshow("Mask Debug", mask)
        else:
            try:
                cv2.destroyWindow("Mask Debug")
            except cv2.error:
                pass

        key = cv2.waitKey(1) & 0xFF

        if key in (ord('q'), ord('Q')):
            metronome.stop()
            break

        elif key == ord('1'):
            if session_state != SessionState.RUNNING:
                current_mode = AppMode.HOLD
                session_state = SessionState.IDLE
                last_results = None

        elif key == ord('2'):
            if session_state != SessionState.RUNNING:
                current_mode = AppMode.FOLLOW
                session_state = SessionState.IDLE
                last_results = None

        elif key == ord(' '):
            if session_state == SessionState.IDLE:
                session_state = SessionState.RUNNING
                session_start_time = time.time()
                last_results = None

                if current_mode == AppMode.HOLD:
                    hold_metrics.reset()
                else:
                    follow_metrics.reset()
                    metronome.set_bpm(current_bpm)
                    metronome.start()

            elif session_state == SessionState.RUNNING:
                session_state = SessionState.IDLE
                metronome.stop()

            elif session_state == SessionState.COMPLETE:
                session_state = SessionState.IDLE
                last_results = None

        elif key in (82, 0):  # UP
            if session_state != SessionState.RUNNING:
                current_bpm = min(200, current_bpm + 5)

        elif key in (84, 1):  # DOWN
            if session_state != SessionState.RUNNING:
                current_bpm = max(20, current_bpm - 5)

        elif key in (ord('t'), ord('T')):
            show_hsv_trackbars = not show_hsv_trackbars
            if show_hsv_trackbars and not hsv_window_created:
                create_hsv_trackbars()
                hsv_window_created = True
            elif not show_hsv_trackbars:
                cv2.destroyWindow("HSV Tuning")
                hsv_window_created = False

        elif key in (ord('m'), ord('M')):
            show_mask = not show_mask

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
