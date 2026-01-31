from logic.perspective import FrameUnskew
from .Coord import Coord

class Court:
  def __init__(self, tl : Coord, tr : Coord, br : Coord, bl : Coord):
    self.tl = tl
    self.tr = tr
    self.br = br
    self.bl = bl

  def to_vectors(self):
    return [self.tl.to_vector(), self.tr.to_vector(), self.br.to_vector(), self.bl.to_vector()]

  def map(self, normaliser: FrameUnskew):
    self.tl = normaliser.unskew_coords_to_coords(self.tl.to_vector())
    self.tr = normaliser.unskew_coords_to_coords(self.tr.to_vector())
    self.br = normaliser.unskew_coords_to_coords(self.br.to_vector())
    self.bl = normaliser.unskew_coords_to_coords(self.bl.to_vector())
    return self