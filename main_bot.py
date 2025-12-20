import os
import uuid
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ================= APP =================
app = Flask(__name__)
CORS(app)

# ================= DB =================
chroma_client = chromadb.PersistentClient(path="./backend/gita_db")
collection = chroma_client.get_collection(name="gita_verses")

# ================= USER STORE =================
USER_PROFILES = {}

# ================= OLLAMA LLM (LOCAL) =================
def call_ollama(prompt):
    """Call local Ollama LLM - fast, free, private"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100  # Limit tokens for faster response
                }
            },
            timeout=60  # Increased timeout for first request (model loading)
        )
        if response.status_code == 200:
            result = response.json()["response"].strip()
            print(f"✅ Ollama response: {result[:50]}...")
            return result
        else:
            print(f"⚠️ Ollama Error: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print("⚠️ Ollama timeout - model may be loading, try again")
        return None
    except Exception as e:
        print(f"⚠️ Ollama not available: {str(e)}")
        return None


# ================= GEMINI CALL (FALLBACK) =================
def call_gemini(prompt):
    """Fallback to Gemini API if Ollama fails"""
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY not found")
        return None
    
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code != 200:
            print(f"⚠️ Gemini API Error: {r.status_code}")
            return None
        result = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"✅ Gemini response: {result[:50]}...")
        return result
    except Exception as e:
        print(f"⚠️ Gemini Exception: {str(e)}")
        return None


# ================= SMART LLM CALL (TRIES OLLAMA FIRST) =================
def call_llm(prompt):
    """Smart LLM caller: Ollama → Gemini → Fallback"""
    # Try Ollama first (local, fast, free)
    result = call_ollama(prompt)
    if result:
        return result
    
    # Fallback to Gemini if Ollama unavailable
    result = call_gemini(prompt)
    if result:
        return result
    
    # If both fail, return None (will use rule-based fallbacks)
    print("❌ All LLM backends unavailable")
    return None


# ================= INTENT CLASSIFICATION =================
def detect_intent(text):
    # Fallback: rule-based intent detection
    text_lower = text.lower()
    
    # Check for greetings
    if text_lower in ["hi", "hello", "hlo", "hey", "how are you", "what's up", "wassup"]:
        return "CASUAL_CHAT"
    
    # Check for emotional distress
    if has_high_emotion(text):
        return "EMOTIONAL_SUPPORT"
    
    # Check for single-word philosophical terms (strong indicators)
    philosophical_terms = ["dharma", "karma", "yoga", "moksha", "atman", "brahman", 
                          "samsara", "nirvana", "maya", "bhakti", "jnana"]
    # Match whole words ending with ? or standalone
    for term in philosophical_terms:
        if text_lower in [term, f"{term}?", f"what is {term}", f"explain {term}"]:
            return "REFLECTIVE_GUIDANCE"
    
    # Check for "explain/tell me about X" pattern
    if text_lower.startswith(("explain ", "tell me about ", "what about ")):
        return "REFLECTIVE_GUIDANCE"
    
    # Check for reflective questions
    reflective_keywords = ["why", "what is", "meaning", "purpose", "duty", "should i", 
                          "confused", "guidance", "help me understand", "verses", "verse",
                          "how to", "how do i"]
    if any(keyword in text_lower for keyword in reflective_keywords):
        return "REFLECTIVE_GUIDANCE"
    
    # Try LLM if available (Ollama or Gemini)
    prompt = f"""
Classify the user's intent into ONE category only:
CASUAL_CHAT, EMOTIONAL_SUPPORT, REFLECTIVE_GUIDANCE

CASUAL_CHAT: greetings, small talk, acknowledgements
EMOTIONAL_SUPPORT: expressing distress, anxiety, anger, fear
REFLECTIVE_GUIDANCE: seeking wisdom, meaning, purpose, ethical guidance

User message:
"{text}"

Return ONLY one word: CASUAL_CHAT, EMOTIONAL_SUPPORT, or REFLECTIVE_GUIDANCE
"""
    res = call_llm(prompt)
    if res:
        res = res.strip().upper()
        if res in ["CASUAL_CHAT", "EMOTIONAL_SUPPORT", "REFLECTIVE_GUIDANCE"]:
            print(f"✅ Intent detected: {res}")
            return res
        else:
            print(f"⚠️ Unexpected intent response: {res}")
    else:
        print("❌ Intent detection failed - using fallback")
    
    # Default to casual if uncertain
    return "CASUAL_CHAT"


# ================= HIGH EMOTION DETECTION (RULE-BASED) =================
INTENSE_WORDS = [
    "angry", "anger", "furious",
    "anxious", "anxiety", "panic",
    "stress", "stressed",
    "afraid", "fear", "scared"
]

def has_high_emotion(text):
    t = text.lower()
    return any(word in t for word in INTENSE_WORDS)


# ================= VERSE GATE (INTENT-BASED) =================
def should_show_verse(user_text, intent):
    # Only show verse for reflective guidance
    if intent != "REFLECTIVE_GUIDANCE":
        return False
    
    # Additional safety: block if high emotion detected
    if has_high_emotion(user_text):
        return False
    
    return True


# ================= SURVEY (SESSION CREATION) =================
@app.route("/api/survey", methods=["POST"])
def survey():
    user_id = str(uuid.uuid4())
    USER_PROFILES[user_id] = {
        "guidance_tone": "calm",
        "decision_style": "balanced"
    }
    return jsonify({"user_id": user_id})


# ================= CHAT =================
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_text = data.get("message", "").strip()
    user_id = data.get("user_id")

    # ---------- Empty ----------
    if not user_text:
        return jsonify({
            "response": "Please share what is troubling you.",
            "data": None
        })

    # ---------- STEP 1: Detect Intent ----------
    intent = detect_intent(user_text)

    # ---------- STEP 2: Handle by Intent ----------
    
    # CASUAL_CHAT: Friendly, conversational
    if intent == "CASUAL_CHAT":
        if user_text.lower() in ["hi", "hello", "hlo", "hey"]:
            response = "I am here. Speak freely."
        elif "how are you" in user_text.lower():
            response = "I am well. How may I assist you today?"
        elif "who are you" in user_text.lower():
            response = "I am a guide inspired by the wisdom of the Gita. Share what troubles you."
        else:
            prompt = f"""
