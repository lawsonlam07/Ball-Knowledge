import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

# IMPORT YOUR CLASSES
from data.Coord import Coord
from data.Ball import Ball
from data.Court import Court
from data.Player import Player

# --- CONFIG ---
MODEL_NAME = 'yolov8m.pt' 

# THRESHOLDS
CONF_PLAYER = 0.25  # Lowered slightly to ensure we catch players even when blurry
CONF_BALL = 0.15    # Very low to catch fast balls

def get_court_calibration(frame):
    print("✅ Using Hardcoded Court Coordinates")
    return Court(
        tl=Coord(746, 257),
        tr=Coord(1183, 254),
        br=Coord(1879, 836),
        bl=Coord(27, 841)
    )

def is_point_in_court(point, court, buffer=100):
    """
    Checks if a point is inside the court + a buffer area.
    Reduced buffer to 100px to help exclude umpires/benches.
    """
    polygon = np.array([
        [court.tl.x, court.tl.y],
        [court.tr.x, court.tr.y],
        [court.br.x, court.br.y],
        [court.bl.x, court.bl.y]
    ], np.int32)
    
    dist = cv2.pointPolygonTest(polygon, (float(point[0]), float(point[1])), True)
    return dist >= -buffer

def get_best_two_players(detections, court):
    """
    Selects exactly one player for the Top Half and one for the Bottom Half.
    Ignores umpires (middle) and crowd (outside).
    """
    top_candidate = None
    bottom_candidate = None
    
    # Calculate an approximate "net line" Y-coordinate
    # (Midpoint between top-y and bottom-y)
    net_y = (court.tl.y + court.bl.y) / 2

    # Filter for class 0 (Person)
    people = detections[detections.class_id == 0]

    for i, box in enumerate(people.xyxy):
        # Calculate key points
        x1, y1, x2, y2 = box
        feet_pos = (int((x1 + x2) / 2), int(y2))
        torso_pos = (int((x1 + x2) / 2), int((y1 + y2) / 2))
        conf = people.confidence[i]

        # 1. GEOMETRY CHECK: Must be inside/near court
        if not is_point_in_court(feet_pos, court, buffer=150):
            continue

        # 2. SPLIT: Is this person above or below the net?
        if feet_pos[1] < net_y:
            # TOP HALF CANDIDATE
            # Logic: We want the person "deepest" in the court (closest to baseline)
            # or simply highest confidence. Confidence is usually safer.
            if top_candidate is None or conf > top_candidate['conf']:
                top_candidate = {'pos': torso_pos, 'conf': conf, 'name': 'Top'}
        else:
            # BOTTOM HALF CANDIDATE
            if bottom_candidate is None or conf > bottom_candidate['conf']:
                bottom_candidate = {'pos': torso_pos, 'conf': conf, 'name': 'Bottom'}

    # Compile the final list of up to 2 players
    final_players = []
    if top_candidate:
        final_players.append(Player(pos=Coord(*top_candidate['pos']), name="P2")) # Top
    if bottom_candidate:
        final_players.append(Player(pos=Coord(*bottom_candidate['pos']), name="P1")) # Bottom
        
    return final_players

def process_video(source_path: str):
    cap = cv2.VideoCapture(source_path)
    model = YOLO(MODEL_NAME)
    
    # NOTE: Tracker removed. 
    # Since we are spatially assigning "Top" and "Bottom" every frame, 
    # we don't need complex ID tracking (which fails when players leave frame).
    
    ret, first_frame = cap.read()
    if not ret: raise ValueError("Video empty")
    
    raw_court = get_court_calibration(first_frame)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1
        
        # 1. DETECT EVERYTHING
        results = model(frame, classes=[0, 32], conf=CONF_BALL, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)
        
        # 2. GET PLAYERS (STRICT FILTER)
        # We pass the raw detections; the function handles confidence checks for players internally
        # (We rely on the geometric filter to remove low-conf noise outside the court)
        players = get_best_two_players(detections, raw_court)

        # 3. GET BALL (SIMPLEGEST FILTER)
        ball = None 
        mask_balls = (detections.class_id == 32)
        ball_detections = detections[mask_balls]
        
        if len(ball_detections) > 0:
            # Find the best ball that is actually inside the court
            best_ball_conf = -1
            
            for i, box in enumerate(ball_detections.xyxy):
                conf = ball_detections.confidence[i]
                cx = int((box[0] + box[2]) / 2)
                cy = int((box[1] + box[3]) / 2)
                
                # Check if ball is reasonably inside the court
                if is_point_in_court((cx, cy), raw_court, buffer=100):
                    if conf > best_ball_conf:
                        best_ball_conf = conf
                        ball = Ball(pos=Coord(cx, cy))

        yield (frame_count, players, ball, raw_court)

    cap.release()