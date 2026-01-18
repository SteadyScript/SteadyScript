"""
Video streaming endpoint for SteadyScript.
Provides MJPEG stream of processed camera feed.
"""

import cv2
import numpy as np
from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from typing import Generator, Optional, Tuple

from ..compvis import detect_marker, draw_marker_overlay, DEFAULT_HSV_LOWER, DEFAULT_HSV_UPPER
from ..compvis.session import SessionManager

router = APIRouter()

camera: Optional[cv2.VideoCapture] = None
session_manager: Optional[SessionManager] = None
hsv_lower = DEFAULT_HSV_LOWER.copy()
hsv_upper = DEFAULT_HSV_UPPER.copy()
current_position: Optional[Tuple[int, int]] = None
stability_level: str = "stable"


def get_camera() -> cv2.VideoCapture:
    """Get or initialize the camera."""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera


def get_session_manager() -> SessionManager:
    """Get or initialize the session manager."""
    global session_manager
    if session_manager is None:
        session_manager = SessionManager()
    return session_manager


def generate_frames() -> Generator[bytes, None, None]:
    """
    Generate MJPEG frames from camera.
    Yields JPEG frames with marker overlay.
    """
    global current_position, stability_level
    
    cap = get_camera()
    sess = get_session_manager()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame = cv2.flip(frame, 1)
        
        position = detect_marker(frame, hsv_lower, hsv_upper)
        current_position = position
        
        if sess.is_active and position:
            sess.update(position, None, 0)
            stability_level = sess.get_stability_level()
        elif position:
            stability_level = "stable"
        
        frame = draw_marker_overlay(frame, position, stability_level)
        
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame_bytes = buffer.tobytes()
        
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )


@router.get("/video_feed")
async def video_feed():
    """
    MJPEG video stream endpoint.
    Returns continuous stream of JPEG frames.
    """
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/tracking_data")
async def get_tracking_data():
    """
    Get current tracking data (for polling fallback).
    """
    sess = get_session_manager()
    
    return {
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
            "remaining": round(sess.get_time_remaining(), 1)
        }
    }


@router.post("/hsv")
async def update_hsv(lower_h: int, lower_s: int, lower_v: int,
                     upper_h: int, upper_s: int, upper_v: int):
    """Update HSV color range for marker detection."""
    global hsv_lower, hsv_upper
    hsv_lower = np.array([lower_h, lower_s, lower_v])
    hsv_upper = np.array([upper_h, upper_s, upper_v])
    return {"status": "updated", "lower": hsv_lower.tolist(), "upper": hsv_upper.tolist()}


@router.post("/session/start")
async def start_session():
    """Start a new tracking session."""
    sess = get_session_manager()
    sess.start_session()
    return {"status": "started"}


@router.post("/session/stop")
async def stop_session():
    """Stop the current session."""
    sess = get_session_manager()
    sess.stop_session()
    return {"status": "stopped", "metrics": sess.get_final_metrics()}

