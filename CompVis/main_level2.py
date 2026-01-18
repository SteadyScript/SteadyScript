"""
SteadyScript Level 2 - FOLLOW Mode Standalone
Real-time smooth pursuit training with movement quality metrics.
Run this file directly to test Level 2 FOLLOW mode.
"""

import cv2
import numpy as np
import time
import json
import os
from datetime import datetime
from typing import Optional, Tuple

import cv_tracker
import follow_session
from target_path import TargetPath
import utils


# Window name
WINDOW_NAME = "SteadyScript Level 2 - FOLLOW Mode"

# Session duration
FOLLOW_DURATION = 20.0

# Application states
CALIBRATE_A = "CALIBRATE_A"
CALIBRATE_B = "CALIBRATE_B"
READY = "READY"
RUNNING = "RUNNING"
RESULT = "RESULT"


class Level2App:
    """Standalone Level 2 FOLLOW mode application."""
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize the application.
        
        Args:
            camera_index: Camera index to use (default 0)
        """
        # Camera
        self.cap: Optional[cv2.VideoCapture] = None
        
        # Session
        self.session = follow_session.FollowSessionManager(duration=FOLLOW_DURATION)
        
        # Application state
        self.current_state = CALIBRATE_A
        self.hsv_trackbars_visible = False
        self.hsv_lower = cv_tracker.DEFAULT_HSV_LOWER.copy()
        self.hsv_upper = cv_tracker.DEFAULT_HSV_UPPER.copy()
        
        # Marker detection
        self.marker_pos: Optional[Tuple[int, int]] = None
        
        # Target path
        self.target_path: Optional[TargetPath] = None
        
        # Calibration points
        self.point_a: Optional[Tuple[int, int]] = None
        self.point_b: Optional[Tuple[int, int]] = None
        
        # Initialize camera
        self._init_camera(camera_index)
    
    def _init_camera(self, camera_index: int = 0):
        """Initialize camera capture."""
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            raise RuntimeError(f"Camera {camera_index} not available")
        
        # Test if we can actually read a frame
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            print(f"Error: Camera {camera_index} opened but cannot read frames")
            raise RuntimeError(f"Camera {camera_index} cannot read frames")
        
        # Initialize target path with frame dimensions
        h, w = frame.shape[:2]
        self.target_path = TargetPath(w, h)
        
        print(f"Using camera {camera_index}")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    def _setup_window(self):
        """Setup OpenCV window and mouse callback."""
        cv2.namedWindow(WINDOW_NAME)
        cv2.setMouseCallback(WINDOW_NAME, self._mouse_callback)
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks for A/B calibration."""
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.current_state == CALIBRATE_A:
                self.point_a = (x, y)
                self.current_state = CALIBRATE_B
                print(f"Point A set at ({x}, {y})")
            elif self.current_state == CALIBRATE_B:
                self.point_b = (x, y)
                if self.target_path is not None:
                    self.target_path.set_points(self.point_a, self.point_b)
                self.current_state = READY
                print(f"Point B set at ({x}, {y})")
                print("Calibration complete! Press SPACE to start.")
    
    def _handle_keyboard(self, key: int) -> bool:
        """Handle keyboard input."""
        key_char = chr(key & 0xFF) if key != -1 else None
        
        if key_char == 'q':
            return False
        
        elif key_char == 't':
            # Toggle HSV trackbars
            self.hsv_trackbars_visible = not self.hsv_trackbars_visible
            if self.hsv_trackbars_visible:
                def nothing(x):
                    pass
                cv2.createTrackbar('Lower H', WINDOW_NAME, int(self.hsv_lower[0]), 179, nothing)
                cv2.createTrackbar('Lower S', WINDOW_NAME, int(self.hsv_lower[1]), 255, nothing)
                cv2.createTrackbar('Lower V', WINDOW_NAME, int(self.hsv_lower[2]), 255, nothing)
                cv2.createTrackbar('Upper H', WINDOW_NAME, int(self.hsv_upper[0]), 179, nothing)
                cv2.createTrackbar('Upper S', WINDOW_NAME, int(self.hsv_upper[1]), 255, nothing)
                cv2.createTrackbar('Upper V', WINDOW_NAME, int(self.hsv_upper[2]), 255, nothing)
                print("HSV trackbars enabled")
            else:
                print("HSV trackbars disabled")
        
        elif key_char == 'c':
            # Reset calibration
            self.point_a = None
            self.point_b = None
            self.current_state = CALIBRATE_A
            print("Calibration reset")
        
        elif key_char == ' ' and self.current_state == READY:
            # Start session (only if A and B are set)
            if self.point_a is not None and self.point_b is not None:
                self.session.start_session(self.point_a, self.point_b)
                self.current_state = RUNNING
                print("FOLLOW session started!")
            else:
                print("Please calibrate points A and B first!")
        
        elif key_char == ' ' and self.current_state == RESULT:
            # Retry from result screen
            if self.point_a is not None and self.point_b is not None:
                self.current_state = READY
            else:
                self.current_state = CALIBRATE_A
            print("Ready for new session")
        
        return True
    
    def _detect_marker(self, frame: np.ndarray):
        """Detect marker in current frame."""
        # Get HSV bounds from trackbars if visible
        if self.hsv_trackbars_visible:
            try:
                self.hsv_lower[0] = cv2.getTrackbarPos('Lower H', WINDOW_NAME)
                self.hsv_lower[1] = cv2.getTrackbarPos('Lower S', WINDOW_NAME)
                self.hsv_lower[2] = cv2.getTrackbarPos('Lower V', WINDOW_NAME)
                self.hsv_upper[0] = cv2.getTrackbarPos('Upper H', WINDOW_NAME)
                self.hsv_upper[1] = cv2.getTrackbarPos('Upper S', WINDOW_NAME)
                self.hsv_upper[2] = cv2.getTrackbarPos('Upper V', WINDOW_NAME)
            except:
                pass
        
        # Detect marker
        self.marker_pos = cv_tracker.detect_marker(frame, self.hsv_lower, self.hsv_upper)
    
    def _draw_overlays(self, frame: np.ndarray):
        """Draw UI overlays on frame."""
        h, w = frame.shape[:2]
        
        # Draw mode indicator
        mode_text = "Level 2: FOLLOW Mode"
        cv2.putText(frame, mode_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, mode_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
        
        # Draw marker status
        if self.marker_pos is not None:
            marker_text = "Marker: OK"
            color = (0, 255, 0)
        else:
            marker_text = "Marker: NOT FOUND"
            color = (0, 0, 255)
        
        cv2.putText(frame, marker_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw A and B boxes if calibrated
        if self.point_a is not None:
            # Draw box A (blue)
            box_size = 30
            top_left = (self.point_a[0] - box_size//2, self.point_a[1] - box_size//2)
            bottom_right = (self.point_a[0] + box_size//2, self.point_a[1] + box_size//2)
            cv2.rectangle(frame, top_left, bottom_right, (255, 0, 0), 2)
            cv2.putText(frame, "A", (self.point_a[0] - 5, self.point_a[1] + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        if self.point_b is not None:
            # Draw box B (red)
            box_size = 30
            top_left = (self.point_b[0] - box_size//2, self.point_b[1] - box_size//2)
            bottom_right = (self.point_b[0] + box_size//2, self.point_b[1] + box_size//2)
            cv2.rectangle(frame, top_left, bottom_right, (0, 0, 255), 2)
            cv2.putText(frame, "B", (self.point_b[0] - 5, self.point_b[1] + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # State-specific overlays
        if self.current_state == CALIBRATE_A:
            instruction = "Click to set Point A (first box)"
            cv2.putText(frame, instruction, (w//2 - 180, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        elif self.current_state == CALIBRATE_B:
            instruction = "Click to set Point B (second box)"
            cv2.putText(frame, instruction, (w//2 - 180, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        elif self.current_state == READY:
            instruction = "Press SPACE to start FOLLOW session"
            cv2.putText(frame, instruction, (w//2 - 200, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        elif self.current_state == RUNNING:
            # Draw target dot and path
            if self.target_path is not None:
                elapsed = self.session.get_elapsed_time()
                target_pos = self.target_path.get_position(elapsed)
                
                # Draw target dot (green circle)
                cv2.circle(frame, target_pos, 8, (0, 255, 0), -1)
                cv2.circle(frame, target_pos, 10, (0, 255, 0), 2)
            
            # Draw pen trail (last 2 seconds, ~60 frames)
            if self.marker_pos is not None and len(self.session.positions) > 1:
                trail_points = list(self.session.positions)[-60:]
                for i in range(1, len(trail_points)):
                    pt1 = (int(trail_points[i-1][0]), int(trail_points[i-1][1]))
                    pt2 = (int(trail_points[i][0]), int(trail_points[i][1]))
                    alpha = i / len(trail_points)
                    color = (0, int(255 * alpha), 255)
                    cv2.line(frame, pt1, pt2, color, 2)
            
            # Draw marker position
            if self.marker_pos is not None:
                cv2.circle(frame, self.marker_pos, 5, (0, 0, 255), -1)
            
            # Metronome display (top-right corner) - speeds up over time
            elapsed = self.session.get_elapsed_time()
            if self.target_path is not None:
                speed_mult = self.target_path.get_current_speed_multiplier(elapsed)
                metronome_text = f"Speed: {speed_mult:.1f}x"
                cv2.putText(frame, metronome_text, (w - 150, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Visual metronome indicator (pulsing circle)
                metronome_x = w - 50
                metronome_y = 60
                pulse_size = int(10 + 5 * (speed_mult - 1.0))
                cv2.circle(frame, (metronome_x, metronome_y), pulse_size, (0, 255, 255), 2)
            
            # Session running overlays
            time_text = f"Time: {elapsed:.1f} / {FOLLOW_DURATION:.1f}s"
            cv2.putText(frame, time_text, (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Real-time metrics (focus on movement quality, not target accuracy)
            jitter_text = f"Jitter (p95): {self.session.p95_jitter:.2f} px"
            cv2.putText(frame, jitter_text, (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            jerk_text = f"Jerk (p95): {self.session.p95_jerk:.2f}"
            cv2.putText(frame, jerk_text, (10, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Status indicator (green/red based on thresholds)
            jitter_ok = self.session.p95_jitter < follow_session.FOLLOW_CONFIG["jitter_ref"]
            jerk_ok = self.session.p95_jerk < follow_session.FOLLOW_CONFIG["jerk_ref"]
            status_color = (0, 255, 0) if (jitter_ok and jerk_ok) else (0, 0, 255)
            status_text = "Status: GOOD" if (jitter_ok and jerk_ok) else "Status: NEEDS IMPROVEMENT"
            cv2.putText(frame, status_text, (10, 210), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            # Check if session ended
            if not self.session.is_active:
                self.current_state = RESULT
                self._save_session_result()
        
        elif self.current_state == RESULT:
            # Result screen
            metrics = self.session.get_final_metrics()
            y_offset = h//2 - 100
            result_text = "FOLLOW Session Complete!"
            cv2.putText(frame, result_text, (w//2 - 180, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            y_offset += 40
            score_text = f"Movement Quality Score: {metrics['movement_quality_score']:.1f}/100"
            cv2.putText(frame, score_text, (w//2 - 200, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_offset += 35
            jitter_text = f"Jitter (p95): {metrics['p95_jitter']:.2f} px"
            cv2.putText(frame, jitter_text, (w//2 - 120, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30
            jerk_text = f"Jerk (p95): {metrics['p95_jerk']:.2f}"
            cv2.putText(frame, jerk_text, (w//2 - 100, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 40
            retry_text = "Press SPACE to retry"
            cv2.putText(frame, retry_text, (w//2 - 120, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw controls help (bottom)
        if self.current_state in [CALIBRATE_A, CALIBRATE_B]:
            controls = "Click to set points A and B, 'c'=reset, 't'=HSV tune, 'q'=quit"
        else:
            controls = "Controls: 'c'=reset calib, 't'=HSV tune, SPACE=start/retry, 'q'=quit"
        cv2.putText(frame, controls, (10, h - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    def _save_session_result(self):
        """Save session result to JSON file."""
        metrics = self.session.get_final_metrics()
        
        session_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hsv_lower": self.hsv_lower.tolist(),
            "hsv_upper": self.hsv_upper.tolist(),
            **metrics
        }
        
        # Save to data/sessions.json
        data_file = "data/sessions.json"
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        
        # Load existing sessions
        sessions = []
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    sessions = json.load(f)
                    if not isinstance(sessions, list):
                        sessions = []
            except:
                sessions = []
        
        # Append new session
        sessions.append(session_data)
        
        try:
            with open(data_file, 'w') as f:
                json.dump(sessions, f, indent=2)
            print(f"Session saved: Movement Quality Score = {metrics['movement_quality_score']:.1f}/100")
        except Exception as e:
            print(f"Warning: Failed to save session: {e}")
    
    def run(self):
        """Main application loop."""
        self._setup_window()
        
        print("SteadyScript Level 2 - FOLLOW Mode")
        print("Instructions:")
        print("  1. Click to set Point A (first box)")
        print("  2. Click to set Point B (second box)")
        print("  3. Press SPACE to start a 20-second follow session")
        print("  4. Follow the green target dot back and forth between A and B")
        print("  5. Focus on smooth movement - speed will increase over time")
        print("  Press 't' to tune HSV if marker not detected")
        print("  Press 'q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to read frame")
                break
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Detect marker
            self._detect_marker(frame)
            
            # Update session if running
            if self.current_state == RUNNING:
                # Get target position
                target_pos = None
                if self.target_path is not None:
                    elapsed = self.session.get_elapsed_time()
                    target_pos = self.target_path.get_position(elapsed)
                
                # Update follow session
                dt = 1.0 / 30.0  # Assume ~30 FPS
                self.session.update(self.marker_pos, target_pos, dt)
            
            # Draw overlays
            self._draw_overlays(frame)
            
            # Show mask if HSV tuning is active
            if self.hsv_trackbars_visible:
                mask = cv_tracker.get_mask(frame, self.hsv_lower, self.hsv_upper)
                cv2.imshow("Mask (HSV Tuning)", mask)
            else:
                try:
                    cv2.destroyWindow("Mask (HSV Tuning)")
                except:
                    pass
            
            # Display frame
            cv2.imshow(WINDOW_NAME, frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key != 255:  # Key pressed
                if not self._handle_keyboard(key):
                    break
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("SteadyScript Level 2 closed")


def main():
    """Entry point."""
    import sys
    
    camera_index = 0
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except ValueError:
            print(f"Invalid camera index: {sys.argv[1]}. Using default (0).")
    
    try:
        app = Level2App(camera_index=camera_index)
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
