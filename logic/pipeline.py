import json
from dataclasses import asdict

from data.eventframe import EventFrame
from data.frame import Frame
from data.framestack import FrameStack
from data.orderofevents import OrderOfEvents
from logic.events import EventTesters
from logic.perspective import FrameUnskew
from vision import VisionSystem, get_court_calibration


def process_frames(url):
    fps = 60
    system = VisionSystem(url)
    stack = FrameStack(fps)
    i = 0
    order = OrderOfEvents()
    while True:
        i = i + 1
        frame: Frame = system.getNextFrame()
        if frame is None:
            break
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
                results.append(result)
                order.addEvent(EventFrame(i, result.to_string()))
        # Extract the event strings from the EventFrame objects
        event_descriptions = [res.to_string() for res in results]
        print(f"Frame {i}: {' | '.join(event_descriptions)}")
        if len(stack.elements) > 5 * fps:
            stack.dequeue()

    # Merge consecutive events
    order.mergeConsecutiveEvents()
    json_array = json.dumps([asdict(e) for e in order.orderedEvents], indent=4)
    return json_array
