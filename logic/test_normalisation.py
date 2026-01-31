import cv2
import numpy as np
import sys
import os

# --- 1. PATHS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

# --- 2. IMPORTS ---
from vision import VisionSystem

# --- 3. CONFIG ---
VIDEO_PATH = os.path.join(root_dir, "tennis2.mp4")
WINDOW_HEIGHT = 700  # Fixed height for the combined window

# --- 4. LOGIC ---
TENNIS_COURT_WIDTH = 8.23
TENNIS_COURT_LENGTH = 23.77

class FrameUnskew:
    def __init__(self, corners):
        src_points = np.array(corners, dtype="float32")
        # Standard Mapping: TL(0,0), TR(W,0), BR(W,L), BL(0,L)
        dst_points = np.array([
            [0, 0], [TENNIS_COURT_WIDTH, 0],
            [TENNIS_COURT_WIDTH, TENNIS_COURT_LENGTH], [0, TENNIS_COURT_LENGTH]
        ], dtype="float32")
        self.matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    def unskew(self, x, y):
        pts = np.array([[[float(x), float(y)]]], dtype="float32")
        res = cv2.perspectiveTransform(pts, self.matrix)[0][0]
        return (float(res[0]), float(res[1]))

# --- 5. VISUALIZATION HELPERS ---
def draw_minimap(frame_obj, unskewer, target_height):
    """Draws the minimap scaled to match the video height exactly."""
    padding = 40
    # Calculate scale so the court fits the target height
    scale = (target_height - (padding * 2)) / TENNIS_COURT_LENGTH
    
    map_w = int(TENNIS_COURT_WIDTH * scale) + (padding * 2)
    map_h = target_height
    
    # Dark background for minimap
    canvas = np.zeros((map_h, map_w, 3), dtype=np.uint8)
    
    def to_px(rx, ry):
        return (padding + int(rx * scale), padding + int(ry * scale))

    # Draw Court (White Outline)
    cv2.rectangle(canvas, to_px(0, 0), to_px(TENNIS_COURT_WIDTH, TENNIS_COURT_LENGTH), (200, 200, 200), 2)
    # Net (Grey Line)
    net_y = TENNIS_COURT_LENGTH / 2
    cv2.line(canvas, to_px(0, net_y), to_px(TENNIS_COURT_WIDTH, net_y), (100, 100, 100), 1)

    # Draw Data
    if frame_obj:
        if frame_obj.player1:
            rx, ry = unskewer.unskew(frame_obj.player1.pos.x, frame_obj.player1.pos.y)
            cv2.circle(canvas, to_px(rx, ry), 10, (0, 0, 255), -1) # Red
            cv2.putText(canvas, "P1", to_px(rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        if frame_obj.player2:
            rx, ry = unskewer.unskew(frame_obj.player2.pos.x, frame_obj.player2.pos.y)
            cv2.circle(canvas, to_px(rx, ry), 10, (255, 0, 0), -1) # Blue
            cv2.putText(canvas, "P2", to_px(rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        if frame_obj.ball:
            rx, ry = unskewer.unskew(frame_obj.ball.pos.x, frame_obj.ball.pos.y)
            cv2.circle(canvas, to_px(rx, ry), 6, (0, 255, 255), -1) # Yellow

    return canvas

def draw_video_overlay(image, frame_obj, frame_count):
    """Draws raw tracking dots on the original video."""
    if frame_obj:
        if frame_obj.player1:
            p = (int(frame_obj.player1.pos.x), int(frame_obj.player1.pos.y))
            cv2.circle(image, p, 15, (0, 0, 255), 3)
        if frame_obj.player2:
            p = (int(frame_obj.player2.pos.x), int(frame_obj.player2.pos.y))
            cv2.circle(image, p, 15, (255, 0, 0), 3)
        if frame_obj.ball:
            p = (int(frame_obj.ball.pos.x), int(frame_obj.ball.pos.y))
            cv2.circle(image, p, 10, (0, 255, 255), -1)
            
    cv2.putText(image, f"Frame: {frame_count}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    return image

# --- 6. MAIN ---
def main():
    print(f"🚀 Starting Unified Test View...")
    if not os.path.exists(VIDEO_PATH): return print("❌ Video not found")

    vision = VisionSystem(VIDEO_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH) # Open video again for display syncing

    # Setup Unskewer
    first = vision.getNextFrame()
    if not first: return
    c = first.court
    unskewer = FrameUnskew([[c.tl.x, c.tl.y], [c.tr.x, c.tr.y], [c.br.x, c.br.y], [c.bl.x, c.bl.y]])

    frame_count = 0

    while True:
        # 1. Get Data & Image
        data = vision.getNextFrame()
        ret, frame = cap.read()
        if not data or not ret: break
        frame_count += 1

        # 2. Draw Overlay on Original Frame
        frame = draw_video_overlay(frame, data, frame_count)

        # 3. Resize Video to Target Height (Maintain Aspect Ratio)
        h, w = frame.shape[:2]
        aspect_ratio = w / h
        new_w = int(WINDOW_HEIGHT * aspect_ratio)
        frame_resized = cv2.resize(frame, (new_w, WINDOW_HEIGHT))

        # 4. Generate Minimap (Same Height)
        minimap = draw_minimap(data, unskewer, WINDOW_HEIGHT)

        # 5. Stitch Together (Side-by-Side)
        combined_view = np.hstack([frame_resized, minimap])

        # 6. Show
        cv2.imshow("Normalization Test (Video + Minimap)", combined_view)
        
        # 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()