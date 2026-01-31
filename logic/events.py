from abc import abstractmethod, ABC
from data.framestack import FrameStack
from data.normalisedframe import NormalisedFrame
from logic.perspective import TENNIS_COURT_LENGTH

threshold = 0.1
NET_POS = TENNIS_COURT_LENGTH / 2


class EventInterface(ABC):
    @abstractmethod
    def test_event(self, frames: FrameStack):
        pass


class RallyEvent(EventInterface):  # Added inheritance
    def test_event(self, frames: FrameStack):
        frames_sided = [self.isRightOfNet(f) for f in frames.takeFrames(2)]

        return any(frames_sided) and not all(frames_sided)

    def isRightOfNet(self, frame: NormalisedFrame):
        ball_positions = frame.ball.pos
        return ball_positions.x > NET_POS


class BounceOrShotEvent(EventInterface):  # Added inheritance
    def test_event(self, frames: FrameStack):
        # Logic: take the last 0.05 seconds
        # if the ball has not changed sign but changed direction by more than
        # some tolerance k then we have a bounce; if not we have a shot
        return False


# --- Instances ---
rally_event = RallyEvent()
bounce_or_shot_event = BounceOrShotEvent()