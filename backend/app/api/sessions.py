"""
Sessions API - Retrieve session history from CompVis data.
"""

import os
import json
from typing import List, Optional
from fastapi import APIRouter, Query

router = APIRouter()

# Path to sessions file
SESSIONS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "CompVis", "data", "sessions.json"
)


def load_sessions() -> List[dict]:
    """Load sessions from the JSON file."""
    if not os.path.exists(SESSIONS_FILE):
        return []
    try:
        with open(SESSIONS_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


@router.get("/api/sessions")
async def get_sessions(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of sessions to return"),
    session_type: Optional[str] = Query(None, description="Filter by session type (HOLD or FOLLOW)")
):
    """
    Get session history.

    Returns sessions sorted by timestamp (most recent first).
    """
    sessions = load_sessions()

    # Filter by type if specified
    if session_type:
        sessions = [s for s in sessions if s.get("type", "").upper() == session_type.upper()]

    # Sort by timestamp (most recent first)
    sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Limit results
    sessions = sessions[:limit]

    return {
        "sessions": sessions,
        "total": len(sessions),
    }


@router.get("/api/sessions/stats")
async def get_session_stats():
    """
    Get aggregate statistics from session history.

    Returns:
    - Total session count
    - Average tremor score (last 5 vs previous 5)
    - Trend indicator
    """
    sessions = load_sessions()

    if not sessions:
        return {
            "total_sessions": 0,
            "hold_sessions": 0,
            "follow_sessions": 0,
            "avg_score_recent": 0,
            "avg_score_previous": 0,
            "trend": "stable",
            "trend_percent": 0,
        }

    # Sort by timestamp
    sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    hold_sessions = [s for s in sessions if s.get("type") == "HOLD"]
    follow_sessions = [s for s in sessions if s.get("type") == "FOLLOW"]

    # Calculate trend from recent vs previous sessions
    recent_5 = sessions[:5]
    previous_5 = sessions[5:10] if len(sessions) > 5 else []

    def avg_score(session_list):
        scores = [s.get("tremor_score", 0) for s in session_list if s.get("tremor_score") is not None]
        return sum(scores) / len(scores) if scores else 0

    avg_recent = avg_score(recent_5)
    avg_previous = avg_score(previous_5) if previous_5 else avg_recent

    # Calculate trend
    if avg_previous > 0:
        trend_percent = ((avg_recent - avg_previous) / avg_previous) * 100
    else:
        trend_percent = 0

    if trend_percent > 5:
        trend = "improving"
    elif trend_percent < -5:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "total_sessions": len(sessions),
        "hold_sessions": len(hold_sessions),
        "follow_sessions": len(follow_sessions),
        "avg_score_recent": round(avg_recent, 1),
        "avg_score_previous": round(avg_previous, 1),
        "trend": trend,
        "trend_percent": round(trend_percent, 1),
    }
