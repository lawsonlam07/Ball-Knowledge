from .eventframe import EventFrame

class OrderOfEvents:
  def __init__(self):
      self.orderedEvents = []  # list[EventFrame]

  def addEvent(self, event: EventFrame):
      self.orderedEvents.append(event)

  def mergeConsecutiveEvents(self) -> list[EventFrame]:
    if not self.orderedEvents:
        return []

    result = [self.orderedEvents[0]]

    for current in self.orderedEvents[1:]:
        last = result[-1]

        if current.event != last.event:
            result.append(current)

    return result