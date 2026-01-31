import cv2
import base64
import json
import os
import re
from ultralytics import YOLO
import supervision as sv
import anthropic

# IMPORT YOUR CLASSES
# (Adjust these imports if your files are named differently)
from data.Coord import Coord
from data.Ball import Ball
from data.Court import Court
from data.Player import Player

# --- CONFIG ---
MODEL_NAME = 'yolov8m.pt' 
CONFIDENCE_THRESHOLD = 0.25

def extract_json_from_text(text):
    """Helper to clean Claude's output"""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match: return match.group(0)
    return text

def get_court_calibration(frame):
    """
    Sends Frame 1 to Claude to get the RAW pixel corners.
    Returns a Court object.
    """
    print("🤖 Calibrating Court via Claude...")
    
    # Resize to save bandwidth/tokens
    height, width = frame.shape[:2]
    scale = 640 / width
    small_frame = cv2.resize(frame, (640, int(height * scale)))
    
    _, buffer = cv2.imencode(".jpg", small_frame)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    prompt = """
    Identify the pixel coordinates of the 4 corners of the SINGLES tennis court.
    Return JSON with keys "tl", "tr", "br", "bl". Format: [x, y].
    """

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}},
                    {"type": "text", "text": prompt}
                ]
            }]
        )
        
        # Parse JSON
        data = json.loads(extract_json_from_text(message.content[0].text))
        
        # Scale back up to original resolution
        def make_coord(key):
            x, y = data[key]
            return Coord(int(x / scale), int(y / scale))

        return Court(
            tl=make_coord("tl"),
            tr=make_coord("tr"),
            br=make_coord("br"),
            bl=make_coord("bl")
        )

    except Exception as e:
        print(f"⚠️ Calibration failed: {e}")
        # Fallback: Return a dummy court or raise error
        raise ValueError("Could not detect court corners.")

def process_video(source_path: str):
    """
    Yields a tuple: (frame_number, [Player], Ball, Court)
    """
    cap = cv2.VideoCapture(source_path)
    model = YOLO(MODEL_NAME)
    tracker = sv.ByteTrack()

    # 1. GET STATIC COURT DATA (Once)
    ret, first_frame = cap.read()
    if not ret: raise ValueError("Video empty")
    
    raw_court = get_court_calibration(first_frame)
    print(f"✅ Court Detected: {raw_court.tl.x}, {raw_court.tl.y} ...")
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1
        
        # 2. DETECT OBJECTS
        results = model(frame, classes=[0, 32], conf=CONFIDENCE_THRESHOLD, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)
        
        # 3. PROCESS PLAYERS
        players = []
        person_detections = detections[detections.class_id == 0]
        person_detections = tracker.update_with_detections(person_detections)
        
        for i, box in enumerate(person_detections.xyxy):
            id_num = int(person_detections.tracker_id[i]) if person_detections.tracker_id is not None else -1
            
            # Position = Feet (Bottom Center of box)
            feet_x = int((box[0] + box[2]) / 2)
            feet_y = int(box[3])
            
            # Name convention: "P1", "P2" based on ID
            players.append(Player(
                pos=Coord(feet_x, feet_y),
                name=f"P{id_num}"
            ))

        # 4. PROCESS BALL
        ball = None # Default if no ball found
        ball_detections = detections[detections.class_id == 32]
        
        if len(ball_detections) > 0:
            # Pick the most confident ball
            box = ball_detections.xyxy[0]
            cx = int((box[0] + box[2]) / 2)
            cy = int((box[1] + box[3]) / 2)
            ball = Ball(pos=Coord(cx, cy))

        # 5. YIELD RAW DATA
        # We send the 'raw_court' every frame so Logic doesn't need to remember state
        yield (frame_count, players, ball, raw_court)

    cap.release()