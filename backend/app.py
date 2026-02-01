import sys
import os
import json
import time
import re
# import io
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from anthropic import Anthropic
from elevenlabs import ElevenLabs
# from pydub import AudioSegment

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

@app.route('/api/download-youtube', methods=['POST'])
def download_youtube():
    """
    Download a YouTube video and save it locally
    Expects: JSON with 'url' field
    Returns: JSON with video path
    """
    try:
        data = request.get_json()
        youtube_url = data.get('url')

        if not youtube_url:
            return jsonify({'error': 'No URL provided'}), 400

        print(f"📥 Downloading YouTube video: {youtube_url}")

        # Generate filename
        timestamp = int(time.time())
        output_template = str(UPLOAD_FOLDER / f"{timestamp}_%(title)s.%(ext)s")

        # Use yt-dlp to download the video
        import subprocess

        # Download with best quality video+audio
        result = subprocess.run([
            'yt-dlp',
            '-f', 'best[ext=mp4]/best',  # Prefer mp4 format
            '--no-playlist',  # Don't download playlists
            '-o', output_template,
            youtube_url
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ yt-dlp error: {result.stderr}")
            return jsonify({'error': f'Failed to download video: {result.stderr}'}), 500

        # Find the downloaded file
        import glob
        downloaded_files = glob.glob(str(UPLOAD_FOLDER / f"{timestamp}_*"))

        if not downloaded_files:
            return jsonify({'error': 'Download succeeded but file not found'}), 500

        video_path = downloaded_files[0]
        video_filename = os.path.basename(video_path)

        print(f"✅ Downloaded: {video_filename}")

        return jsonify({
            'success': True,
            'video_path': video_path,
            'filename': video_filename
        }), 200

    except Exception as e:
        print(f"❌ Error downloading YouTube video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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

Provide natural, exciting commentary that captures the action and energy of the match.
You must produce commentary similar to a professional commentator
This means that you do not speak continually and only speak when you are able to provide insight about the gameplay.
When we say "left" in a prompt it means that the ball is in the top of the court as the camera sees it.
You may only use information contained within the prompt. You may use context to change how engaging the commentary is.
Events are timestamped in frames at 60FPS.
You must ensure that your commentary can be spoken at a normal human pace without needing to be spoken unnaturally quickly.
Do not provide any text other than the commentary"""

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
    Returns a list of segment dictionaries with timestamp and text
    """
    style = preferences.get('style', 'professional')
    energy_level = preferences.get('energy', 'medium')
    duration = preferences.get('duration', '60')  # Default 60 seconds

    prompt = f"""You are a professional tennis commentator. Generate engaging, timestamped commentary for a tennis match video.

Commentary Style: {style}
Energy Level: {energy_level}
Video Duration: approximately {duration} seconds

Generate a natural, flowing commentary that:
1. Creates an exciting narrative for a tennis match
2. Includes realistic play-by-play moments
3. Describes serves, volleys, rallies, and match points
4. Builds excitement and drama appropriate to the energy level
5. Maintains the specified style throughout
6. Sounds natural when spoken aloud
7. Includes player movements, shot descriptions, and crowd reactions
8. Don't refer to players' names unless they appear onscreen
9. Don't refer to the score unless it appears onscreen

CRITICAL: You MUST respond with valid JSON ONLY. No other text before or after.
Format your response as a JSON array of segments:

[
  {{"timestamp": 0, "text": "Welcome to this exciting tennis match"}},
  {{"timestamp": 5, "text": "The first serve is powerful and well-placed"}},
  {{"timestamp": 12, "text": "What a rally, both players showing incredible footwork"}}
]

Rules:
- timestamp is in seconds (integer or float)
- text should be 1-3 sentences that flow naturally when spoken
- Keep it engaging and approximately {duration} seconds worth of content
- Use plain language, no markdown or special characters
- Return ONLY the JSON array, nothing else"""

    response = anthropic_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.content[0].text.strip()
    print(f"📝 Raw Claude response: {response_text[:300]}...")

    # Parse JSON response
    try:
        # Try to extract JSON from markdown code blocks if present
        if response_text.startswith('```'):
            # Extract content between ```json and ``` or ``` and ```
            import re
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1).strip()
                print(f"📝 Extracted JSON from code block: {response_text[:200]}...")

        segments = json.loads(response_text)
        print(f"✅ Successfully parsed {len(segments)} segments")
        return segments
    except json.JSONDecodeError as e:
        print(f"⚠️ Failed to parse JSON response: {e}")
        print(f"Response was: {response_text[:500]}...")
        # Fallback: return a simple segment
        return [{"timestamp": 0, "text": "Commentary generation encountered an error."}]

def generate_audio_commentary(commentary_segments, preferences):
    """
    Convert commentary segments to speech using ElevenLabs
    Returns list of audio segments with timestamps for frontend synchronization
    """
    voice = preferences.get('voice', DEFAULT_VOICE)

    try:
        print(f"📝 Processing {len(commentary_segments)} commentary segments")

        # Generate audio for each segment
        audio_segments = []

        for i, segment in enumerate(commentary_segments):
            timestamp = segment['timestamp']
            text = segment['text']

            # Remove any remaining formatting characters
            clean_text = re.sub(r'[*_~`#\[\]]', '', text).strip()

            if not clean_text:
                continue

            print(f"🎙️ Generating audio segment {i+1}/{len(commentary_segments)} at {timestamp}s: {clean_text[:50]}...")

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

            audio_segments.append({
                'timestamp': timestamp,
                'text': clean_text,
                'audio': segment_audio_bytes
            })

        print(f"✅ Generated {len(audio_segments)} audio segments")
        return audio_segments

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
        # Get preferences from form data
        preferences = {
            'style': request.form.get('style', 'professional'),
            'energy': request.form.get('energy', 'medium'),
            'voice': request.form.get('voice', 'Adam'),
            'duration': request.form.get('duration', '60')
        }

        # Check if video_filename is provided (for pre-downloaded videos)
        timestamp = int(time.time())

        if 'video_filename' in request.form:
            # Video was already downloaded (e.g., from YouTube)
            video_filename = request.form.get('video_filename', '')
            if not video_filename:
                return jsonify({'error': 'Video filename is empty'}), 400

            video_path = UPLOAD_FOLDER / video_filename

            if not video_path.exists():
                return jsonify({'error': 'Downloaded video file not found'}), 400

            print(f"📹 Processing pre-downloaded video: {video_filename}")
            print(f"⚙️ Preferences: {preferences}")
        else:
            # Normal file upload
            if 'video' not in request.files:
                return jsonify({'error': 'No video file provided'}), 400

            video_file = request.files['video']
            if video_file.filename == '':
                return jsonify({'error': 'No video file selected'}), 400

            print(f"📹 Processing uploaded video: {video_file.filename}")
            print(f"⚙️ Preferences: {preferences}")

            # Save uploaded video
            video_filename = f"{timestamp}_{video_file.filename}"
            video_path = UPLOAD_FOLDER / video_filename
            video_file.save(str(video_path))

        # Step 1: Generate commentary with Claude
        print("🤖 Generating commentary with Claude...")
        commentary_segments = generate_commentary_for_video(video_path, preferences)
        print(f"✅ Generated {len(commentary_segments)} commentary segments")

        # Convert segments back to text format for compatibility
        commentary_text = "\n".join([
            f"{seg['timestamp']}s - {seg['text']}" for seg in commentary_segments
        ])

        # Step 2: Convert to audio with ElevenLabs (if available)
        audio_segments_data = None
        if ELEVENLABS_AVAILABLE:
            try:
                print("🎙️ Converting to speech with ElevenLabs...")
                audio_segments = generate_audio_commentary(commentary_segments, preferences)

                # Save each audio segment as a separate file
                audio_segments_data = []
                for i, segment in enumerate(audio_segments):
                    audio_filename = f"{timestamp}_segment_{i}.mp3"
                    audio_path = UPLOAD_FOLDER / audio_filename

                    print(f"💾 Saving audio segment {i} to: {audio_path}")
                    print(f"   Audio data size: {len(segment['audio'])} bytes")

                    with open(audio_path, 'wb') as f:
                        bytes_written = f.write(segment['audio'])
                        print(f"   Wrote {bytes_written} bytes to disk")

                    # Verify file was created
                    if audio_path.exists():
                        file_size = audio_path.stat().st_size
                        print(f"   ✅ File created: {file_size} bytes on disk")
                    else:
                        print(f"   ❌ File not found after writing!")

                    # Add segment metadata for frontend
                    audio_url = f'/api/audio/{audio_filename}'
                    audio_segments_data.append({
                        'timestamp': segment['timestamp'],
                        'text': segment['text'],
                        'audio_url': audio_url
                    })
                    print(f"   URL: {audio_url}")

                print(f"✅ Saved {len(audio_segments_data)} audio segments")
            except Exception as e:
                print(f"⚠️ Failed to generate audio: {e}")
                print("   Continuing with text commentary only")
                audio_segments_data = None
        else:
            print("⚠️ ElevenLabs not available - returning text commentary only")

        # Return response with audio segments (if generated) and metadata
        return jsonify({
            'success': True,
            'audio_segments': audio_segments_data,
            'commentary_text': commentary_text,
            'video_filename': video_filename,
            'has_audio': audio_segments_data is not None
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
        print(f"📡 Audio request received for: {filename}")
        audio_path = UPLOAD_FOLDER / filename
        print(f"   Looking for file at: {audio_path}")
        print(f"   File exists: {audio_path.exists()}")

        if audio_path.exists():
            file_size = audio_path.stat().st_size
            print(f"   File size: {file_size} bytes")

        if not audio_path.exists():
            print(f"   ❌ File not found!")
            print(f"   Directory contents: {list(UPLOAD_FOLDER.glob('*'))}")
            return jsonify({'error': 'Audio file not found'}), 404

        print(f"   ✅ Serving audio file")
        return send_file(
            str(audio_path),
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except Exception as e:
        print(f"   ❌ Error serving audio: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
