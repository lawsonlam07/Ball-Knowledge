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
from data.Coord import Coord 
from logic.perspective import FrameUnskew, TENNIS_COURT_LENGTH, TENNIS_COURT_SINGLES_WIDTH

# --- 3. CONFIG ---
VIDEO_PATH = os.path.join(root_dir, "tennis2.mp4")

# We render internally at high quality (720p height) so text is crisp.
# The window can be scaled down by the user or our auto-sizer below.
INTERNAL_HEIGHT = 720 
WINDOW_NAME = "Normalization Test"

# --- 4. DRAWING HELPERS ---
def draw_minimap(frame_obj, unskewer, target_height):
    padding = int(target_height * 0.05) 
    scale = (target_height - (padding * 2)) / TENNIS_COURT_LENGTH
    
    map_w = int(TENNIS_COURT_SINGLES_WIDTH * scale) + (padding * 2)
    map_h = target_height
    canvas = np.zeros((map_h, map_w, 3), dtype=np.uint8)
    
    def to_px(coord):
        px = padding + int(coord.y * scale)
        py = padding + int(coord.x * scale)
        return (px, py)

    cv2.rectangle(canvas, to_px(Coord(0,0)), to_px(Coord(TENNIS_COURT_LENGTH, TENNIS_COURT_SINGLES_WIDTH)), (200, 200, 200), 2)
    net_x = TENNIS_COURT_LENGTH / 2
    cv2.line(canvas, to_px(Coord(net_x, 0)), to_px(Coord(net_x, TENNIS_COURT_SINGLES_WIDTH)), (100, 100, 100), 2)

    dot_radius = int(target_height * 0.015)
    
    if frame_obj:
        if frame_obj.player1 and frame_obj.player1.pos:
            raw = [frame_obj.player1.pos.x, frame_obj.player1.pos.y]
            real = unskewer.unskew_coords_to_coords(raw, height_factor=0.0)
            cv2.circle(canvas, to_px(real), dot_radius, (0, 0, 255), -1) 
            cv2.putText(canvas, "P1", to_px(real), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        if frame_obj.player2 and frame_obj.player2.pos:
            raw = [frame_obj.player2.pos.x, frame_obj.player2.pos.y]
            real = unskewer.unskew_coords_to_coords(raw, height_factor=0.0)
            cv2.circle(canvas, to_px(real), dot_radius, (255, 0, 0), -1) 
            cv2.putText(canvas, "P2", to_px(real), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        if frame_obj.ball and frame_obj.ball.pos:
            raw = [frame_obj.ball.pos.x, frame_obj.ball.pos.y]
            real = unskewer.unskew_coords_to_coords(raw, height_factor=0.0) 
            cv2.circle(canvas, to_px(real), int(dot_radius*0.6), (0, 255, 255), -1) 

    return canvas

def draw_video_overlay(image, frame_obj, frame_count):
    if frame_obj:
        if frame_obj.court:
            c = frame_obj.court
            pts = np.array([
                [c.tl.x, c.tl.y], [c.tr.x, c.tr.y],
                [c.br.x, c.br.y], [c.bl.x, c.bl.y]
            ], np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [pts], True, (0, 255, 0), 2)

        if frame_obj.player1:
            cv2.circle(image, (int(frame_obj.player1.pos.x), int(frame_obj.player1.pos.y)), 12, (0, 0, 255), 3)
        if frame_obj.player2:
            cv2.circle(image, (int(frame_obj.player2.pos.x), int(frame_obj.player2.pos.y)), 12, (255, 0, 0), 3)
        if frame_obj.ball:
            cv2.circle(image, (int(frame_obj.ball.pos.x), int(frame_obj.ball.pos.y)), 8, (0, 255, 255), -1)
            
    # Scale font size based on image height so it's always readable
    font_scale = image.shape[0] / 500.0 
    text = f"FRAME: {frame_count}"
    cv2.putText(image, text, (40, 80), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 8) 
    cv2.putText(image, text, (40, 80), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2) 
    
    return image

# --- 5. MAIN ---
def main():
    print(f"🚀 Starting Test...")
    if not os.path.exists(VIDEO_PATH): return print("❌ Video not found")

    vision = VisionSystem(VIDEO_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH) 

    # Sync
    first = vision.getNextFrame()
    if not first: return
    cap.read() 
    
    # Setup Logic
    c = first.court
    corners = [[c.tl.x, c.tl.y], [c.tr.x, c.tr.y], [c.br.x, c.br.y], [c.bl.x, c.bl.y]]
    unskewer = FrameUnskew(corners)

    # Initialize Window
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    frame_count = 0

    while True:
        data = vision.getNextFrame()
        ret, frame = cap.read()
        
        if not data or not ret: break
        frame_count += 1

        # 1. Prepare Images
        frame = draw_video_overlay(frame, data, frame_count)
        
        h, w = frame.shape[:2]
        aspect_ratio = w / h
        new_w = int(INTERNAL_HEIGHT * aspect_ratio)
        frame_resized = cv2.resize(frame, (new_w, INTERNAL_HEIGHT))

        minimap = draw_minimap(data, unskewer, INTERNAL_HEIGHT)
        combined = np.hstack([frame_resized, minimap])

        # --- AUTO-FIX ASPECT RATIO (ON FIRST FRAME ONLY) ---
        if frame_count == 1:
            comb_h, comb_w = combined.shape[:2]
            # If the image is excessively large (>1400px wide), scale the window down
            # but KEEP the aspect ratio correct so it isn't squished.
            target_w = comb_w
            target_h = comb_h
            
            if target_w > 1400:
                ratio = 1400 / target_w
                target_w = 1400
                target_h = int(target_h * ratio)
            
            # Force the window to this size
            cv2.resizeWindow(WINDOW_NAME, target_w, target_h)

        # 2. Show
        cv2.imshow(WINDOW_NAME, combined)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()