You are a calm, wise companion having a natural conversation.

User: "{user_text}"

Respond naturally and warmly in under 25 words. Be conversational, not preachy.
"""
            response = call_llm(prompt)
            if not response:
                # Fallback responses
                fallbacks = [
                    "Tell me more.",
                    "I am listening. What is on your mind?",
                    "Continue. I am here."
                ]
                import random
                response = random.choice(fallbacks)
        
        return jsonify({
            "response": response,
            "data": None
        })

    # EMOTIONAL_SUPPORT: Grounding, calming
    elif intent == "EMOTIONAL_SUPPORT":
        prompt = f"""
You are Krishna offering grounding support to someone in distress.

User: "{user_text}"

Give calm, grounding guidance. Do NOT preach. Keep under 30 words.
Focus on steadying the mind, not on philosophy.
"""
        response = call_llm(prompt)
        
        if not response:
            # Emotion-specific fallbacks
            text_lower = user_text.lower()
            if "angry" in text_lower or "anger" in text_lower:
                response = "Pause. Anger clouds judgment. Breathe deeply. Act only when the mind is calm."
            elif "anxious" in text_lower or "anxiety" in text_lower:
                response = "Take a moment. Ground yourself. You cannot control everything, but you can steady your mind."
            elif "stress" in text_lower:
                response = "Step back. Release what you cannot control. Focus on your breath and present moment."
            else:
                response = "Pause for a moment. Let the emotion settle before choosing your next step."
        
        return jsonify({
            "response": response,
            "data": None
        })

    # REFLECTIVE_GUIDANCE: Wisdom + optional verse
    elif intent == "REFLECTIVE_GUIDANCE":
        # Check if verse should be shown
        show_verse = should_show_verse(user_text, intent)
        
        verse_data = None
        verse_english = ""
        
        # Verse retrieval
        if show_verse:
            try:
                results = collection.query(
                    query_texts=[user_text],
                    n_results=1
                )
                meta = results.get("metadatas", [[]])[0]
                if meta:
                    m = meta[0]
                    verse_data = {
                        "id": m["verse_id"],
                        "english": m["english"],
                        "sanskrit": m.get("sanskrit", ""),
                        "tamil": m.get("tamil", "")
                    }
                    verse_english = m["english"]
            except Exception:
                verse_data = None
        
        # Generate guidance
        prompt = f"""
You are Krishna giving calm, practical guidance.

User question:
"{user_text}"

Instructions:
- Speak naturally and clearly.
- Give ONE practical insight.
- Keep under 35 words.
- Do NOT say "I sense" or "I understand".
- Do NOT quote verses directly.
"""
        
        if show_verse and verse_english:
            prompt += f'\n\nAlign your guidance with this wisdom:\n"{verse_english}"'
        
        response = call_llm(prompt)
        
        if not response:
            # Wisdom fallbacks
            if verse_data:
                response = "Reflect on this verse. Its wisdom speaks to your question."
            else:
                response = (
                    "Perform your duty without attachment to results. "
                    "Act with a steady mind and clear intention."
                )
        
        return jsonify({
            "response": response,
            "data": verse_data
        })

    # Fallback
    return jsonify({
        "response": "Tell me more about what troubles you.",
        "data": None
    })


# ================= WARMUP OLLAMA =================
def warmup_ollama():
    """Preload Ollama model to avoid first-request timeout"""
    print("🔥 Warming up Ollama model...")
    try:
        result = call_ollama("Hi")
        if result:
            print("✅ Ollama ready!")
        else:
            print("⚠️ Ollama warmup failed - will use fallbacks")
    except Exception:
        print("⚠️ Ollama not available - will use fallbacks")


# ================= RUN =================
if __name__ == "__main__":
    # Warmup model before starting server
    warmup_ollama()
    
    print("\n🚀 Starting GITA-AI server...")
    app.run(debug=True, port=5000, use_reloader=False)  # use_reloader=False prevents double warmup
