import cv2
import os
import sys

# Import the specific function we want to test
from vision import get_court_calibration

# --- CONFIG ---
VIDEO_PATH = "tennis2.mp4"
DISPLAY_WIDTH = 1280  # Target width for the popup

def draw_debug_court(frame, court):
    """
    Draws the court with high-visibility markers for debugging.
    """
    if not court:
        print("❌ No court data to draw.")
        return

    # 1. Define corners
    corners = {
        "TL": (court.tl.x, court.tl.y),
        "TR": (court.tr.x, court.tr.y),
        "BR": (court.br.x, court.br.y),
        "BL": (court.bl.x, court.bl.y)
    }

    # 2. Print coordinates to console for verification
    print("\n--- DETECTED COORDINATES ---")
    for name, (x, y) in corners.items():
        print(f"{name}: ({x}, {y})")
        
        # Draw a big red circle at each corner
        cv2.circle(frame, (x, y), 20, (0, 0, 255), -1)
        # Draw the label (White with Black outline for readability)
        cv2.putText(frame, name, (x - 20, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 5)
        cv2.putText(frame, name, (x - 20, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

    # 3. Draw connection lines (Blue)
    pts = [corners["TL"], corners["TR"], corners["BR"], corners["BL"]]
    for i in range(4):
        p1 = pts[i]
        p2 = pts[(i+1) % 4]
        cv2.line(frame, p1, p2, (255, 0, 0), 4)

def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Video not found at {VIDEO_PATH}")
        return

    # 1. Grab just the first frame
    print(f"Reading first frame from {VIDEO_PATH}...")
    cap = cv2.VideoCapture(VIDEO_PATH)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error: Could not read frame from video.")
        return

    # 2. Run the isolated calibration function
    print("Sending frame to Claude for calibration...")
    try:
        court = get_court_calibration(frame)
        print("✅ Calibration returned successfully.")
    except Exception as e:
        print(f"❌ Calibration Error: {e}")
        court = None 

    # 3. Visualize on the ORIGINAL high-res frame
    draw_debug_court(frame, court)
    
    # Save a copy to disk (Full Resolution)
    cv2.imwrite("debug_court_output.jpg", frame)
    print("Saved full-res result to 'debug_court_output.jpg'")

    # 4. Create a SMALLER copy for display only
    height, width = frame.shape[:2]
    scale = DISPLAY_WIDTH / width
    new_height = int(height * scale)
    
    # Resize image to fit screen
    display_frame = cv2.resize(frame, (DISPLAY_WIDTH, new_height))
    
    window_name = "Court Detection Debug (Resized)"
    cv2.imshow(window_name, display_frame)
    
    print("\nWindow open. Press 'q' or 'ESC' to close.")
    
    # 5. Loop specifically waiting for Q or ESC
    while True:
        key = cv2.waitKey(100) & 0xFF
        
        # Close only if 'q' (113) or 'ESC' (27) is pressed
        if key == ord('q') or key == 27:
            break
            
        # Safety check: if you closed the window with the mouse X button
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()