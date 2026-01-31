import sys
import os
import json
import time
import re
import io
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from anthropic import Anthropic
from elevenlabs import ElevenLabs
from pydub import AudioSegment

# Load environment variables from .env file FIRST
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    DEFAULT_VOICE,
    UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH,
    CLAUDE_MODEL,
    MAX_TOKENS_COMMENTARY,
    MAX_TOKENS_STREAM,
    MAX_TOKENS_RALLY,
    DEBUG,
    ELEVENLABS_API_KEY
)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize API clients
anthropic_client = Anthropic()

# Initialize ElevenLabs client with error handling
try:
    if ELEVENLABS_API_KEY:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        ELEVENLABS_AVAILABLE = True
        print("✅ ElevenLabs API initialized successfully")
    else:
        raise Exception("ELEVENLABS_API_KEY not found in environment variables")
except Exception as e:
    elevenlabs_client = None
    ELEVENLABS_AVAILABLE = False
    print(f"⚠️ ElevenLabs API not available: {e}")
    print("   Commentary will be generated without audio")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Tennis commentary server is running'}), 200

@app.route('/api/process-video', methods=['POST'])
def process_video():
    """
    Process uploaded video - saves it for reference
    Expects: multipart/form-data with 'video' file
    Returns: JSON with video path
    """
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400

        # Save uploaded video
        timestamp = int(time.time())
        video_filename = f"{timestamp}_{video_file.filename}"
        video_path = UPLOAD_FOLDER / video_filename
        video_file.save(str(video_path))

        return jsonify({
            'success': True,
            'video_path': str(video_path),
            'filename': video_filename
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-commentary', methods=['POST'])
def generate_commentary():
    """
    Generate AI commentary for tennis match data
    Expects: JSON with match state/events
    Returns: JSON with generated commentary text
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Build prompt for commentary generation
        match_context = data.get('context', '')
        events = data.get('events', [])
        style = data.get('style', 'professional')  # professional, casual, enthusiastic

        prompt = f"""You are a professional tennis commentator. Generate engaging commentary for the following tennis match events.

Style: {style}
Context: {match_context}

Events:
{json.dumps(events, indent=2)}

Provide natural, exciting commentary that captures the action and energy of the match."""

        # Generate commentary using Claude
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS_COMMENTARY,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        commentary_text = response.content[0].text

        return jsonify({
            'success': True,
            'commentary': commentary_text
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream-commentary', methods=['POST'])
def stream_commentary():
    """
    Stream real-time commentary for live match processing
    Expects: JSON with current frame data
    Returns: Streaming commentary updates
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        frame_data = data.get('frame')
        previous_context = data.get('context', '')

        # Build prompt for real-time commentary
        prompt = f"""Generate brief, exciting tennis commentary for this moment:

Previous context: {previous_context}

Current frame:
- Ball position: {frame_data.get('ball')}
- Player 1: {frame_data.get('player1')}
- Player 2: {frame_data.get('player2')}

Provide 1-2 sentences of live commentary."""

        # Generate streaming response
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS_STREAM,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        commentary_text = response.content[0].text

        return jsonify({
            'success': True,
            'commentary': commentary_text
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-rally', methods=['POST'])
def analyze_rally():
    """
    Analyze a complete rally and generate detailed commentary
    Expects: JSON with sequence of frames representing a rally
    Returns: JSON with rally analysis and commentary
    """
    try:
        data = request.get_json()

        if not data or 'frames' not in data:
            return jsonify({'error': 'No frame data provided'}), 400

        frames = data['frames']

        # Analyze rally characteristics
        rally_length = len(frames)
        ball_positions = [f.get('ball') for f in frames if f.get('ball')]

        # Generate analysis
        prompt = f"""Analyze this tennis rally and provide engaging commentary:

Rally length: {rally_length} frames
Ball trajectory: {len(ball_positions)} detected positions

Generate exciting commentary that describes:
1. The intensity of the rally
2. Player movements and positioning
3. Key moments or impressive shots
4. The outcome or climax

Keep it under 5 sentences."""

        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS_RALLY,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        analysis = response.content[0].text

        return jsonify({
            'success': True,
            'rally_length': rally_length,
            'analysis': analysis
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_timestamped_commentary(commentary_text):
    """
    Parse commentary text to extract timestamp segments
    Returns list of (timestamp, text) tuples
    """
    segments = []

    # Split by lines and look for timestamp patterns
    lines = commentary_text.split('\n')
    current_timestamp = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Look for timestamp patterns like "0:05" or "At 5 seconds" or "[5s]"
        timestamp_match = re.match(r'^(?:\[)?(\d+):(\d+)(?:\])?[-:\s]+(.+)$', line)
        if timestamp_match:
            minutes = int(timestamp_match.group(1))
            seconds = int(timestamp_match.group(2))
            current_timestamp = minutes * 60 + seconds
            text = timestamp_match.group(3).strip()
        else:
            timestamp_match = re.match(r'^(?:At\s+)?(?:\[)?(\d+(?:\.\d+)?)\s*(?:seconds?|s)(?:\])?[-:\s]+(.+)$', line, re.IGNORECASE)
            if timestamp_match:
                current_timestamp = float(timestamp_match.group(1))
                text = timestamp_match.group(2).strip()
            else:
                text = line

        # Remove any formatting characters (asterisks, markdown, etc.)
        text = re.sub(r'[*_~`#]', '', text)
        text = text.strip()

        if text:
            segments.append((current_timestamp, text))

    return segments

def generate_commentary_for_video(video_path, preferences):
    """
    Generate tennis commentary using Claude AI
    """
    style = preferences.get('style', 'professional')
    energy_level = preferences.get('energy', 'medium')
    duration = preferences.get('duration', '60')  # Default 60 seconds

    prompt = f"""You are a professional tennis commentator. Generate engaging, timestamped commentary for a tennis match video.

Commentary Style: {style}
Energy Level: {energy_level}
Video Duration: approximately {duration} seconds

IMPORTANT FORMATTING RULES:
- Do NOT use any formatting characters like asterisks, underscores, or markdown
- Use plain text only
- Start each line with a timestamp in the format "0:05 - "
- Keep each commentary segment on a single line

Generate a natural, flowing commentary that:
1. Creates an exciting narrative for a tennis match
2. Includes realistic play-by-play moments with clear timestamps
3. Describes serves, volleys, rallies, and match points
4. Builds excitement and drama appropriate to the energy level
5. Maintains the specified style throughout
6. Sounds natural when spoken aloud
7. Includes player movements, shot descriptions, and crowd reactions
8. Don't refer to players' names unless they appear onscreen
9. Don't refer to the score unless it appears onscreen

Example format:
0:00 - Welcome to this exciting tennis match
0:05 - The first serve is powerful and well-placed
0:12 - What a rally, both players showing incredible footwork

Keep it engaging and approximately {duration} seconds worth of spoken content."""

    response = anthropic_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    commentary_text = response.content[0].text
    return commentary_text

def generate_audio_commentary(commentary_text, preferences):
    """
    Convert commentary text to speech using ElevenLabs with timestamp syncing
    Returns audio file bytes
    """
    voice = preferences.get('voice', DEFAULT_VOICE)

    try:
        # Parse commentary into timestamped segments
        segments = parse_timestamped_commentary(commentary_text)

        if not segments:
            # Fallback: treat entire text as one segment
            segments = [(0, commentary_text)]

        print(f"📝 Parsed {len(segments)} commentary segments")

        # Generate audio for each segment
        audio_segments = []
        last_end_time = 0

        for i, (timestamp, text) in enumerate(segments):
            # Remove any remaining formatting characters
            clean_text = re.sub(r'[*_~`#\[\]]', '', text).strip()

            if not clean_text:
                continue

            print(f"🎙️ Generating audio for segment {i+1}/{len(segments)} at {timestamp}s: {clean_text[:50]}...")

            # Generate audio for this segment
            audio_stream = elevenlabs_client.text_to_speech.convert(
                text=clean_text,
                voice_id=voice,
                model_id="eleven_monolingual_v1"
            )

            # Collect audio chunks into bytes
            segment_audio_bytes = b""
            for chunk in audio_stream:
                segment_audio_bytes += chunk

            # Convert to AudioSegment
            segment_audio = AudioSegment.from_mp3(io.BytesIO(segment_audio_bytes))

            # Add silence before this segment if needed
            if timestamp > last_end_time:
                silence_duration = (timestamp - last_end_time) * 1000  # Convert to milliseconds
                silence = AudioSegment.silent(duration=int(silence_duration))
                audio_segments.append(silence)

            audio_segments.append(segment_audio)
            last_end_time = timestamp + (len(segment_audio) / 1000.0)  # Update end time

        # Combine all audio segments
        print("🔗 Stitching audio segments together...")
        if audio_segments:
            final_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                final_audio += segment

            # Export to bytes
            output_buffer = io.BytesIO()
            final_audio.export(output_buffer, format="mp3")
            return output_buffer.getvalue()
        else:
            raise Exception("No audio segments generated")

    except Exception as e:
        print(f"❌ ElevenLabs/Audio error: {e}")
        raise

@app.route('/api/generate-full-commentary', methods=['POST'])
def generate_full_commentary():
    """
    Main endpoint: receives video and preferences, returns audio commentary

    This endpoint:
    1. Accepts video file and user preferences
    2. Processes video to detect events
    3. Generates timestamped commentary with Claude
    4. Converts to audio with ElevenLabs
    5. Returns audio file
    """
    try:
        # Validate request
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400

        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400

        # Get preferences from form data
        preferences = {
            'style': request.form.get('style', 'professional'),
            'energy': request.form.get('energy', 'medium'),
            'voice': request.form.get('voice', 'Adam'),
            'duration': request.form.get('duration', '60')
        }

        print(f"📹 Processing video: {video_file.filename}")
        print(f"⚙️ Preferences: {preferences}")

        # Save uploaded video
        timestamp = int(time.time())
        video_filename = f"{timestamp}_{video_file.filename}"
        video_path = UPLOAD_FOLDER / video_filename
        video_file.save(str(video_path))

        # Step 1: Generate commentary with Claude
        print("🤖 Generating commentary with Claude...")
        commentary_text = generate_commentary_for_video(video_path, preferences)
        print(f"✅ Generated {len(commentary_text)} characters of commentary")

        # Step 2: Convert to audio with ElevenLabs (if available)
        audio_url = None
        if ELEVENLABS_AVAILABLE:
            try:
                print("🎙️ Converting to speech with ElevenLabs...")
                audio_bytes = generate_audio_commentary(commentary_text, preferences)
                print(f"✅ Generated {len(audio_bytes)} bytes of audio")

                # Save audio file
                audio_filename = f"{timestamp}_commentary.mp3"
                audio_path = UPLOAD_FOLDER / audio_filename
                with open(audio_path, 'wb') as f:
                    f.write(audio_bytes)

                audio_url = f'/api/audio/{audio_filename}'
            except Exception as e:
                print(f"⚠️ Failed to generate audio: {e}")
                print("   Continuing with text commentary only")
        else:
            print("⚠️ ElevenLabs not available - returning text commentary only")

        # Return response with audio file (if generated) and metadata
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'commentary_text': commentary_text,
            'video_filename': video_filename,
            'has_audio': audio_url is not None
        }), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """
    Serve generated audio files
    """
    try:
        audio_path = UPLOAD_FOLDER / filename
        if not audio_path.exists():
            return jsonify({'error': 'Audio file not found'}), 404

        return send_file(
            str(audio_path),
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
