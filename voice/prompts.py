import os
from google import genai
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

# Initialize Clients
genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
el_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def generate_commentary(event_data, persona_style):
    prompt = f"Context: {event_data}. Style: {persona_style}. Action: Write a 1-sentence live commentary."
    
    response = genai_client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return response.text

def speak_text(text):
    # This uses the streaming API for low latency
    audio_stream = el_client.generate(
        text=text,
        voice="Brian", # Or any voice ID you like
        model="eleven_turbo_v2",
        stream=True
    )
    return audio_stream