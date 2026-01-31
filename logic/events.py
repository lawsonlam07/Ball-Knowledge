import numpy as np
from data.framestack import FrameStack
from data.frame import NormalisedFrame


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
    """
    Generic tester to detect if the ball is on a specific side of the net.
    """

    def __init__(self, target_right: bool, event_class: type):
        self.target_right = target_right
        self.event_class = event_class
        self.net_pos_x = 11.885  # Half of 23.77m

    def test_event(self, frames: FrameStack):
        # Take the last 2 frames to detect a transition
        recent = frames.takeFrames(2)

        # 1. Guard: Need 2 frames with valid balls to detect a 'switch'
        if len(recent) < 2 or any(f.ball is None for f in recent):
            return None

        # 2. Check sides for both frames
        prev_is_right = recent[0].ball.pos.x > self.net_pos_x
        curr_is_right = recent[1].ball.pos.x > self.net_pos_x

        # 3. Logic: Trigger ONLY if it just entered the target side
        # Example: If target is RIGHT, we trigger when (Prev=Left and Curr=Right)
        if self.target_right:
            if not prev_is_right and curr_is_right:
                return self.event_class()
        else:
            if prev_is_right and not curr_is_right:
                return self.event_class()

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
    LEFT_SIDE = SideTester(target_right=False, event_class=LeftOfNetEvent)
    RIGHT_SIDE = SideTester(target_right=True, event_class=RightOfNetEvent)

    # Physics-based detection
    BOUNCE_SHOT = BounceOrShotTester()

    # Java-style .values() equivalent
    ALL = [LEFT_SIDE, RIGHT_SIDE, BOUNCE_SHOT]