import numpy as np
from data.framestack import FrameStack
from data.frame import NormalisedFrame
from logic.perspective import TENNIS_COURT_LENGTH


# --- EVENT CLASSES ---

class Event:
    def to_string(self):
        return self.__class__.__name__


# Ideas
# Volley Event
# Plr Left, Right, Up, Down event
# Ball Stopped Event
# Ball In/Out event
class RallyEvent(Event): pass
class BounceEvent(Event): pass
class ShotEvent(Event): pass
class RightOfNetEvent(Event): pass
class LeftOfNetEvent(Event): pass
class VolleyEvent(Event): pass
class PlayerUpEvent(Event): pass
class PlayerDownEvent(Event): pass
class PlayerLeftEvent(Event): pass
class PlayerRightEvent(Event): pass
class BallStoppedEvent(Event): pass
class BallInEvent(Event): pass
class BallOutEvent(Event): pass

# --- BASE TESTER ---

class SideTester:
    def __init__(self, side: str):
        self.side = side
        self.net_pos_x = TENNIS_COURT_LENGTH/2

    def test_event(self, frames: FrameStack):
        recent = frames.takeFrames(1)

        # Guard against nulls
        if not recent or recent[0].ball is None:
            return None

        ball_x = recent[0].ball.pos.x

        if self.side == "right":
            if ball_x > self.net_pos_x:
                return RightOfNetEvent()

        if self.side == "left":
            if ball_x <= self.net_pos_x:
                return LeftOfNetEvent()

        return None

# --- COMPLEX TESTERS ---

class BounceOrShotTester:
    def test_event(self, frames: FrameStack):
        recent = frames.takeFrames(3)

        # Ensure we have 3 frames and all have ball data
        if len(recent) < 3 or any(f is None or f.ball is None for f in recent):
            return None

        v1_x = recent[1].ball.pos.x - recent[0].ball.pos.x
        v2_x = recent[2].ball.pos.x - recent[1].ball.pos.x

        # Detect Shot: Horizontal direction reversal
        if (v1_x > 0) != (v2_x > 0) and abs(v1_x) > 0.05:
            return ShotEvent()

        # Detect Bounce: Significant loss of horizontal velocity
        if abs(v1_x) > 0:
            speed_ratio = abs(v2_x) / abs(v1_x)
            if speed_ratio < 0.8:
                return BounceEvent()

        return None

class PlayerMovementTester:
    def __init__(self, player_index: int, direction: str, movement_threshold: float = 0.5):
        self.player_index = player_index
        self.direction = direction
        self.movement_threshold = movement_threshold

    def test_event(self, frames: FrameStack):
        recent = frames.takeFrames(5)  # Look at movement over ~0.17 seconds

        # Guard against nulls
        if len(recent) < 5:
            return None

        # Get the correct player based on index
        players = []
        for f in recent:
            if f is None:
                players.append(None)
            elif self.player_index == 0 and f.player1 is not None:
                players.append(f.player1)
            elif self.player_index == 1 and f.player2 is not None:
                players.append(f.player2)
            else:
                players.append(None)

        if any(p is None for p in players):
            return None

        # Calculate net displacement
        start_pos = players[0].pos
        end_pos = players[-1].pos

        dx = end_pos.x - start_pos.x
        dy = end_pos.y - start_pos.y

        # Check direction-specific movement
        if self.direction == "up":
            if dy > self.movement_threshold:
                return PlayerUpEvent()
        elif self.direction == "down":
            if dy < -self.movement_threshold:
                return PlayerDownEvent()
        elif self.direction == "left":
            if dx < -self.movement_threshold:
                return PlayerLeftEvent()
        elif self.direction == "right":
            if dx > self.movement_threshold:
                return PlayerRightEvent()

        return None

class BallStoppedTester:
    def __init__(self, velocity_threshold: float = 0.05, min_stopped_seconds: float = 0.5, fps: int = 60):
        self.min_stopped_seconds = min_stopped_seconds
        self.velocity_threshold = velocity_threshold
        self.fps = fps
        
    def test_event(self, frames: FrameStack):
        # Calculate number of frames needed based on seconds and fps
        min_stopped_frames = int(self.min_stopped_seconds * self.fps)
        
        recent = frames.takeFrames(min_stopped_frames + 1)

        # Guard against nulls
        if len(recent) < min_stopped_frames + 1:
            return None

        if any(f is None or f.ball is None for f in recent):
            return None

        # Check velocity for consecutive frames
        stopped_count = 0
        for i in range(len(recent) - 1):
            dx = recent[i + 1].ball.pos.x - recent[i].ball.pos.x
            dy = recent[i + 1].ball.pos.y - recent[i].ball.pos.y
            
            # Ball only has x and y coordinates based on Coord class
            velocity = np.sqrt(dx**2 + dy**2)

            if velocity < self.velocity_threshold:
                stopped_count += 1

        # Ball has been stopped for minimum duration
        if stopped_count >= min_stopped_frames:
            return BallStoppedEvent()

        return None

