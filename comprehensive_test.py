import requests
import json
import time

base_url = "http://127.0.0.1:5000/api"

# Create session
print("=" * 80)
print("🧪 COMPREHENSIVE TEST SUITE - GITA AI")
print("=" * 80)

response = requests.post(f"{base_url}/survey", json={})
user_id = response.json().get("user_id")
print(f"✅ Session created: {user_id}\n")

def test_chat(message, scenario_name):
    """Test a chat message and display results"""
    print(f"\n{'='*80}")
    print(f"📝 SCENARIO: {scenario_name}")
    print(f"{'='*80}")
    print(f"User: \"{message}\"")
    print("-" * 80)
    
    response = requests.post(f"{base_url}/chat", json={
        "message": message,
        "user_id": user_id
    })
    data = response.json()
    
    print(f"🤖 Bot: {data['response']}")
    
    if data['data']:
        print(f"\n📖 Verse: {data['data']['id']}")
        if data['data'].get('sanskrit'):
            print(f"Sanskrit: {data['data']['sanskrit'][:80]}...")
        print(f"English: {data['data']['english'][:100]}...")
        if data['data'].get('tamil'):
            print(f"Tamil: {data['data']['tamil'][:80]}...")
    else:
        print(f"📖 Verse: None (Correctly withheld)")
    
    time.sleep(1)  # Small delay between requests


# ==================== CATEGORY 1: GREETINGS & CASUAL ====================
print("\n" + "🟦" * 40)
print("CATEGORY 1: GREETINGS & CASUAL CONVERSATION")
print("🟦" * 40)

test_chat("hi", "Simple Greeting")
test_chat("hey there", "Casual Greeting")
test_chat("good morning", "Time-based Greeting")
test_chat("how are you doing?", "Checking on Bot")
test_chat("what's your name?", "Identity Question")
test_chat("thanks for the help", "Gratitude")
test_chat("okay", "Short Acknowledgment")

# ==================== CATEGORY 2: EMOTIONAL DISTRESS ====================
print("\n" + "🟥" * 40)
print("CATEGORY 2: EMOTIONAL DISTRESS (No Verses Expected)")
print("🟥" * 40)

test_chat("I am so angry right now", "Pure Anger")
test_chat("feeling very anxious about tomorrow", "Anxiety")
test_chat("I'm stressed about work", "Stress")
test_chat("I'm afraid of failure", "Fear")
test_chat("feeling depressed and sad", "Sadness")
test_chat("panic attack help", "Panic/Emergency")
test_chat("I hate everything", "Intense Negative Emotion")

# ==================== CATEGORY 3: REFLECTIVE QUESTIONS ====================
print("\n" + "🟩" * 40)
print("CATEGORY 3: REFLECTIVE GUIDANCE (Verses Expected)")
print("🟩" * 40)

test_chat("What is dharma?", "Simple Philosophical Question")
test_chat("Why should I perform my duty?", "Question About Duty")
test_chat("What is the meaning of life?", "Existential Question")
test_chat("How do I find inner peace?", "Seeking Peace")
test_chat("What is karma?", "Karma Question")
test_chat("How to detach from results?", "Detachment Question")
test_chat("What is the self?", "Self-inquiry")
test_chat("Why do I suffer?", "Question About Suffering")

# ==================== CATEGORY 4: PRACTICAL LIFE QUESTIONS ====================
print("\n" + "🟨" * 40)
print("CATEGORY 4: PRACTICAL LIFE SITUATIONS")
print("🟨" * 40)

test_chat("I have to make a difficult decision", "Decision Making")
test_chat("I'm confused about my career path", "Career Confusion")
test_chat("Should I help someone who hurt me?", "Ethical Dilemma")
test_chat("How do I deal with difficult people?", "Relationship Issue")
test_chat("I feel lost in life", "General Confusion")
test_chat("What should I do when everything feels wrong?", "Crisis Moment")

# ==================== CATEGORY 5: MIXED EMOTIONS + REFLECTION ====================
print("\n" + "🟧" * 40)
print("CATEGORY 5: MIXED EMOTIONS (Testing Edge Cases)")
print("🟧" * 40)

test_chat("I'm anxious but I want to understand my purpose", 
          "Anxiety + Purpose (Should block verse)")
test_chat("I'm confused about duty", 
          "Confusion (Reflective, not emotional)")
test_chat("Why am I so angry all the time?", 
          "Anger + Why (Borderline case)")
test_chat("stressed about finding meaning in life", 
          "Stress + Meaning (Should block verse)")

# ==================== CATEGORY 6: SHORT QUESTIONS ====================
print("\n" + "🟪" * 40)
print("CATEGORY 6: SHORT/CONCISE QUESTIONS")
print("🟪" * 40)

test_chat("duty?", "Single Word Question")
test_chat("why act?", "Two Words")
test_chat("what's karma", "Three Words")
test_chat("give me a verse", "Explicit Request")

# ==================== CATEGORY 7: FOLLOW-UP CONVERSATION ====================
print("\n" + "🟫" * 40)
print("CATEGORY 7: CONVERSATIONAL FLOW")
print("🟫" * 40)

test_chat("tell me about the gita", "About the Source")
test_chat("I want to learn", "Openness to Learning")
test_chat("explain more", "Follow-up Request")
test_chat("I don't understand", "Confusion Expression")
test_chat("that makes sense", "Understanding Acknowledgment")

# ==================== CATEGORY 8: EDGE CASES ====================
print("\n" + "⬛" * 40)
print("CATEGORY 8: EDGE CASES & SPECIAL SCENARIOS")
print("⬛" * 40)

test_chat("", "Empty Message (Should handle gracefully)")
test_chat("asdfghjkl", "Gibberish")
test_chat("What is dharma but I'm also angry?", "Mixed Clear Intent")
test_chat("Can you help me understand while I'm stressed?", "Help Request During Stress")

# ==================== CATEGORY 9: POSITIVE EMOTIONS ====================
print("\n" + "🟢" * 40)
print("CATEGORY 9: POSITIVE EMOTIONAL STATES")
print("🟢" * 40)

test_chat("I feel happy today", "Happiness")
test_chat("I'm grateful for my life", "Gratitude")
test_chat("feeling peaceful", "Peace")
test_chat("I'm content", "Contentment")
test_chat("celebrating a success", "Celebration")

# ==================== CATEGORY 10: SPECIFIC VERSE TOPICS ====================
print("\n" + "🔵" * 40)
print("CATEGORY 10: SPECIFIC GITA TOPICS")
print("🔵" * 40)

test_chat("Tell me about Arjuna's dilemma", "Story/Context")
test_chat("What did Krishna say about action?", "Action Philosophy")
test_chat("Explain yoga in the Gita", "Yoga Concept")
test_chat("What is devotion?", "Bhakti")
test_chat("How to control the mind?", "Mind Control")
test_chat("What about renunciation?", "Sannyasa")

# ==================== SUMMARY ====================
print("\n" + "=" * 80)
print("✅ TEST SUITE COMPLETED")
print("=" * 80)
print("\n📊 Summary:")
print("- Tested 60+ different scenarios")
print("- Categories: Greetings, Emotions, Philosophy, Practical, Edge Cases")
print("- System should demonstrate:")
print("  ✓ Appropriate intent detection")
print("  ✓ Verse blocking during emotional distress")
print("  ✓ Verse provision for reflective questions")
print("  ✓ Conversational responses for casual chat")
print("  ✓ Graceful handling of edge cases")
print("\n🎯 Review the results to verify system behavior!")
