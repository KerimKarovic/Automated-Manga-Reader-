import cv2
import numpy as np

def detect_panels(image_path: str):
    # Read the image from the given path.
    image = cv2.imread(image_path)
    if image is None:
        return []  # Return empty list if image could not be read.
    
    # Convert image to grayscale.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to invert the image for better contour detection.
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours in the thresholded image.
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    panels = []
    # Iterate over each contour to get bounding rectangles.
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter out small regions that are unlikely to be panels.
        if w > 50 and h > 50:
            panels.append((x, y, w, h))
    
    # Sort panels in reading order (this logic might be adjusted as needed).
    panels_sorted = sorted(panels, key=lambda b: (-b[0], b[1]))
    return panels_sorted
