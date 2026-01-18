"""
SteadyScript - Main Entry Point
Real-time computer vision tremor training prototype.
"""

import cv2
import numpy as np
import time
from datetime import datetime
from typing import Optional, Tuple

import cv_tracker
from calibration import CalibrationState, CalibrationHandler
import session
import follow_session
from target_path import TargetPath
import utils
from arduino_led import ArduinoLEDController


# Application modes
MODE_HOLD = "HOLD"
MODE_FOLLOW = "FOLLOW"

# Application states
MENU = "MENU"
CALIBRATE_CENTER = "CALIBRATE_CENTER"
CALIBRATE_RADIUS = "CALIBRATE_RADIUS"
READY = "READY"
RUNNING = "RUNNING"
RESULT = "RESULT"

# Window name
WINDOW_NAME = "SteadyScript"

# Session durations
HOLD_DURATION = 10.0
FOLLOW_DURATION = 20.0


class SteadyScriptApp:
    """Main application class for SteadyScript tremor training."""
    
    def __init__(self, camera_index: int = None, arduino_port: Optional[str] = None):
        """
        Initialize the application.
        
        Args:
            camera_index: Specific camera index to use, or None to auto-detect
            arduino_port: Arduino serial port (e.g., 'COM3' on Windows), or None to disable
        """
        # Camera
        self.cap: Optional[cv2.VideoCapture] = None
        
        # Calibration
        self.calibration_state = CalibrationState()
        self.calibration_handler = CalibrationHandler(self.calibration_state)
        
        # Session managers
        self.hold_session = session.SessionManager(duration=HOLD_DURATION)
        self.follow_session = follow_session.FollowSessionManager(duration=FOLLOW_DURATION)
        
        # Current mode and state
        self.current_mode = MODE_HOLD
        self.current_state = MENU
        
        # Target path for FOLLOW mode
        self.target_path: Optional[TargetPath] = None
        self.hsv_trackbars_visible = False
        self.hsv_lower = cv_tracker.DEFAULT_HSV_LOWER.copy()
        self.hsv_upper = cv_tracker.DEFAULT_HSV_UPPER.copy()
        
        # Marker detection
        self.marker_pos: Optional[Tuple[int, int]] = None
        
        # Arduino LED controller
        self.arduino: Optional[ArduinoLEDController] = None
        if arduino_port:
            self.arduino = ArduinoLEDController(port=arduino_port)
        
        # Initialize camera
        self._init_camera(camera_index)
    
    def _init_camera(self, camera_index: int = None):
        """
        Initialize camera capture.
        Defaults to camera 0 if camera_index is not specified.
        
        Args:
            camera_index: Specific camera index to use, or None to use camera 0
        """
        if camera_index is None:
            camera_index = 0  # Default to camera 0
        
        # Try specific camera index
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            raise RuntimeError(f"Camera {camera_index} not available")
        
        # Test if we can actually read a frame
        ret, _ = self.cap.read()
        if not ret:
            self.cap.release()
            print(f"Error: Camera {camera_index} opened but cannot read frames")
            raise RuntimeError(f"Camera {camera_index} cannot read frames")
        
        print(f"Using camera {camera_index}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    def _setup_window(self):
        """Setup OpenCV window and mouse callback."""
        cv2.namedWindow(WINDOW_NAME)
        cv2.setMouseCallback(WINDOW_NAME, self.calibration_handler.mouse_callback)
    
    def _handle_keyboard(self, key: int) -> bool:
        """
        Handle keyboard input.
        
        Args:
            key: Key code from cv2.waitKey()
            
        Returns:
            True if should continue, False if should quit
        """
        key_char = chr(key & 0xFF) if key != -1 else None
        
        if key_char == 'q':
            return False
        
        elif key_char == '1':
            # Switch to HOLD mode
            if self.current_state == RUNNING:
                return True  # Don't switch during active session
            self.current_mode = MODE_HOLD
            if self.calibration_state.is_complete():
                self.current_state = READY
            else:
                self.current_state = CALIBRATE_CENTER
            print("Switched to HOLD mode")
        
        elif key_char == '2':
            # Switch to FOLLOW mode
            if self.current_state == RUNNING:
                return True  # Don't switch during active session
            self.current_mode = MODE_FOLLOW
            self.current_state = READY
            print("Switched to FOLLOW mode")
        
        elif key_char == 'c':
            # Reset calibration (only for HOLD mode)
            if self.current_mode == MODE_HOLD:
                self.calibration_state.reset()
                self.current_state = CALIBRATE_CENTER
                print("Calibration reset")
        
        elif key_char == 't':
            # Toggle HSV trackbars
            self.hsv_trackbars_visible = not self.hsv_trackbars_visible
            if self.hsv_trackbars_visible:
                cv_tracker.create_hsv_trackbars(WINDOW_NAME, self.hsv_lower, self.hsv_upper)
                print("HSV trackbars enabled - adjust to tune marker detection")
            else:
                print("HSV trackbars disabled")
        
        elif key_char == ' ' and self.current_state == READY:
            # Start session
            if self.current_mode == MODE_HOLD:
                if self.calibration_state.is_complete():
                    self.hold_session.start_session()
                    self.current_state = RUNNING
                    print("HOLD session started!")
            elif self.current_mode == MODE_FOLLOW:
                # Initialize target path if needed
                if self.target_path is None:
                    ret, frame = self.cap.read()
                    if ret:
                        h, w = frame.shape[:2]
                        self.target_path = TargetPath(w, h)
                self.follow_session.start_session()
                self.current_state = RUNNING
                print("FOLLOW session started!")
        
        elif key_char == ' ' and self.current_state == RESULT:
            # Retry from result screen
            if self.current_mode == MODE_HOLD:
                if self.calibration_state.is_complete():
                    self.current_state = READY
                else:
                    self.current_state = CALIBRATE_CENTER
            else:
                self.current_state = READY
            print("Ready for new session")
        
        return True
    
    def _update_calibration_state(self):
        """Update calibration state machine."""
        # Only update calibration state for HOLD mode
        if self.current_mode == MODE_HOLD:
            if not self.calibration_state.is_complete():
                if self.calibration_state.center is None:
                    self.current_state = CALIBRATE_CENTER
                else:
                    self.current_state = CALIBRATE_RADIUS
            else:
                if self.current_state in [CALIBRATE_CENTER, CALIBRATE_RADIUS, MENU]:
                    self.current_state = READY
    
    def _detect_marker(self, frame: np.ndarray):
        """Detect marker in current frame."""
        # Get HSV bounds from trackbars if visible
        if self.hsv_trackbars_visible:
            try:
                self.hsv_lower, self.hsv_upper = cv_tracker.get_hsv_from_trackbars(WINDOW_NAME)
            except:
                pass  # Trackbars might not be ready yet
        
        # Detect marker
        self.marker_pos = cv_tracker.detect_marker(frame, self.hsv_lower, self.hsv_upper)
    
    def _draw_overlays(self, frame: np.ndarray):
        """Draw UI overlays on frame."""
        h, w = frame.shape[:2]
        
        # Draw mode and state indicator (top-left)
        mode_text = f"Mode: {self.current_mode} | State: {self.current_state}"
        cv2.putText(frame, mode_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, mode_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # Draw marker status
        if self.marker_pos is not None:
            marker_text = "Marker: OK"
            color = (0, 255, 0)
        else:
            marker_text = "Marker: NOT FOUND"
            color = (0, 0, 255)
        
        cv2.putText(frame, marker_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # MENU state - show mode selection
        if self.current_state == MENU:
            y_start = h//2 - 60
            cv2.putText(frame, "Select Mode:", (w//2 - 100, y_start), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            y_start += 40
            cv2.putText(frame, "Press '1' for HOLD mode", (w//2 - 150, y_start), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            y_start += 35
            cv2.putText(frame, "Press '2' for FOLLOW mode", (w//2 - 150, y_start), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # HOLD mode specific overlays
        if self.current_mode == MODE_HOLD:
            # Draw circle overlay if calibrated
            if self.calibration_state.is_complete():
                center = self.calibration_state.center
                radius = self.calibration_state.radius
                cv2.circle(frame, center, int(radius), (255, 0, 0), 2)
                cv2.circle(frame, center, 3, (255, 0, 0), -1)
            
            # Draw marker position
            if self.marker_pos is not None:
                cv2.circle(frame, self.marker_pos, 5, (0, 0, 255), -1)
                
                # Check if inside circle
                if self.calibration_state.is_complete():
                    inside = utils.point_in_circle(
                        self.marker_pos, 
                        self.calibration_state.center, 
                        self.calibration_state.radius
                    )
                    inside_text = "Inside: YES" if inside else "Inside: NO"
                    inside_color = (0, 255, 0) if inside else (0, 0, 255)
                    cv2.putText(frame, inside_text, (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, inside_color, 2)
            
            # HOLD state-specific overlays
            if self.current_state == CALIBRATE_CENTER:
                instruction = "Click to set circle CENTER"
                cv2.putText(frame, instruction, (w//2 - 150, h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            elif self.current_state == CALIBRATE_RADIUS:
                instruction = "Click to set circle EDGE (radius)"
                cv2.putText(frame, instruction, (w//2 - 150, h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            elif self.current_state == READY:
                instruction = "Press SPACE to start HOLD session"
                cv2.putText(frame, instruction, (w//2 - 180, h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            elif self.current_state == RUNNING:
                elapsed = self.hold_session.get_elapsed_time()
                time_text = f"Time: {elapsed:.1f} / {HOLD_DURATION:.1f}s"
                cv2.putText(frame, time_text, (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                jitter_text = f"Jitter: {self.hold_session.current_jitter:.2f} px"
                cv2.putText(frame, jitter_text, (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                tremor_text = f"Tremor: {self.hold_session.tremor_score:.2f}"
                cv2.putText(frame, tremor_text, (10, 180), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                if not self.hold_session.is_active:
                    self.current_state = RESULT
                    self._save_session_result()
            
            elif self.current_state == RESULT:
                metrics = self.hold_session.get_final_metrics()
                y_offset = h//2 - 80
                result_text = "HOLD Session Complete!"
                cv2.putText(frame, result_text, (w//2 - 150, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                y_offset += 40
                tremor_final = f"Tremor Score: {metrics['tremor_score']:.2f}"
                cv2.putText(frame, tremor_final, (w//2 - 120, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                y_offset += 35
                stability = f"Stability: {metrics['inside_circle_pct']:.1f}%"
                cv2.putText(frame, stability, (w//2 - 100, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                y_offset += 40
                retry_text = "Press SPACE to retry"
                cv2.putText(frame, retry_text, (w//2 - 120, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # FOLLOW mode specific overlays
        elif self.current_mode == MODE_FOLLOW:
            # Draw target dot and path
            if self.target_path is not None and self.current_state == RUNNING:
                elapsed = self.follow_session.get_elapsed_time()
                target_pos = self.target_path.get_position(elapsed)
                
                # Draw target dot (green circle)
                cv2.circle(frame, target_pos, 8, (0, 255, 0), -1)
                cv2.circle(frame, target_pos, 10, (0, 255, 0), 2)
                
                # Draw pen trail (last 2 seconds, ~60 frames)
                if self.marker_pos is not None and len(self.follow_session.positions) > 1:
                    trail_points = list(self.follow_session.positions)[-60:]
                    for i in range(1, len(trail_points)):
                        pt1 = (int(trail_points[i-1][0]), int(trail_points[i-1][1]))
                        pt2 = (int(trail_points[i][0]), int(trail_points[i][1]))
                        alpha = i / len(trail_points)
                        color = (0, int(255 * alpha), 255)
                        cv2.line(frame, pt1, pt2, color, 2)
            
            # Draw marker position
            if self.marker_pos is not None:
                cv2.circle(frame, self.marker_pos, 5, (0, 0, 255), -1)
            
            # FOLLOW state-specific overlays
            if self.current_state == READY:
                instruction = "Press SPACE to start FOLLOW session"
                cv2.putText(frame, instruction, (w//2 - 200, h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            elif self.current_state == RUNNING:
                elapsed = self.follow_session.get_elapsed_time()
                time_text = f"Time: {elapsed:.1f} / {FOLLOW_DURATION:.1f}s"
                cv2.putText(frame, time_text, (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Real-time metrics
                jitter_text = f"Jitter (p95): {self.follow_session.p95_jitter:.2f} px"
                cv2.putText(frame, jitter_text, (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                jerk_text = f"Jerk (p95): {self.follow_session.p95_jerk:.2f}"
                cv2.putText(frame, jerk_text, (10, 180), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Status indicator (green/red based on thresholds)
                jitter_ok = self.follow_session.p95_jitter < follow_session.FOLLOW_CONFIG["jitter_ref"]
                jerk_ok = self.follow_session.p95_jerk < follow_session.FOLLOW_CONFIG["jerk_ref"]
                status_color = (0, 255, 0) if (jitter_ok and jerk_ok) else (0, 0, 255)
                status_text = "Status: GOOD" if (jitter_ok and jerk_ok) else "Status: NEEDS IMPROVEMENT"
                cv2.putText(frame, status_text, (10, 210), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                
                if not self.follow_session.is_active:
                    self.current_state = RESULT
                    self._save_session_result()
            
            elif self.current_state == RESULT:
                metrics = self.follow_session.get_final_metrics()
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
        if self.current_mode == MODE_HOLD:
            controls = "Controls: '1'=HOLD, '2'=FOLLOW, 'c'=reset calib, 't'=HSV, SPACE=start/retry, 'q'=quit"
        else:
            controls = "Controls: '1'=HOLD, '2'=FOLLOW, 't'=HSV, SPACE=start/retry, 'q'=quit"
        cv2.putText(frame, controls, (10, h - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    def _save_session_result(self):
        """Save session result to JSON file."""
        session_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hsv_lower": self.hsv_lower.tolist(),
            "hsv_upper": self.hsv_upper.tolist(),
        }
        
        if self.current_mode == MODE_HOLD:
            if not self.calibration_state.is_complete():
                return
            metrics = self.hold_session.get_final_metrics()
            session_data.update({
                "circle_center": list(self.calibration_state.center),
                "circle_radius": round(self.calibration_state.radius, 2),
                **metrics
            })
            if utils.save_session(session_data):
                print(f"HOLD session saved: Tremor Score = {metrics['tremor_score']:.2f}")
            else:
                print("Warning: Failed to save HOLD session")
        
        elif self.current_mode == MODE_FOLLOW:
            metrics = self.follow_session.get_final_metrics()
            session_data.update(metrics)
            if utils.save_session(session_data):
                print(f"FOLLOW session saved: Movement Quality Score = {metrics['movement_quality_score']:.1f}/100")
            else:
                print("Warning: Failed to save FOLLOW session")
    
    def run(self):
        """Main application loop."""
        self._setup_window()
        
        print("SteadyScript Level 2 - Starting...")
        print("Instructions:")
        print("  Press '1' for HOLD mode (Level 1)")
        print("  Press '2' for FOLLOW mode (Level 2)")
        print("  Press 't' to tune HSV if marker not detected")
        print("  Press SPACE to start session")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to read frame")
                break
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Update calibration state
            self._update_calibration_state()
            
            # Detect marker
            self._detect_marker(frame)
            
            # Update session if running
            if self.current_state == RUNNING:
                if self.current_mode == MODE_HOLD:
                    circle_center = self.calibration_state.center if self.calibration_state.is_complete() else None
                    circle_radius = self.calibration_state.radius if self.calibration_state.is_complete() else 0.0
                    self.hold_session.update(self.marker_pos, circle_center, circle_radius)
                elif self.current_mode == MODE_FOLLOW:
                    # Get target position for FOLLOW mode
                    target_pos = None
                    if self.target_path is not None:
                        elapsed = self.follow_session.get_elapsed_time()
                        target_pos = self.target_path.get_position(elapsed)
                    
                    # Update follow session with marker and target positions
                    dt = 1.0 / 30.0  # Assume ~30 FPS
                    self.follow_session.update(self.marker_pos, target_pos, dt)
            
            # Update Arduino LED based on marker position (only for HOLD mode)
            if self.arduino is not None and self.arduino.is_connected:
                if self.current_mode == MODE_HOLD:
                    if self.calibration_state.is_complete() and self.marker_pos is not None:
                        marker_inside = utils.point_in_circle(
                            self.marker_pos, 
                            self.calibration_state.center, 
                            self.calibration_state.radius
                        )
                        self.arduino.update(marker_inside)
                    else:
                        self.arduino.update(False)
                else:
                    # FOLLOW mode - LED off (or could implement different behavior)
                    self.arduino.update(False)
            
            # Draw overlays
            self._draw_overlays(frame)
            
            # Show mask if HSV tuning is active
            if self.hsv_trackbars_visible:
                mask = cv_tracker.get_mask(frame, self.hsv_lower, self.hsv_upper)
                cv2.imshow("Mask (HSV Tuning)", mask)
            else:
                # Close mask window if it exists
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
        if self.arduino is not None:
            self.arduino.close()
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("SteadyScript closed")


def main():
    """Entry point."""
    import sys
    
    # --- CONFIGURATION ---
    # PASTE YOUR EXACT MAC PORT HERE (e.g., '/dev/tty.usbmodem1101')
    # You can find this in Arduino IDE > Tools > Port
    DEFAULT_PORT = '/dev/tty.usbmodemB0818498245C2' 
    # ---------------------

    camera_index = None
    arduino_port = DEFAULT_PORT 
    
    # Allow command line overrides (optional)
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
        try:
            camera_index = int(arg1)
            if len(sys.argv) > 2:
                arduino_port = sys.argv[2]
        except ValueError:
            arduino_port = arg1
            if len(sys.argv) > 2:
                try:
                    camera_index = int(sys.argv[2])
                except ValueError:
                    pass

    print(f"Starting SteadyScript with Arduino Port: {arduino_port}")

    try:
        app = SteadyScriptApp(camera_index=camera_index, arduino_port=arduino_port)
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()