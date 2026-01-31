"""
Example usage script for the tennis commentary API
Demonstrates how to call the main endpoint from a client
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def generate_commentary_example():
    """
    Example: Upload a video and generate full audio commentary
    """
    # Path to your tennis video
    video_path = "../tennis.mp4"  # Adjust path as needed

    print("=" * 60)
    print("Tennis Commentary API - Example Usage")
    print("=" * 60)

    # Prepare the request
    with open(video_path, 'rb') as video_file:
        files = {
            'video': ('tennis.mp4', video_file, 'video/mp4')
        }

        data = {
            'style': 'enthusiastic',  # professional, casual, enthusiastic
            'energy': 'high',          # low, medium, high
            'voice': 'Adam'            # ElevenLabs voice ID
        }

        print("\n📤 Sending video for processing...")
        print(f"Video: {video_path}")
        print(f"Preferences: {json.dumps(data, indent=2)}")
        print("\n⏳ This may take a while...\n")

        try:
            # Make the request
            response = requests.post(
                f"{BASE_URL}/api/generate-full-commentary",
                files=files,
                data=data,
                timeout=300  # 5 minute timeout
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"\n🎙️ Audio URL: {BASE_URL}{result['audio_url']}")
                print(f"\n📝 Commentary Preview:")
                print("-" * 60)
                print(result['commentary_text'][:500] + "...")
                print("-" * 60)
                print(f"\n📊 Events detected: {result['events_count']}")

                # Save audio URL for reference
                print(f"\n💾 You can access the audio at:")
                print(f"   {BASE_URL}{result['audio_url']}")

            else:
                print(f"❌ Error: {response.status_code}")
                print(response.json())

        except requests.exceptions.Timeout:
            print("⏰ Request timed out - video processing takes a while!")
        except Exception as e:
            print(f"❌ Error: {e}")

def check_server_health():
    """
    Check if the server is running
    """
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print("❌ Server returned error")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"Make sure the server is running at {BASE_URL}")
        return False

if __name__ == "__main__":
    print("\n🔍 Checking server status...")
    if check_server_health():
        print("\n" + "=" * 60)
        generate_commentary_example()
    else:
        print("\n⚠️ Start the server first:")
        print("   cd backend")
        print("   uv run python app.py")
