import cv2
import numpy as np
from collections import deque

def is_contour_circle(cnt):
    """
    Determines if a contour is a circle based on 'circularity'.
    Circularity = 4 * pi * (Area / Perimeter^2)
    Perfect circle == 1.0. 
    We accept 0.7 to 1.2 to account for camera angle/noise.
    """
    perimeter = cv2.arcLength(cnt, True)
    area = cv2.contourArea(cnt)
    
    if perimeter == 0:
        return False, 0

    circularity = 4 * np.pi * (area / (perimeter * perimeter))
    
    # Check if circularity is within range
    if 0.7 < circularity < 1.3:
        return True, circularity
    return False, circularity

def track_colored_circle(color_lower, color_upper):
    cap = cv2.VideoCapture(0)
    
    # --- TRAIL & SENSITIVITY SETUP ---
    # Store points for the trail
    points = deque(maxlen=64)
    
    cv2.namedWindow('Tracker')
    cv2.namedWindow('Mask')
    def nothing(x): pass
    
    # Slider to smooth out the drawing line
    cv2.createTrackbar('Smoothing', 'Tracker', 5, 20, nothing)
    
    # Initialize smoothing factor with default value
    smoothing_factor = 5

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1) # Mirror view
        
        # Get trackbar position (with fallback to default)
        try:
            smoothing_factor = max(1, cv2.getTrackbarPos('Smoothing', 'Tracker'))
        except:
            smoothing_factor = 5

        # 1. Color Masking
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, color_lower, color_upper)
        
        # Clean noise
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # 2. Find Contours
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        center = None
        is_circle = False
        shape_label = "Undetermined"

        if len(contours) > 0:
            # Get largest contour (the main object)
            c = max(contours, key=cv2.contourArea)
            
            # Filter out tiny noise (area must be decent size)
            if cv2.contourArea(c) > 500:
                
                # 3. Shape Recognition
                is_circle, score = is_contour_circle(c)
                
                # Calculate center
                M = cv2.moments(c)
                if M["m00"] > 0:
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # VISUALIZATION:
                # If it's a circle, draw a Circle UI. If not, draw a Rectangle UI.
                if is_circle:
                    shape_label = f"Circle (Conf: {score:.2f})"
                    # Draw minimum enclosing circle
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                else:
                    shape_label = f"Not Circle (Conf: {score:.2f})"
                    # Draw bounding box for non-circles
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # Display label
                cv2.putText(frame, shape_label, (10, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 4. Map Movement (Only if it IS a Circle)
        if is_circle and center is not None:
            points.appendleft(center)
        else:
            # Optional: If you want the trail to break when the circle is lost, 
            # uncomment the line below. Otherwise, it remembers the last position.
            # points.appendleft(None)
            pass

        # Draw the Trail
        for i in range(1, len(points)):
            if points[i - 1] is None or points[i] is None:
                continue
            
            # Apply smoothing sensitivity
            if i % smoothing_factor != 0:
                continue

            thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
            cv2.line(frame, points[i - 1], points[i], (0, 255, 0), thickness)

        cv2.imshow('Tracker', frame)
        cv2.imshow('Mask', mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Example: Blue
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])

    track_colored_circle(lower_blue, upper_blue)