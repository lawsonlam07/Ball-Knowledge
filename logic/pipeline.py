from data.eventframe import EventFrame
from data.frame import Frame
from data.framestack import FrameStack
from data.orderofevents import OrderOfEvents
from logic.events import EventTesters
from logic.perspective import FrameUnskew
from vision import VisionSystem, get_court_calibration


def process_frames():
    fps = 60
    system = VisionSystem("tennis2.mp4")
    stack = FrameStack(60)
    i = 0
    order = OrderOfEvents()
    while True:
        i = i + 1
        frame: Frame = system.getNextFrame()
        normaliser = FrameUnskew(get_court_calibration(frame).to_vectors())
        normalised = frame.map(normaliser)
        # Push onto frame stack
        stack.push(normalised)
        # Iterate through event testers and pass frame stack
        results = []
        # noinspection PyTypeChecker
        for tester in EventTesters.ALL:
            result = tester.test_event(stack)
            if result is not None:
                # Pass events for which the test passes to event frames
                order.addEvent(EventFrame(frame, result.to_string()))
        # Extract the event strings from the EventFrame objects
        event_descriptions = [res.event for res in results]
        print(f"Frame {i}: {' | '.join(event_descriptions)}")

        # Merge consecutive events
        order.mergeConsecutiveEvents()
