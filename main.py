import os
from logic.pipeline import process_frames
# Importing your existing functions from prompts.py
from voice.prompts import generate_commentary, speak_text

# --- CONFIG ---
VIDEO_FILE = "tennis2.mp4"
OUTPUT_AUDIO_FILE = "final_commentary.mp3"
PERSONA = "Energetic, fast-paced tennis commentator like Robbie Koenig"

def main():
    print(f"🚀 Starting Pipeline for {VIDEO_FILE}...")
    
    # 1. VIDEO -> JSON (Using your pipeline.py)
    print("\n[1/3] Processing Video Frames...")
    raw_json = process_frames(VIDEO_FILE)
    
    # 2. JSON -> SCRIPT (Using your prompts.py)
    print("\n[2/3] Generating Commentary Script...")
    script = generate_commentary(raw_json, PERSONA)
    print(f"\n💬 SCRIPT:\n{'-'*20}\n{script}\n{'-'*20}")
    
    # 3. SCRIPT -> AUDIO (Using your prompts.py)
    print("\n[3/3] Generating Audio...")
    audio_stream = speak_text(script)
    
    # 4. SAVE AUDIO STREAM TO FILE
    print(f"   Saving to {OUTPUT_AUDIO_FILE}...")
    with open(OUTPUT_AUDIO_FILE, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
            
    print(f"\n✅ DONE! Audio saved to: {os.path.abspath(OUTPUT_AUDIO_FILE)}")

if __name__ == "__main__":
    main()