"""
WebSocket endpoint for real-time pen tracking.

This module handles:
- WebSocket connections from the frontend
- Receiving base64-encoded video frames
- Sending back tracking data (position, stability, feedback)

TODO: Implement the WebSocket endpoint
"""

from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time tracking.
    
    Expected input: Base64 encoded video frames
    Output: JSON with position, stability score, and feedback
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "tracking",
                "data": {
                    "position": {"x": 0, "y": 0},
                    "stability": {"score": 0, "level": "stable", "jitter": 0},
                    "feedback": "Placeholder - implement tracking logic",
                    "timestamp": 0,
                }
            })
    except Exception:
        pass

