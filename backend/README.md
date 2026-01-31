# Tennis Commentary Backend Server

Flask-based backend server for AI-powered tennis commentary system.

## Features

- AI-generated tennis commentary using Claude (Anthropic)
- Text-to-speech audio generation with ElevenLabs
- Customizable commentary styles and energy levels
- RESTful API endpoints
- Support for multiple voice options

## Setup

This project uses `uv` for package management. Dependencies are defined in the root `pyproject.toml`.

1. **Install dependencies:**
   ```bash
   # From the project root directory
   uv sync
   ```

2. **Set up environment variables:**
   Create a `.env` file in the backend folder based on `.env.example`:
   ```bash
   cd backend
   cp .env.example .env
   ```

   Add your API keys:
   - `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/
   - `ELEVENLABS_API_KEY`: Get from https://elevenlabs.io/ (optional)

3. **Run the server:**
   ```bash
   # From the backend directory
   uv run python app.py
   # or
   uv run python run.py
   ```

   The server will start on `http://localhost:5000`

   > **Note:** If you're not using `uv`, you can still use pip: `pip install -r requirements.txt`

## API Endpoints

### Generate Full Commentary (Main Endpoint)
```
POST /api/generate-full-commentary
Content-Type: multipart/form-data
```
**Primary endpoint** that processes a video and returns complete audio commentary.

**Request:**
- `video`: Video file (mp4, avi, etc.)
- `style`: Commentary style - "professional", "casual", "enthusiastic" (optional, default: "professional")
- `energy`: Energy level - "low", "medium", "high" (optional, default: "medium")
- `voice`: ElevenLabs voice ID (optional, default: "Adam")

**Response:**
```json
{
  "success": true,
  "audio_url": "/api/audio/1234567890_commentary.mp3",
  "commentary_text": "Full commentary script...",
  "events_count": 5,
  "events": [...]
}
```

**Workflow:**
1. Receives video file and user preferences (style, energy level, voice)
2. Generates engaging timestamped commentary with Claude AI
3. Converts commentary text to speech with ElevenLabs
4. Returns audio file URL and commentary text

### Get Audio File
```
GET /api/audio/<filename>
```
Serves the generated audio commentary file.

### Health Check
```
GET /api/health
```
Returns server status.

### Process Video
```
POST /api/process-video
Content-Type: multipart/form-data
```
Upload a tennis match video for frame-by-frame processing.

**Request:**
- `video`: Video file (mp4, avi, etc.)

**Response:**
```json
{
  "success": true,
  "frames": [...],
  "total_frames": 1234
}
```

### Generate Commentary
```
POST /api/generate-commentary
Content-Type: application/json
```
Generate AI commentary for match events.

**Request:**
```json
{
  "context": "Match context or description",
  "events": ["event1", "event2"],
  "style": "professional|casual|enthusiastic"
}
```

**Response:**
```json
{
  "success": true,
  "commentary": "Generated commentary text..."
}
```

### Stream Commentary
```
POST /api/stream-commentary
Content-Type: application/json
```
Get real-time commentary for a single frame.

**Request:**
```json
{
  "frame": {
    "ball": {"x": 100, "y": 200},
    "player1": {"name": "P1", "x": 300, "y": 400},
    "player2": {"name": "P2", "x": 500, "y": 600}
  },
  "context": "Previous commentary context"
}
```

**Response:**
```json
{
  "success": true,
  "commentary": "Brief commentary for this moment..."
}
```

### Analyze Rally
```
POST /api/analyze-rally
Content-Type: application/json
```
Analyze a complete rally sequence.

**Request:**
```json
{
  "frames": [
    {"ball": {...}, "player1": {...}, "player2": {...}},
    ...
  ]
}
```

**Response:**
```json
{
  "success": true,
  "rally_length": 45,
  "analysis": "Detailed rally analysis and commentary..."
}
```

## Architecture

- **Flask**: Web framework for REST API
- **Anthropic Claude**: AI commentary generation
- **ElevenLabs**: Text-to-speech audio generation
- **Flask-CORS**: Cross-origin resource sharing for frontend integration

## Development

The server runs in debug mode by default. For production:

```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## Notes

- Maximum upload file size: 500MB
- Supported video formats: mp4, avi, mov, etc.
- Uploads and generated audio files are stored in `backend/uploads/` directory
- Commentary is generated based on user preferences without computer vision processing
