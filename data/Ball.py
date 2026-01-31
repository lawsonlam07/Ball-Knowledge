from logic.perspective import FrameUnskew
from .Coord import Coord

class Ball:
  def __init__(self, pos : Coord):
    self.pos = pos

  def map(self, normaliser: FrameUnskew):
    self.pos = normaliser.unskew_coords_to_coords(self.pos.to_vector())
    return self