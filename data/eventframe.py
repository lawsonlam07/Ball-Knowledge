from dataclasses import dataclass


@dataclass
class EventFrame:
    frameIndex: int
    event: str