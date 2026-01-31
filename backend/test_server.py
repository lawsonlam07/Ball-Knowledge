"""
Simple test script to verify Flask server functionality
Run this after starting the server to test endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("Testing /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_generate_commentary():
    """Test commentary generation endpoint"""
    print("\nTesting /api/generate-commentary...")
    try:
        payload = {
            "context": "Close tennis match, third set",
            "events": [
                "Player 1 serves ace",
                "Long rally of 15 shots",
                "Player 2 hits winning backhand"
            ],
            "style": "enthusiastic"
        }
        response = requests.post(
            f"{BASE_URL}/api/generate-commentary",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Commentary: {result.get('commentary', 'N/A')[:200]}...")
        else:
            print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_stream_commentary():
    """Test stream commentary endpoint"""
    print("\nTesting /api/stream-commentary...")
    try:
        payload = {
            "frame": {
                "ball": {"x": 500, "y": 300},
                "player1": {"name": "P1", "x": 200, "y": 600},
                "player2": {"name": "P2", "x": 800, "y": 400}
            },
            "context": "Match is tied at 40-40"
        }
        response = requests.post(
            f"{BASE_URL}/api/stream-commentary",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Commentary: {result.get('commentary', 'N/A')}")
        else:
            print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Flask Server Test Suite")
    print("=" * 60)
    print(f"\nTesting server at: {BASE_URL}")
    print("Make sure the server is running (python app.py or python run.py)\n")

    results = []
    results.append(("Health Check", test_health()))
    results.append(("Generate Commentary", test_generate_commentary()))
    results.append(("Stream Commentary", test_stream_commentary()))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
