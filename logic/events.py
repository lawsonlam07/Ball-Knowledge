import numpy as np
from data.framestack import FrameStack
from data.frame import NormalisedFrame
from logic.perspective import TENNIS_COURT_LENGTH


# --- EVENT CLASSES ---

class Event:
    def to_string(self):
        return self.__class__.__name__


class RallyEvent(Event): pass


class BounceEvent(Event): pass


class ShotEvent(Event): pass


class RightOfNetEvent(Event): pass

class LeftOfNetEvent(Event): pass


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


# --- REGISTRY ---

class EventTesters:
    # Instantiate SideTester twice with different configurations
    LEFT_SIDE = SideTester(side="right")
    RIGHT_SIDE = SideTester(side="left")

    # Physics-based detection
    BOUNCE_SHOT = BounceOrShotTester()

    # Java-style .values() equivalent
    ALL = [LEFT_SIDE, RIGHT_SIDE, BOUNCE_SHOT]