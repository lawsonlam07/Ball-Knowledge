import os
import anthropic
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

# Initialize Clients
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
el_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def generate_commentary(event_json, persona_style):
    """
    Feeds raw JSON directly to Claude to generate commentary.
    """
    prompt = f"""
    You are a tennis commentator with the persona: {persona_style}.
    
    Here is the raw event data (a sequence of events) from the court tracking system:
    {event_json}
    
    Based on this data, provide a brief, high-energy commentary describing the flow of action. 
    Keep it natural and continuous. Do not mention "JSON" or "metadata".
    """
    
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929", # Using the 4.5 model
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

def speak_text(text):
    """
    Uses the modern ElevenLabs client syntax to stream audio.
    """
    audio_stream = el_client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb", # 'George' voice ID
        model_id="eleven_turbo_v2",
        output_format="mp3_44100_128"
    )
    return audio_stream