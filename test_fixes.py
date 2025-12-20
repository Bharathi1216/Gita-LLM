import requests

base_url = "http://127.0.0.1:5000/api"

print("🔍 Testing Fixed Issues\n")

# Create session
response = requests.post(f"{base_url}/survey", json={})
user_id = response.json().get("user_id")

def quick_test(msg):
    print(f"\n{'='*60}")
    print(f"👤 User: {msg}")
    response = requests.post(f"{base_url}/chat", json={
        "message": msg,
        "user_id": user_id
    })
    data = response.json()
    print(f"🤖 Bot: {data['response'][:100]}...")
    if data['data']:
        print(f"📖 Verse: {data['data']['id']} ✅ VERSE PROVIDED")
    else:
        print(f"📖 Verse: ❌ NONE")
    return bool(data['data'])

print("\n🔧 TESTING FIXES:")
print("="*60)

# Issue 1: Single word philosophical terms
print("\n1️⃣ Single Word Terms (Should provide verses):")
v1 = quick_test("dharma?")
v2 = quick_test("karma?")
v3 = quick_test("yoga?")

# Issue 2: "Explain X" pattern
print("\n2️⃣ 'Explain' Pattern (Should provide verses):")
v4 = quick_test("Explain yoga")
v5 = quick_test("Explain karma")
v6 = quick_test("Tell me about detachment")

# Verify emotional safety still works
print("\n3️⃣ Emotional Safety Check (Should NOT provide verses):")
v7 = quick_test("I'm stressed")
v8 = quick_test("feeling anxious")

# Verify casual still works
print("\n4️⃣ Casual Chat Check (Should NOT provide verses):")
v9 = quick_test("thanks")
v10 = quick_test("I feel happy")

print("\n" + "="*60)
print("📊 RESULTS:")
print("="*60)

issues_fixed = v1 and v2 and v3 and v4 and v5 and v6
safety_works = not v7 and not v8
casual_works = not v9 and not v10

print(f"✅ Issue 1 (Single words): {'FIXED' if v1 and v2 and v3 else 'STILL BROKEN'}")
print(f"✅ Issue 2 (Explain pattern): {'FIXED' if v4 and v5 and v6 else 'STILL BROKEN'}")
print(f"✅ Emotional Safety: {'WORKING' if safety_works else 'BROKEN'}")
print(f"✅ Casual Chat: {'WORKING' if casual_works else 'BROKEN'}")

if issues_fixed and safety_works and casual_works:
    print("\n🎉 ALL SYSTEMS WORKING PERFECTLY!")
else:
    print("\n⚠️  Some issues remain - check output above")
