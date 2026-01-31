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
    return NormalisedFrame(
      self.ball.map(normaliser),
      self.court.map(normaliser),
      self.player1.map(normaliser),
      self.player2.map(normaliser)
    )