"""
WebSocket endpoint for Game2 video streaming and control.
Streams processed frames from game2.py logic to frontend.
"""

import asyncio
import json
import base64
import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional, Dict, Any
import threading
import time

from ..compvis.game2 import (
    AppMode, SessionState, HoldMetrics, FollowMetrics,
    Metronome, CalibrationState, detect_marker, get_mask,
    draw_mode_header, draw_hold_mode, draw_follow_mode, draw_results,
    CONFIG, save_session, calibration_state, ArduinoLED
)
from datetime import datetime, timezone

router = APIRouter()

# Global state for game2
class Game2State:
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.current_mode = AppMode.HOLD
        self.session_state = SessionState.IDLE
        self.session_start_time = 0.0
        self.last_results: Optional[Dict] = None
        self.current_bpm = CONFIG["default_bpm"]
        
        self.hold_metrics = HoldMetrics()
        self.follow_metrics = FollowMetrics()
        self.metronome = Metronome(CONFIG["default_bpm"])
        
        self.hsv_lower = np.array(CONFIG["hsv_lower"])
        self.hsv_upper = np.array(CONFIG["hsv_upper"])
        
        self.show_mask = False
        self.running = False
        self.frame_loop_task: Optional[asyncio.Task] = None
        
        # Arduino LED control
        self.arduino: Optional[ArduinoLED] = None

game2_state = Game2State()


def encode_frame(frame: np.ndarray) -> str:
    """Encode OpenCV frame to base64 JPEG string."""
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text


async def game2_frame_loop(websocket: WebSocket):
    """Main loop that processes frames and sends them to client."""
    global game2_state
    
    if not game2_state.cap or not game2_state.cap.isOpened():
        await websocket.send_json({
            "type": "error",
            "data": "Camera not initialized"
        })
        return
    
    frame_count = 0
    
    while game2_state.running:
        try:
            ret, frame = game2_state.cap.read()
            if not ret or frame is None:
                await asyncio.sleep(0.01)
                continue
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Detect marker
            pen_pos = detect_marker(frame, game2_state.hsv_lower, game2_state.hsv_upper)
            
            # Calculate elapsed time and metrics
            elapsed_time = 0.0
            time_remaining = 0.0
            beat_count = 0
            
            if game2_state.session_state == SessionState.RUNNING:
                elapsed_time = time.time() - game2_state.session_start_time
                duration = CONFIG["hold_duration"] if game2_state.current_mode == AppMode.HOLD else CONFIG["follow_duration"]
                time_remaining = max(0.0, duration - elapsed_time)
                
                if game2_state.current_mode == AppMode.FOLLOW:
                    beat_count = game2_state.metronome.get_beat_count()
                
                # Check if session should end
                if elapsed_time >= duration:
                    game2_state.session_state = SessionState.COMPLETE
                    if game2_state.current_mode == AppMode.FOLLOW:
                        game2_state.metronome.stop()
                    
                    # Get results and save session
                    if game2_state.current_mode == AppMode.HOLD:
                        game2_state.last_results = game2_state.hold_metrics.get_summary()
                        session_data = {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "type": "HOLD",
                            "duration_s": CONFIG["hold_duration"],
                            **game2_state.last_results,
                        }
                    else:
                        game2_state.last_results = game2_state.follow_metrics.get_summary()
                        session_data = {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "type": "FOLLOW",
                            "duration_s": CONFIG["follow_duration"],
                            "bpm": game2_state.current_bpm,
                            **game2_state.last_results,
                        }
                    
                    save_session(session_data)
                    
                    await websocket.send_json({
                        "type": "session_complete",
                        "data": game2_state.last_results
                    })
            
            # Update metrics if session is running
            if game2_state.session_state == SessionState.RUNNING:
                if game2_state.current_mode == AppMode.HOLD:
                    game2_state.hold_metrics.update(pen_pos)
                    # Update Arduino LED based on stability
                    if game2_state.arduino:
                        level = game2_state.hold_metrics.jitter_tracker.get_stability_level()
                        game2_state.arduino.update_from_stability(level)
                else:
                    game2_state.follow_metrics.update(pen_pos, beat_count)
                    # Update Arduino LED based on lateral stability
                    if game2_state.arduino:
                        status = game2_state.follow_metrics.get_feedback_status()
                        game2_state.arduino.update_from_stability(status)
            else:
                # Turn off LED when not running
                if game2_state.arduino:
                    game2_state.arduino.set_led(False)
            
            # Draw overlays
            frame = draw_mode_header(
                frame, 
                game2_state.current_mode, 
                game2_state.session_state, 
                time_remaining, 
                game2_state.current_bpm
            )
            
            if game2_state.session_state == SessionState.COMPLETE and game2_state.last_results:
                frame = draw_results(frame, game2_state.current_mode, game2_state.last_results)
            elif game2_state.current_mode == AppMode.HOLD:
                frame = draw_hold_mode(frame, pen_pos, game2_state.hold_metrics, game2_state.session_state)
            else:
                frame = draw_follow_mode(
                    frame, 
                    pen_pos, 
                    game2_state.follow_metrics, 
                    game2_state.session_state, 
                    beat_count
                )
            
            # Encode and send frame
            frame_encoded = encode_frame(frame)
            
            # Send frame every ~30ms (30 FPS)
            frame_count += 1
            if frame_count % 1 == 0:  # Send every frame for now
                await websocket.send_json({
                    "type": "frame",
                    "data": frame_encoded
                })
            
            # Also send metrics data
            if game2_state.current_mode == AppMode.HOLD:
                metrics_data = {
                    "mode": "HOLD",
                    "position": {"x": pen_pos[0], "y": pen_pos[1]} if pen_pos else None,
                    "marker_detected": pen_pos is not None,
                    "jitter": game2_state.hold_metrics.jitter_tracker.current_jitter,
                    "p95_jitter": game2_state.hold_metrics.jitter_tracker.p95_jitter,
                    "stability_level": game2_state.hold_metrics.jitter_tracker.get_stability_level(),
                    "score": game2_state.hold_metrics.get_stability_score(),
                    "session_state": game2_state.session_state.value,
                    "time_remaining": time_remaining,
                    "elapsed": elapsed_time,
                }
            else:
                metrics_data = {
                    "mode": "FOLLOW",
                    "position": {"x": pen_pos[0], "y": pen_pos[1]} if pen_pos else None,
                    "marker_detected": pen_pos is not None,
                    "lateral_jitter": game2_state.follow_metrics.jitter_tracker.current_lateral_jitter,
                    "p95_lateral_jitter": game2_state.follow_metrics.jitter_tracker.p95_lateral_jitter,
                    "feedback_status": game2_state.follow_metrics.get_feedback_status(),
                    "score": game2_state.follow_metrics.get_combined_score(),
                    "session_state": game2_state.session_state.value,
                    "time_remaining": time_remaining,
                    "elapsed": elapsed_time,
                    "beat_count": beat_count,
                    "bpm": game2_state.current_bpm,
                }
            
            await websocket.send_json({
                "type": "metrics",
                "data": metrics_data
            })
            
            await asyncio.sleep(1.0 / 30.0)  # ~30 FPS
            
        except Exception as e:
            print(f"Frame loop error: {e}")
            await asyncio.sleep(0.1)


