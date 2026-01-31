import cv2
import sys

# CONFIG
VIDEO_PATH = "tennis2_highres.mp4"

# Global State
points = []
corner_names = ["Top Left (TL)", "Top Right (TR)", "Bottom Right (BR)", "Bottom Left (BL)"]

def click_event(event, x, y, flags, params):
    global points
    
    # 1. LEFT CLICK: Record a Point
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) >= 4:
            print("Already captured 4 points. Right click to reset.")
            return

        # Store point
        points.append((x, y))
        current_idx = len(points) - 1
        name = corner_names[current_idx]
        print(f"✅ Captured {name}: {x}, {y}")

        # Draw visual feedback
        img = params['img_display']
        cv2.circle(img, (x, y), 8, (0, 0, 255), -1) # Red Dot
        cv2.putText(img, f"{current_idx+1}. {name}", (x+15, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow(params['window_name'], img)

        # Check if done
        if len(points) == 4:
            print("\n" + "="*40)
            print("COPY THIS INTO vision.py:")
            print("="*40)
            print(f"tl=Coord({points[0][0]}, {points[0][1]}),")
            print(f"tr=Coord({points[1][0]}, {points[1][1]}),")
            print(f"br=Coord({points[2][0]}, {points[2][1]}),")
            print(f"bl=Coord({points[3][0]}, {points[3][1]})")
            print("="*40 + "\n")
            print("Press 'q' to close.")

    # 2. RIGHT CLICK: Reset/Undo
    elif event == cv2.EVENT_RBUTTONDOWN:
        print("🔄 Resetting points...")
        points.clear()
        # Restore clean image
        params['img_display'][:] = params['img_clean'][:]
        cv2.imshow(params['window_name'], params['img_display'])

def main():
    # Load Video
    cap = cv2.VideoCapture(VIDEO_PATH)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(f"Error: Could not read {VIDEO_PATH}")
        return

    # Setup Windows & Images
    window_name = "Calibration (Resize Me!)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    # Keep a clean copy for resetting
    img_clean = frame.copy()
    img_display = frame.copy()

    # Register Mouse Callback
    callback_params = {
        'img_display': img_display, 
        'img_clean': img_clean,
        'window_name': window_name
    }
    cv2.setMouseCallback(window_name, click_event, callback_params)

    print("------------------------------------------------")
    print("INSTRUCTIONS:")
    print("1. Click the 4 corners in this order:")
    print("   TOP-LEFT -> TOP-RIGHT -> BOTTOM-RIGHT -> BOTTOM-LEFT")
    print("2. RIGHT CLICK to clear points and restart.")
    print("3. Press 'q' to quit.")
    print("------------------------------------------------")

    while True:
        # Overlay instruction text
        if len(points) < 4:
            next_pt = corner_names[len(points)]
            # Draw a black rectangle background for text readability
            cv2.rectangle(img_display, (0, 0), (600, 50), (0, 0, 0), -1)
            cv2.putText(img_display, f"NEXT CLICK: {next_pt}", (20, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        else:
            cv2.rectangle(img_display, (0, 0), (600, 50), (0, 0, 0), -1)
            cv2.putText(img_display, "DONE! Press 'q' to exit", (20, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow(window_name, img_display)
        
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()