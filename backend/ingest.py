import rdflib
import chromadb
from sentence_transformers import SentenceTransformer

# 1. Setup Vector DB
print("⚙️  Initializing Vector Database...")
chroma_client = chromadb.PersistentClient(path="./gita_db")
collection = chroma_client.get_or_create_collection(name="gita_verses")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2') # Small, fast model

# 2. Load Ontology
print("📖 Reading Ontology File...")
g = rdflib.Graph()
try:
    g.parse("bhagavad_gita.ttl", format="ttl")
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# 3. Extract Verses
print("🔍 Extracting Verses...")
query = """
PREFIX : <http://www.semanticweb.org/varshini/ontologies/2025/8/Bhagavad_Gita#>
SELECT ?verseId ?sanskrit ?english ?tamil WHERE {
    ?verse a :Verse .
    ?verse :hasVerseId ?verseId .
    ?verse :hasSanskritVerseText ?sanskrit .
    ?verse :hasEnglishTranslation ?english .
    OPTIONAL { ?verse :hasTamilTranslation ?tamil }
}
"""
results = g.query(query)

documents = []
metadatas = []
ids = []

count = 0
for row in results:
    verse_id = str(row.verseId)
    english_text = str(row.english)
    sanskrit_text = str(row.sanskrit)
    tamil_text = str(row.tamil) if row.tamil else "N/A"

    # We embed the English meaning so we can search against it
    documents.append(english_text)
    
    # We store the rest as data to display later
    metadatas.append({
        "verse_id": verse_id,
        "sanskrit": sanskrit_text,
        "tamil": tamil_text,
        "english": english_text
    })
    
    ids.append(verse_id)
    count += 1

# 4. Save to ChromaDB
print(f"💾 Saving {count} verses to Vector DB (this might take a moment)...")
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print("✅ SUCCESS! Knowledge Base Built.")