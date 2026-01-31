import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

# --- IMPORTS ---
# Ensure these files exist in your 'data' folder
from data.Coord import Coord
from data.Ball import Ball
from data.Court import Court
from data.Player import Player
from data.frame import Frame 

# --- CONFIG ---
MODEL_NAME = 'yolov8m.pt' 

# THRESHOLDS
CONF_BALL = 0.15      
MAX_COAST_FRAMES = 5 
MAX_DIST_ERROR = 100 

# TOGGLE: If True, returns the last known location when detection fails
RETURN_LAST_KNOWN_POS = False

def get_court_calibration(frame):
    print("✅ Using Hardcoded Court Coordinates")
    return Court(
        # 1080p Coordinates:
        tl=Coord(746, 257), tr=Coord(1183, 254),
        br=Coord(1879, 836), bl=Coord(27, 841)
    )

def is_player_in_court(point, court, buffer=100):
    polygon = np.array([
        [court.tl.x, court.tl.y], [court.tr.x, court.tr.y],
        [court.br.x, court.br.y], [court.bl.x, court.bl.y]
    ], np.int32)
    return cv2.pointPolygonTest(polygon, (float(point[0]), float(point[1])), True) >= -buffer

def is_ball_in_zone(point, court, buffer=50):
    sky_polygon = np.array([
        [court.bl.x - buffer, -1000],       
        [court.br.x + buffer, -1000],       
        [court.br.x + buffer, court.br.y + buffer], 
        [court.bl.x - buffer, court.bl.y + buffer]  
    ], np.int32)
    return cv2.pointPolygonTest(sky_polygon, (float(point[0]), float(point[1])), True) >= 0

def get_best_two_players(detections, court):
    top, bottom = None, None
    net_y = (court.tl.y + court.bl.y) / 2
    
    mask = (detections.class_id == 0)
    if not np.any(mask): return []
    people = detections[mask]

    for i, box in enumerate(people.xyxy):
        x1, y1, x2, y2 = box
        feet = (int((x1 + x2) / 2), int(y2))
        torso = (int((x1 + x2) / 2), int((y1 + y2) / 2))
        conf = people.confidence[i]

        if not is_player_in_court(feet, court, buffer=150): continue

        if feet[1] < net_y:
            if top is None or conf > top['conf']: top = {'pos': torso, 'conf': conf}
        else:
            if bottom is None or conf > bottom['conf']: bottom = {'pos': torso, 'conf': conf}

    players = []
    if top: players.append(Player(pos=Coord(*top['pos']), name="P2"))
    if bottom: players.append(Player(pos=Coord(*bottom['pos']), name="P1"))
    return players

def process_video(source_path: str):
    cap = cv2.VideoCapture(source_path)
    model = YOLO(MODEL_NAME)
    
    ret, first_frame = cap.read()
    if not ret: raise ValueError("Video empty")
    
    raw_court = get_court_calibration(first_frame)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    frame_count = 0

    # --- TRACKER STATE ---
    track_pos = None      
    track_vel = (0, 0)    
    frames_since_seen = 0 
    last_valid_pos = None 

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1
        
        # 1. DETECT (Removed imgsz=1280 for speed)
        results = model(frame, classes=[0, 32], conf=CONF_BALL, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)
        
        players = get_best_two_players(detections, raw_court)
        ball_obj = None 

        # 2. PREDICT
        predicted_pos = None
        if track_pos is not None:
            predicted_pos = (track_pos[0] + track_vel[0], track_pos[1] + track_vel[1])

        # 3. GATHER CANDIDATES
        ball_candidates = []
        mask_balls = (detections.class_id == 32)
        if np.any(mask_balls):
            ball_dets = detections[mask_balls]
            for i, box in enumerate(ball_dets.xyxy):
                w, h = box[2] - box[0], box[3] - box[1]
                if w * h > 400: continue 
                
                cx, cy = int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)
                
                if is_ball_in_zone((cx, cy), raw_court, buffer=50):
                    ball_candidates.append({'pos': (cx, cy), 'conf': ball_dets.confidence[i]})

        # 4. MATCH
        matched_candidate = None
        if predicted_pos is not None:
            best_dist = float('inf')
            for cand in ball_candidates:
                dist = np.linalg.norm(np.array(cand['pos']) - np.array(predicted_pos))
                if dist < best_dist and dist < MAX_DIST_ERROR:
                    best_dist = dist
                    matched_candidate = cand
        elif ball_candidates:
            matched_candidate = max(ball_candidates, key=lambda x: x['conf'])

        # 5. UPDATE
        if matched_candidate:
            new_pos = matched_candidate['pos']
            if track_pos is not None:
                inst_vel = (new_pos[0] - track_pos[0], new_pos[1] - track_pos[1])
                track_vel = (0.7 * inst_vel[0] + 0.3 * track_vel[0], 
                             0.7 * inst_vel[1] + 0.3 * track_vel[1])
            track_pos = new_pos
            frames_since_seen = 0 
            ball_obj = Ball(pos=Coord(*track_pos))
            last_valid_pos = track_pos 
        elif track_pos is not None and frames_since_seen < MAX_COAST_FRAMES:
            track_pos = (int(predicted_pos[0]), int(predicted_pos[1]))
            frames_since_seen += 1
            ball_obj = Ball(pos=Coord(*track_pos))
            last_valid_pos = track_pos 
        else:
            track_pos = None
            track_vel = (0, 0)
            frames_since_seen = 0
            if RETURN_LAST_KNOWN_POS and last_valid_pos is not None:
                ball_obj = Ball(pos=Coord(*last_valid_pos))

        yield (frame_count, players, ball_obj, raw_court)

    cap.release()

# --- VISION SYSTEM CLASS ---
class VisionSystem:
    def __init__(self, video_path):
        self.pipeline = process_video(video_path)

    def getNextFrame(self):
        """
        Returns a Frame object (ball, court, player1, player2).
        If ball/players are not found, they will be None.
        Returns None when video ends.
        """
        try:
            # Get data from generator
            _, players_list, ball, court = next(self.pipeline)

            # Default to None (null)
            p1 = None
            p2 = None

            # Map based on fixed names assigned in get_best_two_players
            for p in players_list:
                if p.name == "P1":
                    p1 = p
                elif p.name == "P2":
                    p2 = p
            
            # ball is already None if not found in process_video
            return Frame(ball=ball, court=court, player1=p1, player2=p2)

        except StopIteration:
            return None