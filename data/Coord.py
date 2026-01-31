class Coord:
  def __init__(self, x : float, y : float):
    self.x = x
    self.y = y

  def to_vector(self):
    return [self.x, self.y]