from .Coord import Coord

class Player:
  def __init__(self,  pos : Coord, name = ""):
    self.pos = pos
    self.name = name