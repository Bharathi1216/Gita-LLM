# Gita-LLM

Gita-LLM is an AI-powered spiritual guidance chatbot inspired by the teachings of the Bhagavad Gita. It combines a React frontend with a Flask backend, retrieval over Gita verses using ChromaDB, and LLM-based response generation (Ollama locally with Gemini fallback).

## Features

- Intent-aware chat experience with three response modes:
  - **Casual Chat** for greetings and simple conversation
  - **Emotional Support** for calming, grounding responses
  - **Reflective Guidance** for philosophical and practical insight
- Retrieval-augmented responses using a Bhagavad Gita verse collection in ChromaDB
- Local-first LLM inference via **Ollama** (`llama3.2:3b`) with optional **Gemini** fallback
- Verse metadata support (English, Sanskrit, Tamil)
- Flask REST API with CORS support
- React + Vite web interface

## Tech Stack

- **Frontend:** React, Vite, CSS
- **Backend:** Python, Flask, Flask-CORS
- **Vector DB:** ChromaDB (persistent storage)
- **LLM Providers:** Ollama, Google Gemini API (fallback)
- **Data:** Bhagavad Gita verse corpus and metadata

## Repository Structure

```text
Gita-LLM/
├── backend/
│   ├── ingest.py               # Builds/ingests verse embeddings into ChromaDB
│   └── gita_db/                # Persistent ChromaDB storage
├── gita_db/                    # Additional DB assets (if used)
├── src/
│   ├── App.jsx                 # Main frontend chat UI logic
│   ├── App.css                 # Frontend styles
│   └── main.jsx                # React entrypoint
├── main_bot.py                 # Flask API + intent routing + LLM orchestration
├── bhagavad_gita.ttl           # Bhagavad Gita knowledge data
├── index.html                  # Vite HTML template
├── package.json                # Frontend dependencies and scripts
└── vite.config.js              # Vite configuration
```

## Prerequisites

- **Node.js** 18+
- **Python** 3.9+
- (Optional) **Ollama** installed and running locally
- (Optional) **Google Gemini API key**

## Installation

### 1) Clone the repository

```bash
git clone https://github.com/Revanth03135/Gita-LLM.git
cd Gita-LLM
```

### 2) Frontend setup

```bash
npm install
```

### 3) Backend setup

Create and activate a virtual environment, then install backend dependencies:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install flask flask-cors chromadb python-dotenv requests
```

### 4) Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

> If `GEMINI_API_KEY` is not set, the app will still work with Ollama when available.

### 5) (Optional) Prepare vector database

If you need to (re)ingest verse data:

```bash
python backend/ingest.py
```

## Running the Project

### Start backend (Flask API)

```bash
python main_bot.py
```

The backend runs at:

- `http://127.0.0.1:5000`

### Start frontend (Vite)

In a new terminal:

```bash
npm run dev
```

The frontend typically runs at:

- `http://127.0.0.1:5173`

## API Endpoints

### `POST /api/survey`
Initializes a user profile and returns a `user_id`.

**Response (example):**

```json
{
  "user_id": "uuid-string"
}
```

### `POST /api/chat`
Sends a user message and gets a guided response.

**Request body:**

```json
{
  "user_id": "uuid-string",
  "message": "I feel confused about my purpose"
}
```

**Response body (example):**

```json
{
  "response": "Act with clarity and without attachment to outcomes.",
  "data": {
    "id": "2.47",
    "english": "You have a right to perform your prescribed duty...",
    "sanskrit": "...",
    "tamil": "..."
  }
}
```

## How It Works

1. User message is sent from React UI to Flask backend.
2. Backend classifies intent (`CASUAL_CHAT`, `EMOTIONAL_SUPPORT`, `REFLECTIVE_GUIDANCE`).
3. For reflective queries, relevant verse context is retrieved from ChromaDB.
4. Response is generated using Ollama; if unavailable, Gemini fallback is used.
5. API returns concise guidance and optional verse metadata.

## Notes

- The backend warms up Ollama on startup to reduce first-response latency.
- CORS is enabled to support local frontend-backend communication.
- ChromaDB is configured with persistent storage under `./backend/gita_db`.

## Future Improvements

- Add authentication and persistent user history
- Expand multilingual verse rendering
- Improve prompt safety and guardrails
- Add tests and CI workflows

## License

This project is currently unlicensed (`ISC` listed in `package.json`).
If you intend to open-source broadly, consider adding a dedicated `LICENSE` file.