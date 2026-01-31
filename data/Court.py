from Coord import Coord

class Court:
  def __init__(self, tl : Coord, tr : Coord, br : Coord, bl : Coord):
    self.tl = tl
    self.tr = tr
    self.br = br
    self.bl = bl