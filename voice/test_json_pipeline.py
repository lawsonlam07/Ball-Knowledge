import json
import os
from prompts import generate_commentary, speak_text

# 1. The Example JSON Data (Sequence of 3 events)
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
    print("🎾 Starting Full Sequence Test (One Audio Clip)...\n")
    
    # 1. Convert the ENTIRE JSON object to a string
    full_json_str = json.dumps(TEST_DATA, indent=2)
    
    print("   CONTEXT SENT TO CLAUDE:")
    print("   (Sending full sequence of 3 events...)\n")

    # 2. Generate Commentary (One cohesive take)
    commentary_text = generate_commentary(full_json_str, "Hype Man")
    print(f"   🎙️  Full Commentary: \"{commentary_text}\"\n")
    
    # 3. Generate Audio (One single file)
    print("   🔊 Generating Single Audio File...")
    try:
        audio_stream = speak_text(commentary_text)
        
        filename = "full_commentary.mp3"
        with open(filename, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)
                    
        print(f"   ✅ Success! Saved to {filename}")
        
    except Exception as e:
        print(f"   ❌ Audio generation failed: {e}")

if __name__ == "__main__":
    main()