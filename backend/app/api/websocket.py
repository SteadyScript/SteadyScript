"""
WebSocket endpoint for real-time bidirectional communication.
Sends tracking data and receives control commands.
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional

from .video import current_position, stability_level, get_session_manager, hsv_lower, hsv_upper
import numpy as np

router = APIRouter()

active_connections: list[WebSocket] = []


async def broadcast_tracking_data():
    """Broadcast tracking data to all connected clients."""
    sess = get_session_manager()
    
    data = {
        "type": "tracking",
        "data": {
            "position": {"x": current_position[0], "y": current_position[1]} if current_position else None,
            "marker_detected": current_position is not None,
            "stability": {
                "score": sess.get_stability_score(),
                "level": stability_level,
                "jitter": round(sess.current_jitter, 2)
            },
            "session": {
                "is_active": sess.is_active,
                "elapsed": round(sess.get_elapsed_time(), 1),
                "remaining": round(sess.get_time_remaining(), 1),
                "tremor_score": round(sess.tremor_score, 2)
            }
        }
    }
    
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception:
            pass


@router.websocket("/ws/tracking")
async def websocket_tracking(websocket: WebSocket):
    """
    WebSocket endpoint for real-time tracking data.
    
    Sends:
        - Tracking data every 100ms (position, stability, session info)
    
    Receives:
        - session_start: Start a new session
        - session_stop: Stop current session
        - hsv_update: Update HSV color range
        - calibration: Set calibration data
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    sess = get_session_manager()
    
    await websocket.send_json({
        "type": "connected",
        "data": "WebSocket connection established"
    })
    
    try:
        send_task = asyncio.create_task(send_tracking_loop(websocket))
        
        while True:
            raw_data = await websocket.receive_text()
            message = json.loads(raw_data)
            
            msg_type = message.get("type")
            
            if msg_type == "session_start":
                sess.start_session()
                await websocket.send_json({
                    "type": "session_started",
                    "data": {"duration": sess.duration}
                })
            
            elif msg_type == "session_stop":
                sess.stop_session()
                await websocket.send_json({
                    "type": "session_stopped",
                    "data": sess.get_final_metrics()
                })
            
            elif msg_type == "hsv_update":
                global hsv_lower, hsv_upper
                hsv_data = message.get("data", {})
                from .video import hsv_lower as hl, hsv_upper as hu
                import numpy as np
                hl[:] = np.array([
                    hsv_data.get("lower_h", 100),
                    hsv_data.get("lower_s", 50),
                    hsv_data.get("lower_v", 50)
                ])
                hu[:] = np.array([
                    hsv_data.get("upper_h", 130),
                    hsv_data.get("upper_s", 255),
                    hsv_data.get("upper_v", 255)
                ])
                await websocket.send_json({
                    "type": "hsv_updated",
                    "data": {"lower": hl.tolist(), "upper": hu.tolist()}
                })
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        send_task.cancel()


async def send_tracking_loop(websocket: WebSocket):
    """Send tracking data at regular intervals."""
    sess = get_session_manager()
    
    while True:
        try:
            data = {
                "type": "tracking",
                "data": {
                    "position": {"x": current_position[0], "y": current_position[1]} if current_position else None,
                    "marker_detected": current_position is not None,
                    "stability": {
                        "score": sess.get_stability_score(),
                        "level": sess.get_stability_level() if current_position else "unknown",
                        "jitter": round(sess.current_jitter, 2)
                    },
                    "session": {
                        "is_active": sess.is_active,
                        "elapsed": round(sess.get_elapsed_time(), 1),
                        "remaining": round(sess.get_time_remaining(), 1),
                        "tremor_score": round(sess.tremor_score, 2)
                    }
                }
            }
            await websocket.send_json(data)
            await asyncio.sleep(0.1)
        except Exception:
            break
