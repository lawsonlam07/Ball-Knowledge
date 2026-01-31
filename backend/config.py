import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Upload configuration
UPLOAD_FOLDER = BASE_DIR / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

# API Keys (from environment variables)
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Model configuration
MODEL_PATH = BASE_DIR.parent / 'yolov8m.pt'

# Commentary styles
COMMENTARY_STYLES = ['professional', 'casual', 'enthusiastic', 'dramatic']

# Claude model configuration
CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'
MAX_TOKENS_COMMENTARY = 1024
MAX_TOKENS_STREAM = 256
MAX_TOKENS_RALLY = 512

# ElevenLabs voice options (actual voice IDs from ElevenLabs)
DEFAULT_VOICE = "93nuHbke4dTER9x2pDwE"  # Deep, confident male voice

# Voice ID mapping (for reference)
VOICE_IDS = {
    "professional-male": "93nuHbke4dTER9x2pDwE",      # Deep, confident male
    "professional-female": "or4EV8aZq78KWcXw48wd",    # Calm, professional female
    "enthusiastic-male": "Rsz5u2Huh1hPlPr0oxRQ",      # Young, enthusiastic male
    "enthusiastic-female": "4RZ84U1b4WCqpu57LvIq",    # Soft, pleasant female
    "british-male": "htFfPSZGJwjBv1CL0aMD",           # Well-rounded male
    "british-female": "4RZ84U1b4WCqpu57LvIq",         # Soft, pleasant female
    "energetic-male": "z8I6YkY1XGj4qPGtLHtU",         # Crisp, energetic male
}

AVAILABLE_VOICES = list(VOICE_IDS.values())
