from abc import abstractmethod, ABC
from enum import Enum

from data.framestack import FrameStack
from data.normalisedframe import NormalisedFrame
from logic.perspective import TENNIS_COURT_LENGTH

threshold = 0.1
NET_POS = TENNIS_COURT_LENGTH / 2

class EventInterface(ABC):
    @abstractmethod
    def to_string(self):
        pass

class EventTesterInterface(ABC):
    @abstractmethod
    def test_event(self, frames: FrameStack):
        pass

class RallyEvent(EventInterface):
    def to_string(self):
        return "rally"

class BounceEvent(EventInterface):
    def to_string(self):
        return "bounce"

class ShotEvent(EventInterface):
    def to_string(self):
        return "shot"

class RallyEventTester(EventTesterInterface):
    def test_event(self, frames: FrameStack):
        frames_sided = [self.isRightOfNet(f) for f in frames.takeFrames(2)]

        return any(frames_sided) and not all(frames_sided)

    def isRightOfNet(self, frame: NormalisedFrame):
        ball_positions = frame.ball.pos
        if ball_positions.x > NET_POS:
            return RallyEvent()
        else:
            return None


class BounceOrShotEventTester(EventTesterInterface):
    def __init__(self, _is_internal=False):
        if not _is_internal:
            raise PermissionError("Constructor is private. Use BounceOrShotEvent.create()")

    @classmethod
    def create(cls):
        return cls(_is_internal=True)

    def test_event(self, frames: FrameStack):
        # Take the last 3 frames to get two segments of movement
        recent = frames.takeFrames(3)
        if len(recent) < 3:
            return None

        # Calculate horizontal velocity (relative to net)
        # v1: Velocity before the middle frame
        v1_x = recent[1].ball.pos.x - recent[0].ball.pos.x
        # v2: Velocity after the middle frame
        v2_x = recent[2].ball.pos.x - recent[1].ball.pos.x

        # Logic: If the sign of velocity changed, the ball reversed direction (A Shot)
        # If the sign is the same, but there was a 'spike' in data, it's a Bounce
        changed_sign = (v1_x > 0) != (v2_x > 0)

        if changed_sign:
            return ShotEvent()  # Ball reversed direction relative to net

        # If direction didn't change, we check for a 'k' tolerance
        # (e.g., a sudden drop in speed) to identify a bounce
        speed_ratio = abs(v2_x) / abs(v1_x) if abs(v1_x) > 0 else 1

        if speed_ratio < 0.8:  # Threshold 'k' for energy loss on bounce
            return BounceEvent()

        return None


class EventTesters(Enum, EventTesterInterface):
    RALLY = RallyEventTester()
    BOUNCE_OR_SHOT = BounceOrShotEventTester()
