import google.generativeai as genai
import os

# ⚠️ PASTE YOUR KEY HERE
GEMINI_API_KEY = "AIzaSyCmrZNdv4Fm-qoP37aOZ9Oe0VB7DyFkIXU"
genai.configure(api_key=GEMINI_API_KEY)

print("🔍 Checking available models for this API Key...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")