import re  # vital for the 'Isense' fix
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# Paste your actual key inside the quotes below
GEMINI_API_KEY = "AIzaSyCmrZNdv4Fm-qoP37aOZ9Oe0VB7DyFkIXU" 

# --- CONNECT TO DATABASE ---
chroma_client = chromadb.PersistentClient(path="./backend/gita_db") 
collection = chroma_client.get_collection(name="gita_verses")

# --- EMERGENCY BACKUPS ---
BACKUP_ANSWERS = {
    "anger": "I sense the fire within you. The Gita teaches that anger leads to delusion. Watch this emotion rise and fall like a wave, but do not let it drown your wisdom.",
    "fear": "Fear is born of attachment to the temporary. Remember, you are the eternal soul, not this fragile body. There is nothing in this world that can truly harm your spirit.",
    "worry": "Why do you worry without cause? What is yours today was someone else's yesterday and will be another's tomorrow. Do your duty and leave the rest to the divine.",
    "default": "I sense a disturbance in your mind. The Gita teaches us to be like the ocean—receiving all rivers of emotion but remaining undisturbed and deep."
}

def call_google_direct(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        if response.status_code != 200: 
            return None
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return None

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    print(f"\nUser: {user_input}")

    # STEP 1: Fetch Potential Verse
    verse_data = None
    verse_english = ""
    
    try:
        results = collection.query(query_texts=[user_input], n_results=1)
        if results['metadatas'] and results['metadatas'][0]:
            match = results['metadatas'][0][0]
            
            # Fix Tamil Typo
            if 'tamil' in match:
                match['tamil'] = match['tamil'].replace("கருஷ்ணர்", "கிருஷ்ணர்")
            
            verse_data = {
                "id": match['verse_id'],
                "sanskrit": match['sanskrit'],
                "english": match['english'],
                "tamil": match['tamil']
            }
            verse_english = match['english']
    except:
        pass

    # STEP 2: The "Intelligent Judge" Prompt
    # We explicitly tell Gemini that physical sickness is NOT the same as mental fear
    prompt = f"""
    Act as Krishna. 
    User Situation: "{user_input}"
    Retrieved Database Verse: "{verse_english}"
    
    INSTRUCTIONS:
    1. Analyze if the verse is TRULY relevant.
       - NOTE: "Fever/Sickness" (Physical) is NOT the same as "Fear/Terror" (Mental).
       - If user has fever and verse is about "Terror/Fear", mark as IRRELEVANT.
    
    2. IF RELEVANT: 
       - Explain the verse warmly.
       - Start explicitly with "I sense " (Ensure there is a space after 'sense').
       
    3. IF NOT RELEVANT:
       - Give general spiritual advice (e.g., "Endure the passing pain", "Focus on duty").
       - CRITICAL: End response with <HIDE_VERSE>.
    
    Keep response under 40 words. Warm and soothing tone.
    """
    
    ai_text = call_google_direct(prompt)
    
    # STEP 3: Fallback Logic
    if not ai_text:
        print("⚡ Using Emergency Backup")
        txt = user_input.lower()
        if "ang" in txt or "mad" in txt: ai_text = BACKUP_ANSWERS["anger"]
        elif "fear" in txt or "scar" in txt: ai_text = BACKUP_ANSWERS["fear"]
        elif "worr" in txt or "anx" in txt: ai_text = BACKUP_ANSWERS["worry"]
        else: ai_text = BACKUP_ANSWERS["default"]
    
    # STEP 4: BUG FIX - The "Isense" cleanup
    # This regex looks for 'Isense' at the start and forces it to 'I sense '
    if ai_text:
        ai_text = re.sub(r'^Isense\s?', "I sense ", ai_text, flags=re.IGNORECASE)

    # STEP 5: Process the <HIDE_VERSE> Tag
    if ai_text and "<HIDE_VERSE>" in ai_text:
        ai_text = ai_text.replace("<HIDE_VERSE>", "").strip()
        verse_data = None # ❌ HIDE THE CARD

    return jsonify({
        "response": ai_text,
        "data": verse_data 
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)