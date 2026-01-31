from abc import abstractmethod


class EventInterface:
    @abstractmethod
    def test_event(self, frames):
        pass
