import requests
import time

base_url = "http://127.0.0.1:5000/api"

print("🧪 QUICK TEST SUITE - Key Scenarios\n")

# Create session
response = requests.post(f"{base_url}/survey", json={})
user_id = response.json().get("user_id")

def test(msg, desc, expected_verse=None):
    """Quick test with expectation"""
    print(f"\n{'='*70}")
    print(f"📝 {desc}")
    print(f"{'='*70}")
    print(f"👤 User: {msg}")
    
    response = requests.post(f"{base_url}/chat", json={
        "message": msg,
        "user_id": user_id
    })
    data = response.json()
    
    print(f"🤖 Bot: {data['response'][:150]}...")
    
    if data['data']:
        print(f"📖 Verse: {data['data']['id']} ✅")
        if expected_verse is False:
            print("⚠️  WARNING: Verse shown when it shouldn't be!")
    else:
        print(f"📖 Verse: None")
        if expected_verse is True:
            print("⚠️  WARNING: No verse when one was expected!")
    
    time.sleep(0.5)

# ==================== TEST CASES ====================

print("\n🟦 CASUAL CONVERSATIONS (No verses expected)")
test("hi", "1. Simple Greeting", expected_verse=False)
test("how are you?", "2. Wellness Check", expected_verse=False)
test("thanks", "3. Gratitude", expected_verse=False)
test("good night", "4. Farewell", expected_verse=False)

print("\n🟥 EMOTIONAL DISTRESS (No verses - safety first)")
test("I am very angry", "5. Anger", expected_verse=False)
test("feeling anxious about exam", "6. Anxiety", expected_verse=False)
test("I'm so stressed", "7. Stress", expected_verse=False)
test("I'm afraid", "8. Fear", expected_verse=False)

print("\n🟩 REFLECTIVE QUESTIONS (Verses expected)")
test("What is dharma?", "9. Philosophical - Dharma", expected_verse=True)
test("Why should I do my duty?", "10. About Duty", expected_verse=True)
test("What is karma?", "11. Karma Concept", expected_verse=True)
test("How to find peace?", "12. Seeking Peace", expected_verse=True)
test("What is the self?", "13. Self-Inquiry", expected_verse=True)

print("\n🟨 PRACTICAL LIFE (Context-dependent)")
test("I have to make a difficult decision", "14. Decision Making", expected_verse=None)
test("confused about career", "15. Career Question", expected_verse=None)
test("Should I help someone who hurt me?", "16. Ethical Dilemma", expected_verse=True)

print("\n🟧 MIXED EMOTIONS (Testing safety)")
test("I'm anxious but want to know my purpose", "17. Mixed: Anxiety + Purpose", expected_verse=False)
test("Why am I confused?", "18. Confusion (reflective)", expected_verse=None)

print("\n🟪 EDGE CASES")
test("dharma?", "19. Single Word", expected_verse=True)
test("give me a verse", "20. Explicit Request", expected_verse=True)

print("\n🟢 POSITIVE EMOTIONS (Conversational)")
test("I feel happy today", "21. Happiness", expected_verse=False)
test("grateful for life", "22. Gratitude", expected_verse=False)

print("\n🔵 SPECIFIC TOPICS")
test("Tell me about detachment", "23. Detachment Topic", expected_verse=True)
test("What about action without desire?", "24. Nishkama Karma", expected_verse=True)
test("Explain yoga", "25. Yoga Concept", expected_verse=True)

print("\n" + "="*70)
print("✅ QUICK TEST COMPLETED - 25 Scenarios Tested")
print("="*70)
print("\n📊 Expected Behavior:")
print("✓ Casual → No verse, friendly chat")
print("✓ Emotional → No verse, calming support")
print("✓ Reflective → Verse + guidance")
print("✓ Safety → Emotion blocks verses")
print("\nReview results above to verify system is working correctly!")
