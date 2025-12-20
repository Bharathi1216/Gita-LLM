import requests
import json

# Test the updated bot with Ollama
print("🧪 Testing GITA-AI with Ollama Integration\n")

base_url = "http://127.0.0.1:5000/api"

# Test 1: Survey endpoint
print("1️⃣ Creating session...")
response = requests.post(f"{base_url}/survey", json={})
data = response.json()
user_id = data.get("user_id")
print(f"✅ User ID: {user_id}\n")

# Test 2: Casual chat
print("2️⃣ Testing casual chat...")
response = requests.post(f"{base_url}/chat", json={
    "message": "how are you",
    "user_id": user_id
})
data = response.json()
print(f"Bot: {data['response']}")
print(f"Verse: {data['data']}\n")

# Test 3: Emotional support
print("3️⃣ Testing emotional support...")
response = requests.post(f"{base_url}/chat", json={
    "message": "I am feeling very anxious",
    "user_id": user_id
})
data = response.json()
print(f"Bot: {data['response']}")
print(f"Verse: {data['data']}\n")

# Test 4: Reflective guidance
print("4️⃣ Testing reflective guidance...")
response = requests.post(f"{base_url}/chat", json={
    "message": "What is the meaning of duty?",
    "user_id": user_id
})
data = response.json()
print(f"Bot: {data['response']}")
if data['data']:
    print(f"Verse: {data['data']['id']}")
    print(f"English: {data['data']['english'][:100]}...")
else:
    print("Verse: None")

print("\n✅ All tests completed!")
