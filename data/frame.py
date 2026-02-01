from logic.perspective import FrameUnskew
from .Ball import Ball
from .Court import Court
from .Player import Player
from .normalisedframe import NormalisedFrame


class Frame:
  def __init__(self, ball : Ball, court : Court, player1 : Player, player2 : Player):
    self.ball = ball
    self.court = court
    self.player1 = player1
    self.player2 = player2

  def map(self, normaliser: FrameUnskew):
    ball = self.ball.map(normaliser) if self.ball is not None else None
    court = self.court.map(normaliser) if self.court is not None else None
    p1 = self.player1.map(normaliser) if self.player1 is not None else None
    p2 = self.player2.map(normaliser) if self.player2 is not None else None

    return NormalisedFrame(ball, court, p1, p2)