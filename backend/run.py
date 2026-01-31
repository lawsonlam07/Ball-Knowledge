"""
Simple script to run the Flask development server
"""
from app import app
from config import DEBUG

if __name__ == '__main__':
    print("🎾 Starting Tennis Commentary Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📖 API Documentation: See README.md")
    print("\n✅ Available endpoints:")
    print("   GET  /api/health")
    print("   POST /api/process-video")
    print("   POST /api/generate-commentary")
    print("   POST /api/stream-commentary")
    print("   POST /api/analyze-rally")
    print("\n")

    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
