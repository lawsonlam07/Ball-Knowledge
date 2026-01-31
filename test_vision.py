import cv2
import sys
import os
from vision import process_video

# --- CONFIGURATION ---
VIDEO_PATH = "tennis.mp4"  # <--- REPLACE WITH YOUR VIDEO PATH
SHOW_VIDEO = True         # Set to False to just print console logs

def draw_court(frame, court):
    """Draws the court lines based on the 4 corner coordinates."""
    if not court: return
    
    # Extract points
    pts = [
        (court.tl.x, court.tl.y),
        (court.tr.x, court.tr.y),
        (court.br.x, court.br.y),
        (court.bl.x, court.bl.y)
    ]
    
    # Draw lines connecting the 4 corners (Green)
    for i in range(4):
        p1 = pts[i]
        p2 = pts[(i+1) % 4] # Wrap around to 0
        cv2.line(frame, p1, p2, (0, 255, 0), 2)
    
    # Draw corner labels
    for i, name in enumerate(["TL", "TR", "BR", "BL"]):
        cv2.putText(frame, name, pts[i], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def draw_players(frame, players):
    """Draws player positions and IDs."""
    for p in players:
        # Draw circle at feet (Red)
        cv2.circle(frame, (p.pos.x, p.pos.y), 10, (0, 0, 255), -1)
        # Draw Name/ID above
        cv2.putText(frame, p.name, (p.pos.x - 10, p.pos.y - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

def draw_ball(frame, ball):
    """Draws the ball position."""
    if ball:
        # Draw ball (Yellow)
        cv2.circle(frame, (ball.pos.x, ball.pos.y), 8, (0, 255, 255), -1)
        cv2.putText(frame, "BALL", (ball.pos.x + 10, ball.pos.y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Video not found at {VIDEO_PATH}")
        return

    # 1. Start the Generator
    print(f"Starting pipeline on {VIDEO_PATH}...")
    pipeline = process_video(VIDEO_PATH)

    # 2. Open Video Capture for Visualization (Parallel Read)
    # We open the video again here just to draw on the frames for the user
    cap_vis = cv2.VideoCapture(VIDEO_PATH)

    try:
        for frame_count, players, ball, court in pipeline:
            
            # Read the corresponding frame from our visualization capture
            ret, frame = cap_vis.read()
            if not ret: break

            # --- DRAWING LOGIC ---
            draw_court(frame, court)
            draw_players(frame, players)
            draw_ball(frame, ball)

            # Add Frame Count UI
            cv2.putText(frame, f"Frame: {frame_count}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # --- CONSOLE LOGGING (Sanity Check) ---
            ball_status = "DETECTED" if ball else "MISSING"
            print(f"Frame {frame_count}: Players={len(players)} | Ball={ball_status}")

            if SHOW_VIDEO:
                cv2.imshow("Tennis Pipeline Test", frame)
                # Press 'q' to quit early
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
    finally:
        cap_vis.release()
        cv2.destroyAllWindows()
        print("\nTest Complete.")

if __name__ == "__main__":
    main()