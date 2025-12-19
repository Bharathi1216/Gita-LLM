import rdflib

# 1. Load your populated ontology
g = rdflib.Graph()
try:
    g.parse("bhagavad_gita_fixed.ttl", format="ttl")
    print("✅ Ontology loaded successfully!")
except Exception as e:
    print(f"❌ Error loading file: {e}")
    exit()

# 2. Define the User's Mood (Simulated input from LLM)
# Try changing this to "Confusion", "Fear", "Peace", or "Joy" to test different results
user_mood = "Anxiety" 

print(f"\n🔍 Searching for verses for mood: {user_mood}...\n")

# 3. The SPARQL Query
# This looks for verses that evoke the specific mood and gets the text + translation
query = f"""
PREFIX : <http://www.semanticweb.org/varshini/ontologies/2025/8/Bhagavad_Gita#>

SELECT ?verseId ?sanskrit ?english ?tamil WHERE {{
    ?verse a :Verse .
    ?verse :evokesEmotion :{user_mood} .
    
    ?verse :hasVerseId ?verseId .
    ?verse :hasSanskritVerseText ?sanskrit .
    ?verse :hasEnglishTranslation ?english .
    OPTIONAL {{ ?verse :hasTamilTranslation ?tamil }}
}}
LIMIT 3
"""

# 4. Execute and Print
results = g.query(query)

if len(results) == 0:
    print("No verses found for this mood. Check your spelling (Case Sensitive!)")
else:
    for row in results:
        print(f"📖 Verse: {row.verseId}")
        print(f"🕉️ Sanskrit: {row.sanskrit}")
        print(f"🌍 English: {row.english}")
        if row.tamil:
            print(f"🏹 Tamil: {row.tamil}")
        print("-" * 40)