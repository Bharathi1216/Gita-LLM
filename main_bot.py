# ==============================================================================
# [FLOWFORGE ERROR 4: Backend Dependency / Missing Module Import Error]
# To disable this error, comment out or remove the import below:
# ==============================================================================
import flowforge_audit_logger  # Will raise ModuleNotFoundError: No module named 'flowforge_audit_logger'

import os
import uuid
import random
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
CORS(app)

chroma_client = chromadb.PersistentClient(path="./backend/gita_db")
collection = chroma_client.get_collection(name="gita_verses")

USER_PROFILES = {}

INTENSE_WORDS = ["angry", "anger", "furious", "anxious", "anxiety", "panic", 
                 "stress", "stressed", "afraid", "fear", "scared"]

# LLM: Ollama (local) with Gemini fallback
def call_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": prompt, "stream": False,
                  "options": {"temperature": 0.7, "num_predict": 100}},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["response"].strip()
    except:
        pass
    return None

def call_gemini(prompt):
    if not GEMINI_API_KEY:
        return None
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=15
        )
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        pass
    return None

def call_llm(prompt):
    return call_ollama(prompt) or call_gemini(prompt)


# Intent classification: rule-based + LLM fallback
def detect_intent(text):
    text_lower = text.lower()
    
    if text_lower in ["hi", "hello", "hlo", "hey", "how are you", "what's up", "wassup"]:
        return "CASUAL_CHAT"
    
    if has_high_emotion(text):
        return "EMOTIONAL_SUPPORT"
    
    philosophical_terms = ["dharma", "karma", "yoga", "moksha", "atman", "brahman"]
    for term in philosophical_terms:
        if text_lower in [term, f"{term}?", f"what is {term}", f"explain {term}"]:
            return "REFLECTIVE_GUIDANCE"
    
    if text_lower.startswith(("explain ", "tell me about ", "what about ")):
        return "REFLECTIVE_GUIDANCE"
    
    reflective_keywords = ["why", "what is", "meaning", "purpose", "duty", "should i", 
                          "confused", "guidance", "verses", "verse", "how to"]
    if any(keyword in text_lower for keyword in reflective_keywords):
        return "REFLECTIVE_GUIDANCE"
    
    res = call_llm(f"""Classify intent: CASUAL_CHAT, EMOTIONAL_SUPPORT, or REFLECTIVE_GUIDANCE
User: "{text}"
Return one word only:""")
    
    if res and res.strip().upper() in ["CASUAL_CHAT", "EMOTIONAL_SUPPORT", "REFLECTIVE_GUIDANCE"]:
        return res.strip().upper()
    
    return "CASUAL_CHAT"

def has_high_emotion(text):
    return any(word in text.lower() for word in INTENSE_WORDS)

def should_show_verse(user_text, intent):
    return intent == "REFLECTIVE_GUIDANCE" and not has_high_emotion(user_text)


# API endpoints
@app.route("/api/survey", methods=["POST"])
def survey():
    user_id = str(uuid.uuid4())
    USER_PROFILES[user_id] = {"guidance_tone": "calm", "decision_style": "balanced"}
    return jsonify({"user_id": user_id})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_text = data.get("message", "").strip()
    user_id = data.get("user_id")

    if not user_text:
        return jsonify({"response": "Please share what is troubling you.", "data": None})

    intent = detect_intent(user_text)

    # CASUAL_CHAT
    if intent == "CASUAL_CHAT":
        if user_text.lower() in ["hi", "hello", "hlo", "hey"]:
            response = "I am here. Speak freely."
        elif "how are you" in user_text.lower():
            response = "I am well. How may I assist you today?"
        elif "who are you" in user_text.lower():
            response = "I am a guide inspired by the wisdom of the Gita. Share what troubles you."
        else:
            response = call_llm(f'You are a calm companion. User: "{user_text}"\nRespond warmly in under 25 words:')
            if not response:
                response = random.choice(["Tell me more.", "I am listening. What is on your mind?", "Continue. I am here."])
        
        return jsonify({"response": response, "data": None})

    # EMOTIONAL_SUPPORT
    elif intent == "EMOTIONAL_SUPPORT":
        response = call_llm(f'You are Krishna giving grounding support.\nUser: "{user_text}"\nCalm guidance under 30 words, no philosophy:')
        
        if not response:
            text_lower = user_text.lower()
            if "angry" in text_lower or "anger" in text_lower:
                response = "Pause. Anger clouds judgment. Breathe deeply. Act only when the mind is calm."
            elif "anxious" in text_lower or "anxiety" in text_lower:
                response = "Take a moment. Ground yourself. You cannot control everything, but you can steady your mind."
            elif "stress" in text_lower:
                response = "Step back. Release what you cannot control. Focus on your breath and present moment."
            else:
                response = "Pause for a moment. Let the emotion settle before choosing your next step."
        
        return jsonify({"response": response, "data": None})

    # REFLECTIVE_GUIDANCE
    elif intent == "REFLECTIVE_GUIDANCE":
        show_verse = should_show_verse(user_text, intent)
        verse_data = None
        verse_english = ""
        
        if show_verse:
            try:
                results = collection.query(query_texts=[user_text], n_results=1)
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
            except:
                pass
        
        prompt = f'You are Krishna. User: "{user_text}"\nGive ONE practical insight under 35 words. Do not quote verses directly.'
        if show_verse and verse_english:
            prompt += f'\nAlign with: "{verse_english}"'
        
        response = call_llm(prompt)
        
        if not response:
            response = "Reflect on this verse. Its wisdom speaks to your question." if verse_data else "Perform your duty without attachment to results. Act with a steady mind and clear intention."
        
        return jsonify({"response": response, "data": verse_data})

    return jsonify({"response": "Tell me more about what troubles you.", "data": None})


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