@router.websocket("/ws/game2")
async def websocket_game2(websocket: WebSocket):
    """
    WebSocket endpoint for Game2 video streaming and control.
    
    Sends:
        - frame: Base64 encoded JPEG frames
        - metrics: Real-time metrics data
    
    Receives:
        - mode_switch: Switch between HOLD and FOLLOW modes
        - session_start: Start a session
        - session_stop: Stop current session
        - bpm_change: Change BPM for FOLLOW mode
        - calibration_click: Handle calibration clicks
        - hsv_update: Update HSV color range
        - keyboard: Keyboard input
    """
    global game2_state
    
    await websocket.accept()
    
    # Initialize camera if not already done
    if game2_state.cap is None or not game2_state.cap.isOpened():
        game2_state.cap = cv2.VideoCapture(CONFIG["camera_id"])
        game2_state.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CONFIG["frame_width"])
        game2_state.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG["frame_height"])
        
        if not game2_state.cap.isOpened():
            await websocket.send_json({
                "type": "error",
                "data": "Could not open camera"
            })
            return
        
        # Warm up camera
        for _ in range(30):
            ret, _ = game2_state.cap.read()
            if ret:
                break
            await asyncio.sleep(0.05)
    
    # Initialize Arduino LED if not already done
    if game2_state.arduino is None:
        game2_state.arduino = ArduinoLED(CONFIG["arduino_port"], CONFIG["arduino_baud"])
    
    game2_state.running = True
    
    await websocket.send_json({
        "type": "connected",
        "data": {
            "message": "Game2 WebSocket connected",
            "current_mode": game2_state.current_mode.value,
            "bpm": game2_state.current_bpm
        }
    })
    
    # Start frame loop
    frame_task = asyncio.create_task(game2_frame_loop(websocket))
    
    try:
        while True:
            raw_data = await websocket.receive_text()
            message = json.loads(raw_data)
            
            msg_type = message.get("type")
            msg_data = message.get("data", {})
            
            if msg_type == "mode_switch":
                if game2_state.session_state != SessionState.RUNNING:
                    mode_str = msg_data.get("mode", "HOLD")
                    game2_state.current_mode = AppMode.HOLD if mode_str == "HOLD" else AppMode.FOLLOW
                    game2_state.session_state = SessionState.IDLE
                    game2_state.last_results = None
                    await websocket.send_json({
                        "type": "mode_switched",
                        "data": {"mode": game2_state.current_mode.value}
                    })
            
            elif msg_type == "session_start":
                if game2_state.session_state == SessionState.IDLE:
                    game2_state.session_state = SessionState.RUNNING
                    game2_state.session_start_time = time.time()
                    game2_state.last_results = None
                    
                    if game2_state.current_mode == AppMode.HOLD:
                        game2_state.hold_metrics.reset()
                    else:
                        game2_state.follow_metrics.reset()
                        game2_state.metronome.set_bpm(game2_state.current_bpm)
                        game2_state.metronome.start()
                    
                    await websocket.send_json({
                        "type": "session_started",
                        "data": {
                            "mode": game2_state.current_mode.value,
                            "duration": CONFIG["hold_duration"] if game2_state.current_mode == AppMode.HOLD else CONFIG["follow_duration"]
                        }
                    })
            
            elif msg_type == "session_stop":
                if game2_state.session_state == SessionState.RUNNING:
                    game2_state.session_state = SessionState.IDLE
                    game2_state.metronome.stop()
                    # Turn off LED when session stops
                    if game2_state.arduino:
                        game2_state.arduino.set_led(False)
                    await websocket.send_json({
                        "type": "session_stopped",
                        "data": {}
                    })
            
            elif msg_type == "bpm_change":
                if game2_state.session_state != SessionState.RUNNING:
                    delta = msg_data.get("delta", 0)
                    game2_state.current_bpm = max(20, min(200, game2_state.current_bpm + delta))
                    await websocket.send_json({
                        "type": "bpm_changed",
                        "data": {"bpm": game2_state.current_bpm}
                    })
            
            elif msg_type == "calibration_click":
                if game2_state.current_mode == AppMode.HOLD and game2_state.session_state != SessionState.RUNNING:
                    x = msg_data.get("x")
                    y = msg_data.get("y")
                    if x is not None and y is not None:
                        calibration_state.handle_click(x, y)
                        await websocket.send_json({
                            "type": "calibration_updated",
                            "data": {
                                "center": calibration_state.center,
                                "radius": calibration_state.radius,
                                "click_count": calibration_state.click_count
                            }
                        })
            
            elif msg_type == "hsv_update":
                hsv_data = msg_data
                game2_state.hsv_lower = np.array([
                    hsv_data.get("lower_h", CONFIG["hsv_lower"][0]),
                    hsv_data.get("lower_s", CONFIG["hsv_lower"][1]),
                    hsv_data.get("lower_v", CONFIG["hsv_lower"][2])
                ])
                game2_state.hsv_upper = np.array([
                    hsv_data.get("upper_h", CONFIG["hsv_upper"][0]),
                    hsv_data.get("upper_s", CONFIG["hsv_upper"][1]),
                    hsv_data.get("upper_v", CONFIG["hsv_upper"][2])
                ])
                await websocket.send_json({
                    "type": "hsv_updated",
                    "data": {
                        "lower": game2_state.hsv_lower.tolist(),
                        "upper": game2_state.hsv_upper.tolist()
                    }
                })
            
            elif msg_type == "keyboard":
                key = msg_data.get("key")
                # Handle keyboard shortcuts
                if key == "1":
                    if game2_state.session_state != SessionState.RUNNING:
                        game2_state.current_mode = AppMode.HOLD
                        game2_state.session_state = SessionState.IDLE
                        game2_state.last_results = None
                elif key == "2":
                    if game2_state.session_state != SessionState.RUNNING:
                        game2_state.current_mode = AppMode.FOLLOW
                        game2_state.session_state = SessionState.IDLE
                        game2_state.last_results = None
                elif key == " ":
                    if game2_state.session_state == SessionState.IDLE:
                        game2_state.session_state = SessionState.RUNNING
                        game2_state.session_start_time = time.time()
                        game2_state.last_results = None
                        if game2_state.current_mode == AppMode.HOLD:
                            game2_state.hold_metrics.reset()
                        else:
                            game2_state.follow_metrics.reset()
                            game2_state.metronome.set_bpm(game2_state.current_bpm)
                            game2_state.metronome.start()
                    elif game2_state.session_state == SessionState.RUNNING:
                        game2_state.session_state = SessionState.IDLE
                        game2_state.metronome.stop()
                    elif game2_state.session_state == SessionState.COMPLETE:
                        game2_state.session_state = SessionState.IDLE
                        game2_state.last_results = None
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        game2_state.running = False
        frame_task.cancel()
        try:
            await frame_task
        except asyncio.CancelledError:
            pass
