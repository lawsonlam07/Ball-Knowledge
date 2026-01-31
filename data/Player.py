from logic.perspective import FrameUnskew
from .Coord import Coord

class Player:
  def __init__(self, pos: Coord, name = ""):
    self.pos = pos
    self.name = name

  def map(self, normaliser: FrameUnskew):
    self.pos = normaliser.unskew_coords(self.pos.to_vector())