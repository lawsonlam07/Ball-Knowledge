import json
from dataclasses import asdict

from data.eventframe import EventFrame
from data.frame import Frame
from data.framestack import FrameStack
from data.orderofevents import OrderOfEvents
from logic.events import EventTesters
from logic.perspective import FrameUnskew
from vision.core import VisionSystem, get_court_calibration

def process_frames(url):
    print(f"\n{'='*80}", flush=True)
    print(f"🎬 process_frames() CALLED with video: {url}", flush=True)
    print(f"{'='*80}\n", flush=True)

    fps = 60
    print(f"📹 Initializing VisionSystem...", flush=True)
    system = VisionSystem(url)
    stack = FrameStack(fps)
    i = 0
    order = OrderOfEvents()

    print(f"🔄 Starting frame processing loop...", flush=True)
    while True:
        i += 1
        frame: Frame = system.getNextFrame()
        if frame is None:
            break
            
        # REVERTED: Use the exact function call that worked before
        court_calib = get_court_calibration(frame)
        normaliser = FrameUnskew(court_calib.to_vectors())
        normalised = frame.map(normaliser)
        
        # Push onto frame stack
        stack.push(normalised)
        
        # Iterate through event testers
        results = []
        for tester in EventTesters.ALL:
            result = tester.test_event(stack)
            if result is not None:
                results.append(result)
                # Add to our order object
                order.addEvent(EventFrame(i, result.to_string()))
        
        # Print progress so we know it's working
        event_descriptions = [res.to_string() for res in results]
        print(f"Frame {i}: {' | '.join(event_descriptions)}", flush=True)
            
        if len(stack.elements) > 5 * fps:
            stack.dequeue()

    # --- THE COMPRESSION LOGIC ---
    print(f"\n{'='*80}", flush=True)
    print(f"✅ Frame processing complete! Total frames processed: {i}", flush=True)
    print(f"🔄 Merging consecutive events...", flush=True)

    # Capture the result of the merge
    merged_events = order.mergeConsecutiveEvents()

    print(f"📊 Total events after merge: {len(merged_events)}", flush=True)
    print(f"{'='*80}\n", flush=True)

    # Serialize the MERGED events
    json_array = json.dumps([asdict(e) for e in merged_events], indent=4)

    return json_array