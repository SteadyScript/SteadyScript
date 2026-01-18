"""
Coaching tips and feedback endpoints.

This module provides:
- Static coaching tips
- Dynamic feedback based on user performance

TODO: Implement coaching endpoints
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/tips")
async def get_tips():
    """Get general coaching tips."""
    return {
        "tips": [
            "Keep your wrist anchored on the table for stability",
            "Move slowly and deliberately between targets",
            "Take breaks if you feel fatigued",
            "Practice tracing simple shapes before complex letters",
        ]
    }


@router.get("/feedback/{session_id}")
async def get_session_feedback(session_id: str):
    """Get feedback for a specific session."""
    return {
        "session_id": session_id,
        "feedback": "Session feedback - implement based on tracking data",
    }

