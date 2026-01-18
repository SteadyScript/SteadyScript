"""
Arduino LED control module for SteadyScript.
Controls a green LED based on marker position relative to circle.
"""

import serial
import time
from typing import Optional

class ArduinoLEDController:
    """Manages Arduino LED state based on marker position."""
    
    def __init__(self, port: str, baud_rate: int = 9600):
        self.port = port
        self.baud_rate = baud_rate
        self.ser: Optional[serial.Serial] = None
        self.is_connected = False
        self.current_state = False  # False = OFF, True = ON
        self.last_update_time = 0   # For heartbeat (syncing)
        
        self._connect()
    
    def _connect(self):
        """Attempt to connect to Arduino."""
        try:
            # Open the Serial port
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            
            # CRITICAL: Wait for Arduino to reboot after serial connection
            # If we send data too soon, the Arduino is still booting and will miss it.
            time.sleep(2.0) 
            
            self.is_connected = True
            print(f"Arduino connected on {self.port}")
            
            # Boot-up flash test
            print("Arduino boot test: LED ON...")
            self._send_state(True, force=True)
            time.sleep(1.0)
            self._send_state(False, force=True)
            print("Arduino boot test: Complete.")
            
        except serial.SerialException as e:
            self.is_connected = False
            print(f"Warning: Could not connect to Arduino on {self.port}")
            print(f"  Error: {e}")
        except Exception as e:
            self.is_connected = False
            print(f"Warning: Arduino connection error: {e}")
    
    def _send_state(self, state: bool, force: bool = False):
        """
        Send LED state to Arduino.
        Args:
            state: True (ON) or False (OFF)
            force: If True, sends command even if state hasn't changed.
        """
        if not self.is_connected or self.ser is None:
            return
        
        try:
            if state:
                self.ser.write(b'1')
            else:
                self.ser.write(b'0')
            
            # Flush ensures the bytes leave the computer buffer immediately
            self.ser.flush()
            
            self.current_state = state
            self.last_update_time = time.time()
            
        except Exception as e:
            print(f"Error sending to Arduino: {e}")
            self.is_connected = False
    
    def update(self, marker_inside_circle: bool):
        """
        Update LED state based on marker position.
        Includes a 'heartbeat' to resend the signal every 1 second
        to fix synchronization bugs.
        """
        if not self.is_connected:
            return
            
        current_time = time.time()
        
        # We send data if:
        # 1. The state (Inside/Outside) has changed
        # 2. OR it has been >1 second since we last told the Arduino what to do (Heartbeat)
        state_changed = (marker_inside_circle != self.current_state)
        time_elapsed = (current_time - self.last_update_time > 1.0)
        
        if state_changed or time_elapsed:
            self._send_state(marker_inside_circle)

    def close(self):
        """Close serial connection."""
        if self.ser is not None and self.ser.is_open:
            try:
                self._send_state(False, force=True)
                time.sleep(0.1)
                self.ser.close()
                print("Arduino connection closed")
            except Exception:
                pass
            finally:
                self.is_connected = False