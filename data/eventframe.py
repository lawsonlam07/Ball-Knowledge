from .frame import Frame

class EventFrame:
  def __init__(self, frame : Frame, event : str):
    self.frame = frame
    self.event = event