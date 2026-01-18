"""
Arduino LED control module for SteadyScript.
Controls a green LED based on marker position relative to circle.
"""

import serial
import time
from typing import Optional


class ArduinoLEDController:
    """Manages Arduino LED state based on marker position."""
    
    def __init__(self, port: str = 'COM3', baud_rate: int = 9600):
        """
        Initialize Arduino LED controller.
        
        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/tty.usbmodem...' on Mac/Linux)
            baud_rate: Serial communication baud rate (default 9600)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.ser: Optional[serial.Serial] = None
        self.is_connected = False
        self.current_state = False  # False = OFF, True = ON
        
        # Try to connect
        self._connect()
    
    def _connect(self):
        """Attempt to connect to Arduino."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            self.is_connected = True
            print(f"Arduino connected on {self.port}")
            
            # Boot-up test: Turn LED ON for 2 seconds to verify connection
            print("Arduino boot-up test: LED should turn ON for 2 seconds...")
            self._send_state(True)
            time.sleep(2)
            self._send_state(False)
            print("Boot-up test complete. LED should now be OFF.")
            self.current_state = False
        except serial.SerialException as e:
            self.is_connected = False
            print(f"Warning: Could not connect to Arduino on {self.port}")
            print(f"  Error: {e}")
            print(f"  LED feedback will be disabled. Check your port name.")
        except Exception as e:
            self.is_connected = False
            print(f"Warning: Arduino connection error: {e}")
    
    def _send_state(self, state: bool):
        """
        Send LED state to Arduino.
        
        Args:
            state: True to turn ON, False to turn OFF
        """
        if not self.is_connected or self.ser is None:
            return
        
        try:
            if state:
                self.ser.write(b'1')  # Turn ON
                self.ser.flush()  # Ensure data is sent immediately
            else:
                self.ser.write(b'0')  # Turn OFF
                self.ser.flush()  # Ensure data is sent immediately
            self.current_state = state
        except Exception as e:
            print(f"Error sending to Arduino: {e}")
            self.is_connected = False
    
    def update(self, marker_inside_circle: bool):
        """
        Update LED state based on marker position.
        
        Args:
            marker_inside_circle: True if marker is inside circle, False otherwise
        """
        if not self.is_connected:
            return
        
        # Only update if state changed (avoid spamming serial)
        if marker_inside_circle != self.current_state:
            self._send_state(marker_inside_circle)
    
    def close(self):
        """Close serial connection."""
        if self.ser is not None and self.ser.is_open:
            try:
                self._send_state(False)  # Turn off LED before closing
                time.sleep(0.1)
                self.ser.close()
                print("Arduino connection closed")
            except Exception as e:
                print(f"Error closing Arduino connection: {e}")
            finally:
                self.is_connected = False
