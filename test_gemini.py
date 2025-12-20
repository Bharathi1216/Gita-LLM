import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print(f"API Key loaded: {GEMINI_API_KEY[:20]}..." if GEMINI_API_KEY else "NO API KEY")

# Test available models
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
print("\n📋 Listing available models...")
try:
    r = requests.get(list_url, timeout=10)
    if r.status_code == 200:
        models = r.json().get("models", [])
        print(f"Found {len(models)} models:")
        for model in models[:10]:  # Show first 10
            print(f"  - {model.get('name', 'Unknown')}")
    else:
        print(f"Error listing models: {r.status_code}")
except Exception as e:
    print(f"Exception: {e}")

# Try gemini-2.0-flash
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

payload = {
    "contents": [{
        "parts": [{"text": "Say 'Hello' in one word"}]
    }]
}

print("\n🔄 Testing Gemini API...")
try:
    r = requests.post(url, json=payload, timeout=15)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text[:500]}")
    
    if r.status_code == 200:
        result = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"\n✅ SUCCESS: {result}")
    else:
        print(f"\n❌ API Error: {r.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
