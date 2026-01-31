from .Player import Player
from .Ball import Ball
from .Court import Court
from .net import Net


class Frame:
  def __init__(self, ball : Ball, court : Court, player1 : Player, player2 : Player):
    self.ball = ball
    self.court = court
    self.player1 = player1
    self.player2 = player2
