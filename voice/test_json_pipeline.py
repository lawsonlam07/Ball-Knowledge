import json
import os
from prompts import generate_commentary, speak_text

# 1. The Example JSON Data
TEST_DATA = {
    "metadata": {
        "court_length_meters": 23.77,
        "net_position_x": 11.885
    },
    "events": [
        {
            "frame": 12,
            "event": "bounce",
            "side": "near",
            "x": 8.2
        },
        {
            "frame": 24,
            "event": "rally",
            "description": "ball crossed net",
            "x": 12.1
        },
        {
            "frame": 30,
            "event": "shot",
            "description": "direction reversal",
            "x": 13.5
        }
    ]
}

def main():
    print("🎾 Starting JSON -> Claude -> ElevenLabs Test...\n")
    
    # We pass the metadata once so Claude understands the context (optional, but helpful)
    metadata_str = json.dumps(TEST_DATA["metadata"])

    for i, raw_event in enumerate(TEST_DATA["events"]):
        print(f"--- Processing Event {i+1}: {raw_event['event']} ---")
        
        # Prepare the payload: Metadata + Specific Event
        # We send the raw JSON snippet directly as requested
        payload = {
            "context": json.loads(metadata_str),
            "current_event": raw_event
        }
        
        payload_str = json.dumps(payload, indent=2)
        
        # --- AI GENERATION ---
        print(f"   Context Sent to Claude:\n{payload_str}\n")
        
        # 1. Generate Text (Claude)
        # Using "Hype Man" to see if it picks up on the 'shot' excitement
        commentary_text = generate_commentary(payload_str, "Hype Man")
        print(f"   🎙️ Commentary: \"{commentary_text}\"")
        
        # 2. Generate Audio (ElevenLabs)
        print("   🔊 Generating Audio Stream...")
        try:
            audio_stream = speak_text(commentary_text)
            
            # 3. Save MP3
            filename = f"test_event_{i+1}.mp3"
            with open(filename, "wb") as f:
                for chunk in audio_stream:
                    if chunk:
                        f.write(chunk)
            print(f"   ✅ Saved audio to {filename}\n")
            
        except Exception as e:
            print(f"   ❌ Audio generation failed: {e}\n")

if __name__ == "__main__":
    main()