class BallInOutTester:
    def __init__(self):
        self.last_state = None  # Track last known state to detect transitions

    def test_event(self, frames: FrameStack):
        recent = frames.takeFrames(3)

        # Guard against nulls
        if len(recent) < 3 or any(f is None or f.ball is None or f.court is None for f in recent):
            return None

        # Check if ball has just bounced (reversal in vertical velocity)
        # We need to infer vertical movement from the trajectory
        # Calculate distances between consecutive ball positions
        d1 = np.sqrt((recent[1].ball.pos.x - recent[0].ball.pos.x)**2 + 
                     (recent[1].ball.pos.y - recent[0].ball.pos.y)**2)
        d2 = np.sqrt((recent[2].ball.pos.x - recent[1].ball.pos.x)**2 + 
                     (recent[2].ball.pos.y - recent[1].ball.pos.y)**2)
        
        # Detect bounce: significant change in velocity/direction (similar to BounceEvent logic)
        if d1 > 0:
            speed_ratio = d2 / d1
            # Bounce detected if there's a significant loss of velocity
            just_bounced = speed_ratio < 0.8
        else:
            return None

        if not just_bounced:
            return None

        # Get court boundaries
        court = recent[-1].court
        ball_pos = recent[-1].ball.pos
        
        # Check if ball is within court boundaries using point-in-polygon test
        # Court corners: tl (top-left), tr (top-right), br (bottom-right), bl (bottom-left)
        is_in_bounds = self._point_in_quadrilateral(
            ball_pos,
            court.tl,
            court.tr,
            court.br,
            court.bl
        )

        current_state = "in" if is_in_bounds else "out"

        # Only trigger event on state change or first detection
        if self.last_state != current_state:
            self.last_state = current_state
            if is_in_bounds:
                return BallInEvent()
            else:
                return BallOutEvent()

        return None

    def _point_in_quadrilateral(self, point, tl, tr, br, bl) -> bool:
        """
        Check if a point is inside a quadrilateral using the cross product method.
        The point is inside if it's on the same side of all four edges.
        """
        def sign(p1, p2, p3) -> float:
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
        
        # Check if point is on the correct side of each edge
        # Edge 1: tl -> tr
        d1 = sign(point, tl, tr)
        # Edge 2: tr -> br
        d2 = sign(point, tr, br)
        # Edge 3: br -> bl
        d3 = sign(point, br, bl)
        # Edge 4: bl -> tl
        d4 = sign(point, bl, tl)
        
        # Point is inside if all signs are the same (all positive or all negative)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0) or (d4 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0) or (d4 > 0)
        
        return not (has_neg and has_pos)

# --- REGISTRY ---

class EventTesters:
    # Instantiate SideTester twice with different configurations
    LEFT_SIDE = SideTester(side="left")
    RIGHT_SIDE = SideTester(side="right")

    # Physics-based detection
    BOUNCE_SHOT = BounceOrShotTester()

    # Player movement (Player 0 - player1)
    PLAYER0_UP = PlayerMovementTester(player_index=0, direction="up")
    PLAYER0_DOWN = PlayerMovementTester(player_index=0, direction="down")
    PLAYER0_LEFT = PlayerMovementTester(player_index=0, direction="left")
    PLAYER0_RIGHT = PlayerMovementTester(player_index=0, direction="right")

    # Player movement (Player 1 - player2)
    PLAYER1_UP = PlayerMovementTester(player_index=1, direction="up")
    PLAYER1_DOWN = PlayerMovementTester(player_index=1, direction="down")
    PLAYER1_LEFT = PlayerMovementTester(player_index=1, direction="left")
    PLAYER1_RIGHT = PlayerMovementTester(player_index=1, direction="right")

    # Ball state
    BALL_STOPPED = BallStoppedTester()
    BALL_IN_OUT = BallInOutTester()

    # Java-style .values() equivalent
    ALL = [
        LEFT_SIDE, RIGHT_SIDE,
        BOUNCE_SHOT,
        PLAYER0_UP, PLAYER0_DOWN, PLAYER0_LEFT, PLAYER0_RIGHT,
        PLAYER1_UP, PLAYER1_DOWN, PLAYER1_LEFT, PLAYER1_RIGHT,
        BALL_STOPPED, BALL_IN_OUT
    ]