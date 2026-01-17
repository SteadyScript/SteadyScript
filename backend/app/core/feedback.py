"""
Feedback message generation.

This module handles:
- Generating contextual feedback based on stability
- Providing encouragement and tips
- Tracking session progress

TODO: Expand feedback messages and add session tracking
"""

from typing import Optional


def get_feedback_message(stability_level: str, jitter: float) -> str:
    """
    Generate feedback message based on current stability.
    
    Args:
        stability_level: "stable", "warning", or "unstable"
        jitter: Current jitter value
    
    Returns:
        Feedback message string
    """
    messages = {
        "stable": [
            "Excellent! Your hand is very steady.",
            "Great control! Keep it up.",
            "Perfect stability. Try moving to the next target.",
        ],
        "warning": [
            "Good, but try to steady your hand a bit more.",
            "Almost there! Slow down slightly.",
            "Take a breath and relax your grip.",
        ],
        "unstable": [
            "Try anchoring your wrist on the table.",
            "Slow down and focus on control.",
            "Take a short break if needed.",
        ],
    }
    
    level_messages = messages.get(stability_level, messages["warning"])
    index = int(jitter) % len(level_messages)
    
    return level_messages[index]


def get_session_summary(
    avg_stability: float,
    total_time: float,
    targets_hit: int,
    total_targets: int,
) -> dict:
    """
    Generate session summary.
    
    TODO: Implement based on actual session tracking
    """
    return {
        "average_stability": round(avg_stability, 1),
        "duration_seconds": round(total_time, 1),
        "accuracy": round(targets_hit / max(total_targets, 1) * 100, 1),
        "targets_completed": targets_hit,
        "total_targets": total_targets,
        "feedback": "Session complete! Review your results above.",
    }

