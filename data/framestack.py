from .normalisedframe import NormalisedFrame

class FrameStack:
  def __init__(self, fps : int):
    self.elements = []
    self.topPointer = -1
    self.fps = fps

  def push(self, frame : NormalisedFrame):
    self.elements.append(frame)
    self.topPointer += 1

  def dequeue(self):
    self.topPointer -= 1
    return self.elements.pop(0)
  
  def peek(self):
    return self.elements[self.topPointer]
  
  def takeSeconds(self, seconds: int):
    #Returns the most recent frames covering the last `seconds`.
    num_frames = seconds * self.fps
    return self.elements[-num_frames:]

  def takeFrames(self, noFrames : int):
    return self.elements[-noFrames:]
