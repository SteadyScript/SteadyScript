# SteadyScript

A real-time computer vision tremor training prototype that tracks a colored marker on a pen and measures hand stability during a "Hold Steady" exercise.

## Overview

SteadyScript is a minimal, robust tremor assessment tool that:
- Uses webcam feed to track a colored marker attached to a pen
- Allows click-based calibration of a circular target region
- Computes real-time tremor/jitter scores during timed hold sessions
- Saves session results to JSON for analysis

## Setup

### Prerequisites

- Python 3.7+
- Webcam (USB or built-in)
- OpenCV and NumPy

### Installation

1. Install required packages:
```bash
pip install opencv-python numpy pyserial
```

2. Verify installation:
```bash
python -c "import cv2, numpy, serial; print('OK')"
```

## Hardware Setup

### Camera Positioning

- **Mount camera facing down** over a stable surface (desk/table)
- Ensure the camera has a clear view of the workspace
- Keep the paper/target surface stable and well-lit
- Recommended height: 30-50cm above the surface

### Marker Attachment

1. **Choose a bright, distinct color** for your marker:
   - Bright blue tape/ball (default - works well in most lighting)
   - Bright green, orange, or yellow (good alternatives)
   - Avoid colors that match your background or skin tone

2. **Attach marker to pen**:
   - Use a small piece of colored tape or a small colored ball
   - Attach near the pen tip for best visibility
   - Marker should be 5-15mm in size (visible but not too large)
   - Ensure marker is securely attached and won't fall off

3. **Test marker visibility**:
   - Run the app and press 't' to enable HSV tuning
   - Adjust trackbars until the marker is clearly visible in the mask window
   - The marker should appear as a white blob in the mask

## Running the Application

### Start the App

```bash
python main.py
```

The application will:
1. Open your webcam feed in a window titled "SteadyScript"
2. Display instructions on screen
3. Wait for calibration

### Mode Selection

The app starts with a mode selection menu. Choose your training mode:

- **Press '1'** for **HOLD mode** (Level 1) - Hold the pen steady inside a circle
- **Press '2'** for **FOLLOW mode** (Level 2) - Follow a moving target dot smoothly

### HOLD Mode (Level 1) - User Flow

#### Step 1: Calibrate Circle Center

- **Click once** on the center of your target circle (printed or drawn on paper)
- The app will show "Click to set circle CENTER"
- After clicking, proceed to Step 2

#### Step 2: Calibrate Circle Edge

- **Click once** on any point on the edge of the circle
- The app will show "Click to set circle EDGE (radius)"
- The system calculates the radius automatically
- After clicking, you'll enter READY mode

#### Step 3: Start HOLD Session

- Press **SPACE** to start a 10-second hold session
- Keep the marker inside the circle
- View real-time tremor metrics
- Session ends automatically after 10 seconds

### FOLLOW Mode (Level 2) - User Flow

#### Step 1: Start FOLLOW Session

- No calibration needed for FOLLOW mode
- Press **SPACE** to start a 20-second follow session
- A green target dot will appear and move in a circular path

#### Step 2: Follow the Target

- **Move your pen smoothly** to follow the green target dot
- The target moves in a circular path (one full loop ~8 seconds)
- Focus on smooth, controlled movement rather than speed

#### Step 3: View Results

- Session ends automatically after 20 seconds
- View your Movement Quality Score (0-100)
- Metrics include:
  - **Jitter (p95)**: Tremor-like micro-instability during movement
  - **Jerk (p95)**: Smoothness measure (lower = smoother)
  - **Wobble Ratio**: Path efficiency (how direct vs. wobbly)
  - **Movement Quality Score**: Combined metric (higher = better)

#### Step 3: Tune Marker Detection (Optional)

If the marker is not being detected:

1. Press **'t'** to toggle HSV trackbars
2. A "Mask (HSV Tuning)" window will appear showing the color mask
3. Adjust the trackbars:
   - **Lower H/S/V**: Lower bounds for hue, saturation, value
   - **Upper H/S/V**: Upper bounds for hue, saturation, value
4. Watch the mask window - the marker should appear as a white blob
5. Press **'t'** again to hide trackbars when done

**Default HSV for blue marker:**
- Lower: [100, 50, 50]
- Upper: [130, 255, 255]

**Tips for tuning:**
- If marker is too small or missing: Lower the "Lower V" (value) threshold
- If too much noise: Increase "Lower S" (saturation) threshold
- If marker color is different: Adjust "Lower H" and "Upper H" (hue range)

#### Step 4: Start Session

- Ensure marker is detected (should show "Marker: OK" in green)
- Position the pen so the marker is inside the calibrated circle
- Press **SPACE** to start a 10-second hold session

#### Step 5: Hold Steady

During the session:
- **Keep the marker inside the circle** for best stability score
- The app displays:
  - Elapsed time
  - Live jitter (instantaneous position deviation)
  - Tremor score (weighted combination of average and 95th percentile jitter)
  - Inside/outside circle indicator

#### Step 6: View Results

After 10 seconds:
- Session ends automatically
- Final tremor score and stability percentage are displayed
- Results are saved to `data/sessions.json`
- Press **SPACE** to start a new session

## Arduino LED Feedback (Optional)

If you have an Arduino with a green LED connected, you can enable real-time visual feedback:

### Arduino Setup

