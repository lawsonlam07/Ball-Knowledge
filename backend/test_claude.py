"""
Quick test to find which Claude model your API key has access to
"""
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = Anthropic()

# List of models to try
models_to_try = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]

print("Testing Claude API access...\n")

for model_name in models_to_try:
    try:
        print(f"Testing: {model_name}... ", end="")
        response = client.messages.create(
            model=model_name,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✅ SUCCESS - Use this model!")
        print(f"   Response: {response.content[0].text}\n")
        break  # Found a working model
    except Exception as e:
        if "not_found_error" in str(e):
            print(f"❌ Not found")
        elif "permission" in str(e).lower():
            print(f"❌ No permission")
        else:
            print(f"❌ Error: {str(e)[:50]}")

print("\nUpdate backend/config.py with the working model name.")
