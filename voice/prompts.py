import os
import anthropic
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

# Initialize Clients
# Ensure ANTHROPIC_API_KEY is in your .env file
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
el_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def generate_commentary(event_json, persona_style):
    """
    Feeds raw JSON directly to Claude to generate commentary.
    """
    prompt = f"""
    You are a tennis commentator with the persona: {persona_style}.
    
    Here is the raw event data from the court tracking system:
    {event_json}
    
    Based on this data, write a single, punchy sentence of live commentary. 
    Do not mention "JSON" or "metadata". Just describe the action naturally.
    """
    
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=150,
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