1. **Connect Arduino** to your computer via USB
2. **Upload Arduino code** (see example below)
3. **Find your Arduino port**:
   - Windows: Usually `COM3`, `COM4`, etc. (check Device Manager)
   - Mac/Linux: Usually `/dev/tty.usbmodem...` or `/dev/ttyACM0`

### Arduino Code Example

```cpp
void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);  // LED on pin 13 (or your LED pin)
  digitalWrite(13, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') {
      digitalWrite(13, HIGH);  // Turn ON
    } else if (command == '0') {
      digitalWrite(13, LOW);   // Turn OFF
    }
  }
}
```

### Behavior

- **Green LED ON**: Marker is inside the calibrated circle
- **Green LED OFF**: Marker is outside the circle or not detected

The LED updates in real-time as you move the pen, providing instant visual feedback during calibration and sessions.

## Keyboard Controls

| Key | Action |
|-----|--------|
| **'1'** | Switch to HOLD mode (Level 1) |
| **'2'** | Switch to FOLLOW mode (Level 2) |
| **'c'** | Reset calibration (HOLD mode only) |
| **'t'** | Toggle HSV trackbars for marker tuning |
| **SPACE** | Start session (when ready) or retry (after results) |
| **'q'** | Quit application |

## Understanding the Metrics

### Tremor Score

The primary metric combining:
- **70% weight**: 95th percentile jitter (captures spikes/outliers)
- **30% weight**: Average jitter (overall stability)

**Lower is better** - a score of 0.0 would indicate perfect stillness.

### Stability Percentage

Percentage of time the marker was inside the calibrated circle during the session.

**Higher is better** - 100% means the marker never left the circle.

### Jitter

Instantaneous deviation from smoothed position (in pixels). Measured as the distance between raw marker position and a moving average of recent positions.

## Session Data

Results are saved to `CompVis/data/sessions.json` with the following format:

**HOLD Mode Session:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "type": "HOLD",
  "duration_s": 10.0,
  "circle_center": [320, 240],
  "circle_radius": 50.0,
  "hsv_lower": [100, 50, 50],
  "hsv_upper": [130, 255, 255],
  "avg_jitter": 2.5,
  "p95_jitter": 4.2,
  "tremor_score": 3.8,
  "inside_circle_pct": 85.5,
  "frames_total": 300,
  "frames_marker_found": 295
}
```

**FOLLOW Mode Session:**
```json
{
  "timestamp": "2024-01-15T10:35:00Z",
  "type": "FOLLOW",
  "duration_s": 20.0,
  "hsv_lower": [100, 50, 50],
  "hsv_upper": [130, 255, 255],
  "avg_jitter": 3.2,
  "p95_jitter": 5.1,
  "avg_jerk": 45.3,
  "p95_jerk": 78.5,
  "wobble_ratio": 0.25,
  "movement_quality_score": 72.5,
  "avg_target_error": 12.3,
  "p95_target_error": 18.7,
  "frames_total": 600,
  "frames_marker_found": 585
}
```

## Troubleshooting

### Camera Not Opening

- Check that no other application is using the camera
- Try changing camera index in `main.py`: `cv2.VideoCapture(1)` instead of `0`
- Verify camera permissions on your system

### Marker Not Detected

1. Ensure good lighting (avoid shadows, glare, or too dim conditions)
2. Press 't' to enable HSV tuning and adjust trackbars
3. Check that marker color contrasts with background
4. Verify marker is large enough (at least 5mm visible)
5. Try a different marker color if current one doesn't work

### Calibration Issues

- Make sure you click exactly on the center, then on the edge
- The circle should be clearly visible in the camera feed
- Press 'c' to reset and try again

### Poor Tremor Scores

- Ensure stable camera mount (no vibration)
- Keep paper/target surface still
- Use consistent lighting conditions
- Verify marker is securely attached to pen

## Project Structure

```
SteadyScript/
├── main.py              # Main entry point and application loop
├── cv_tracker.py        # Marker detection using HSV segmentation
├── calibration.py       # Mouse click calibration handlers
├── session.py           # Session management and tremor computation
├── utils.py             # Helper functions (JSON, smoothing, math)
├── arduino_led.py       # Arduino LED control module
├── data/
│   └── sessions.json    # Session results storage
└── README.md            # This file
```

## Technical Details

### Marker Detection Pipeline

1. Convert BGR frame to HSV color space
2. Apply color thresholding with configurable bounds
3. Morphological operations (open + close) to reduce noise
4. Find contours and filter by minimum area
5. Compute centroid of largest contour using moments

### Tremor Computation

1. Maintain rolling window of marker positions (last 1 second)
2. Compute smoothed position using moving average (window=10 frames)
3. Calculate instantaneous jitter = distance(raw, smoothed)
4. Track jitter values in rolling window
5. Compute metrics:
   - Average jitter (mean)
   - 95th percentile jitter (outlier detection)
   - Final tremor score = 0.7 × p95 + 0.3 × avg

## Future Levels

Level 1 provides the foundation for:
- **Level 2**: Multiple targets (A/B pattern), Arduino LED feedback
- **Level 3**: Advanced analytics, progress tracking, gamification
- **Level 4**: ML-based tremor classification and personalized training

## License

This project is part of the SteadyScript tremor training system.

## Support

For issues or questions, check the troubleshooting section above or review the code comments for implementation details.
