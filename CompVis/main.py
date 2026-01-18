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
import utils
from arduino_led import ArduinoLEDController


# Application states
CALIBRATE_CENTER = "CALIBRATE_CENTER"
CALIBRATE_RADIUS = "CALIBRATE_RADIUS"
READY = "READY"
RUNNING = "RUNNING"
RESULT = "RESULT"

# Window name
WINDOW_NAME = "SteadyScript"

# Session duration
SESSION_DURATION = 10.0


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
        
        # Session
        self.session_manager = session.SessionManager(duration=SESSION_DURATION)
        
        # Application state
        self.current_state = CALIBRATE_CENTER
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
        
        elif key_char == 'c':
            # Reset calibration
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
                # Remove trackbars (OpenCV doesn't support removal, but we can ignore them)
                print("HSV trackbars disabled")
        
        elif key_char == ' ' and self.current_state == READY:
            # Start session
            if self.calibration_state.is_complete():
                self.session_manager.start_session()
                self.current_state = RUNNING
                print("Session started!")
        
        elif key_char == ' ' and self.current_state == RESULT:
            # Retry from result screen
            self.current_state = READY
            print("Ready for new session")
        
        return True
    
    def _update_calibration_state(self):
        """Update calibration state machine."""
        if not self.calibration_state.is_complete():
            if self.calibration_state.center is None:
                self.current_state = CALIBRATE_CENTER
            else:
                self.current_state = CALIBRATE_RADIUS
        else:
            if self.current_state in [CALIBRATE_CENTER, CALIBRATE_RADIUS]:
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
        
        # Draw mode indicator (top-left)
        mode_text = f"Mode: {self.current_state}"
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
        
        # Draw circle overlay if calibrated
        if self.calibration_state.is_complete():
            center = self.calibration_state.center
            radius = self.calibration_state.radius
            cv2.circle(frame, center, int(radius), (255, 0, 0), 2)
            
            # Draw center point
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
        
        # State-specific overlays
        if self.current_state == CALIBRATE_CENTER:
            instruction = "Click to set circle CENTER"
            cv2.putText(frame, instruction, (w//2 - 150, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        elif self.current_state == CALIBRATE_RADIUS:
            instruction = "Click to set circle EDGE (radius)"
            cv2.putText(frame, instruction, (w//2 - 150, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        elif self.current_state == READY:
            instruction = "Press SPACE to start session"
            cv2.putText(frame, instruction, (w//2 - 150, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        elif self.current_state == RUNNING:
            # Session running overlays
            elapsed = self.session_manager.get_elapsed_time()
            remaining = self.session_manager.get_time_remaining()
            
            time_text = f"Time: {elapsed:.1f} / {SESSION_DURATION:.1f}s"
            cv2.putText(frame, time_text, (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            jitter_text = f"Jitter: {self.session_manager.current_jitter:.2f} px"
            cv2.putText(frame, jitter_text, (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            tremor_text = f"Tremor: {self.session_manager.tremor_score:.2f}"
            cv2.putText(frame, tremor_text, (10, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Check if session ended
            if not self.session_manager.is_active:
                self.current_state = RESULT
                self._save_session_result()
        
        elif self.current_state == RESULT:
            # Result screen
            metrics = self.session_manager.get_final_metrics()
            
            y_offset = h//2 - 80
            result_text = f"Session Complete!"
            cv2.putText(frame, result_text, (w//2 - 120, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            y_offset += 40
            tremor_final = f"Final Tremor Score: {metrics['tremor_score']:.2f}"
            cv2.putText(frame, tremor_final, (w//2 - 150, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            y_offset += 35
            stability = f"Stability: {metrics['inside_circle_pct']:.1f}%"
            cv2.putText(frame, stability, (w//2 - 100, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            y_offset += 40
            retry_text = "Press SPACE to retry"
            cv2.putText(frame, retry_text, (w//2 - 120, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw controls help (bottom)
        controls = "Controls: 'c'=reset calib, 't'=HSV tune, SPACE=start/retry, 'q'=quit"
        cv2.putText(frame, controls, (10, h - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    def _save_session_result(self):
        """Save session result to JSON file."""
        if not self.calibration_state.is_complete():
            return
        
        metrics = self.session_manager.get_final_metrics()
        
        session_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "duration_s": SESSION_DURATION,
            "circle_center": list(self.calibration_state.center),
            "circle_radius": round(self.calibration_state.radius, 2),
            "hsv_lower": self.hsv_lower.tolist(),
            "hsv_upper": self.hsv_upper.tolist(),
            **metrics
        }
        
        if utils.save_session(session_data):
            print(f"Session saved: Tremor Score = {metrics['tremor_score']:.2f}")
        else:
            print("Warning: Failed to save session")
    
    def run(self):
        """Main application loop."""
        self._setup_window()
        
        print("SteadyScript - Starting...")
        print("Instructions:")
        print("  1. Click to set circle center")
        print("  2. Click to set circle edge")
        print("  3. Press 't' to tune HSV if marker not detected")
        print("  4. Press SPACE to start session")
        
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
                circle_center = self.calibration_state.center if self.calibration_state.is_complete() else None
                circle_radius = self.calibration_state.radius if self.calibration_state.is_complete() else 0.0
                self.session_manager.update(self.marker_pos, circle_center, circle_radius)
            
            # Update Arduino LED based on marker position
            if self.arduino is not None and self.arduino.is_connected:
                if self.calibration_state.is_complete() and self.marker_pos is not None:
                    marker_inside = utils.point_in_circle(
                        self.marker_pos, 
                        self.calibration_state.center, 
                        self.calibration_state.radius
                    )
                    self.arduino.update(marker_inside)
                else:
                    # Marker not found or calibration incomplete - turn LED off
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