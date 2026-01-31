from .Ball import Ball
from .Coart import Court
from .Player import Player

class Frame:
  def __init__(self, ball : Ball, court : Court, player1 : Player, player2 : Player):
    self.ball = ball
    self.court = court
    self.player1 = player1
    self.player2 = player2